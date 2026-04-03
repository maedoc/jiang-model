"""
Delay Differential Equation (DDE) model for geopolitical resource dynamics using JAX.

Three regions: Middle East (producer), Asia (consumer), North America (alternative supplier).
State variables per region: Oil supply O, Fertilizer supply F, Political stability S (0-1).
Time delays model spatial interactions: τ = base shipping delay + choke point disruption.
Choke point (Strait of Hormuz) modulates delay: τ = 30 days + 7 days × Hormuz_disruption.
Hormuz_disruption(t) = 0.5·US_navy(t) + 0.8·Iran_military(t).
DDE form: dx_i/dt = F_i(x_i) + sum_j G_ij(x_i, x_j(t - τ_ij)).

Implementation uses JAX for performance, with jax.lax.scan for time integration.
Simplified Euler method with history lookup for fixed delays.
"""

import jax
import jax.numpy as jnp
from jax import vmap
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# Disable JAX GPU/TPU for compatibility (optional)
jax.config.update("jax_platform_name", "cpu")

# Constants
N_REGIONS = 3
STATE_DIM = 3  # O, F, S per region
DT = 1.0  # time step (days)
TOTAL_DAYS = 365
N_STEPS = int(TOTAL_DAYS / DT)

# Region indices
ME = 0  # Middle East
AS = 1  # Asia
NA = 2  # North America


def region_name(idx: int) -> str:
    return ["Middle East", "Asia", "North America"][idx]


def base_delay() -> float:
    """Base shipping delay in days."""
    return 30.0


def choke_point_multiplier() -> float:
    """Additional days per unit disruption."""
    return 7.0


def compute_hormuz_disruption(t: float, disruption_day: float = 100.0) -> float:
    """
    Compute Hormuz disruption factor as a function of time.
    disruption_day: day when disruption event occurs.
    Returns disruption factor between 0 (normal) and 1 (max disruption).
    """
    # Simplified: no disruption before day 100, then step increase
    # Use jnp.where for JAX compatibility
    ramp = jnp.minimum(1.0, (t - disruption_day) / 10.0)
    return jnp.where(t < disruption_day, 0.0, 0.8 * ramp)


def compute_delay(disruption: float) -> float:
    """Compute delay in days given disruption factor."""
    return base_delay() + choke_point_multiplier() * disruption


def local_dynamics(state: jnp.ndarray, region_idx: int, params: Dict) -> jnp.ndarray:
    """
    Local dynamics F_i(x_i) for region i.
    state: array of length STATE_DIM (O, F, S)
    Returns derivative d(state)/dt.
    """
    O, F, S = state
    # Parameters
    oil_production = params["oil_production"][region_idx]
    oil_consumption = params["oil_consumption"][region_idx]
    fertilizer_production = params["fertilizer_production"][region_idx]
    fertilizer_consumption = params["fertilizer_consumption"][region_idx]
    stability_decay = params["stability_decay"][region_idx]
    stability_gain = params["stability_gain"][region_idx]

    # Oil: production minus consumption, modulated by stability
    dO = oil_production * S - oil_consumption
    # Fertilizer: similar
    dF = fertilizer_production * S - fertilizer_consumption
    # Political stability: decays naturally, gains from resource abundance
    resource_abundance = jnp.tanh(0.01 * (O + F))
    dS = -stability_decay * S + stability_gain * resource_abundance * (1 - S)

    return jnp.array([dO, dF, dS])


def coupling_term(
    state_i: jnp.ndarray,
    state_j_delayed: jnp.ndarray,
    region_i: int,
    region_j: int,
    params: Dict,
) -> jnp.ndarray:
    """
    Coupling term G_ij(x_i, x_j(t - τ)).
    Models trade flow from region j to i.
    """
    # Trade coefficients: oil and fertilizer flow from exporter to importer
    oil_trade = params["oil_trade"][region_i, region_j]
    fertilizer_trade = params["fertilizer_trade"][region_i, region_j]
    # Stability influence
    stability_coupling = params["stability_coupling"][region_i, region_j]

    O_j, F_j, S_j = state_j_delayed
    O_i, F_i, S_i = state_i

    # Oil trade: proportional to exporter's oil and importer's deficit
    oil_deficit = jnp.maximum(0, params["oil_consumption"][region_i] - O_i)
    dO = oil_trade * O_j * oil_deficit * S_j  # exporter stability matters

    # Fertilizer trade similar
    fertilizer_deficit = jnp.maximum(
        0, params["fertilizer_consumption"][region_i] - F_i
    )
    dF = fertilizer_trade * F_j * fertilizer_deficit * S_j

    # Stability coupling: influenced by partner's stability
    dS = stability_coupling * (S_j - S_i) * S_i * (1 - S_i)

    return jnp.array([dO, dF, dS])


def dde_system(
    state_flat: jnp.ndarray,
    t: float,
    history: jnp.ndarray,
    delay_steps: int,
    params: Dict,
) -> jnp.ndarray:
    """
    Compute derivative of the full system.
    state_flat: flattened array of shape (N_REGIONS * STATE_DIM,)
    t: current time (days)
    history: array of shape (delay_steps, N_REGIONS * STATE_DIM) containing past states
    delay_steps: number of steps corresponding to current delay
    Returns derivative flattened array.
    """
    # Reshape to (N_REGIONS, STATE_DIM)
    state = state_flat.reshape(N_REGIONS, STATE_DIM)

    # Compute current Hormuz disruption and delay
    disruption = compute_hormuz_disruption(t)
    delay_days = compute_delay(disruption)
    # Convert delay to steps (rounded down)
    delay_steps_float = delay_days / DT
    delay_steps_int = jnp.floor(delay_steps_float).astype(jnp.int32)
    current_delay_steps = jnp.minimum(delay_steps, delay_steps_int)

    # Retrieve delayed states from history
    delayed_state_flat = history[-current_delay_steps, :]
    delayed_state = delayed_state_flat.reshape(N_REGIONS, STATE_DIM)

    derivative = jnp.zeros_like(state)

    # For each region, compute local dynamics plus coupling from all others
    for i in range(N_REGIONS):
        local = local_dynamics(state[i], i, params)
        derivative = derivative.at[i].add(local)

        for j in range(N_REGIONS):
            if i == j:
                continue
            coupling = coupling_term(state[i], delayed_state[j], i, j, params)
            derivative = derivative.at[i].add(coupling)

    return derivative.flatten()


def euler_step(
    state_flat: jnp.ndarray,
    t: float,
    history: jnp.ndarray,
    delay_steps: int,
    params: Dict,
) -> jnp.ndarray:
    """One Euler step."""
    deriv = dde_system(state_flat, t, history, delay_steps, params)
    return state_flat + DT * deriv


def simulate(
    params: Dict, initial_state: jnp.ndarray
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Run simulation using jax.lax.scan.
    Returns:
        states: array of shape (N_STEPS, N_REGIONS * STATE_DIM)
        times: array of shape (N_STEPS,)
    """
    # Maximum possible delay steps (for history buffer size)
    max_delay_days = compute_delay(1.0)  # maximum disruption = 1
    max_delay_steps = int(max_delay_days / DT) + 10  # safety margin

    # Initialize history buffer as a rolling window
    # We'll store the last max_delay_steps states
    history_shape = (max_delay_steps, N_REGIONS * STATE_DIM)
    # Fill history with initial state for t < 0
    history = jnp.tile(initial_state, (max_delay_steps, 1))

    def step(carry, t):
        state_flat, history = carry
        # Update history: shift and add current state
        history = jnp.roll(history, shift=-1, axis=0)
        history = history.at[-1].set(state_flat)

        # Compute next state
        next_state = euler_step(state_flat, t, history, max_delay_steps, params)

        return (next_state, history), next_state

    # Times array
    times = jnp.arange(0, TOTAL_DAYS, DT)

    # Run scan
    (final_state, final_history), states = jax.lax.scan(
        step, (initial_state, history), times
    )

    # Include initial state at time 0
    states = jnp.vstack([initial_state, states[:-1]])

    return states, times


def default_parameters() -> Dict:
    """Return default parameter set."""
    params = {}

    # Oil production/consumption per region (units per day)
    params["oil_production"] = jnp.array(
        [100.0, 20.0, 60.0]
    )  # ME high, AS low, NA medium
    params["oil_consumption"] = jnp.array(
        [30.0, 80.0, 50.0]
    )  # ME low, AS high, NA medium

    # Fertilizer production/consumption
    params["fertilizer_production"] = jnp.array([40.0, 10.0, 30.0])
    params["fertilizer_consumption"] = jnp.array([10.0, 50.0, 20.0])

    # Stability dynamics
    params["stability_decay"] = jnp.array([0.01, 0.02, 0.01])
    params["stability_gain"] = jnp.array([0.05, 0.03, 0.04])

    # Trade matrices (i, j): flow from j to i
    oil_trade = jnp.zeros((N_REGIONS, N_REGIONS))
    # ME exports to Asia and NA
    oil_trade = oil_trade.at[AS, ME].set(0.02)  # Asia imports from ME
    oil_trade = oil_trade.at[NA, ME].set(0.01)  # NA imports from ME
    # NA exports to Asia (alternative supply)
    oil_trade = oil_trade.at[AS, NA].set(0.015)
    params["oil_trade"] = oil_trade

    fertilizer_trade = jnp.zeros((N_REGIONS, N_REGIONS))
    fertilizer_trade = fertilizer_trade.at[AS, ME].set(0.03)
    fertilizer_trade = fertilizer_trade.at[NA, ME].set(0.01)
    params["fertilizer_trade"] = fertilizer_trade

    # Stability coupling (how region i's stability is influenced by region j)
    stability_coupling = jnp.zeros((N_REGIONS, N_REGIONS))
    # ME stability influences Asia and NA
    stability_coupling = stability_coupling.at[AS, ME].set(0.01)
    stability_coupling = stability_coupling.at[NA, ME].set(0.005)
    params["stability_coupling"] = stability_coupling

    return params


def main():
    """Run simulation and plot results."""
    print("Setting up DDE model for geopolitical resource dynamics...")

    params = default_parameters()

    # Initial conditions: ME oil high, Asia oil low, NA oil medium
    # Format: [O_ME, F_ME, S_ME, O_AS, F_AS, S_AS, O_NA, F_NA, S_NA]
    initial_state = jnp.array(
        [
            200.0,
            100.0,
            0.8,  # ME
            50.0,
            30.0,
            0.6,  # Asia
            150.0,
            80.0,
            0.7,  # NA
        ]
    )

    print("Running simulation...")
    states, times = simulate(params, initial_state)

    # Reshape states for easy indexing
    states_reshaped = states.reshape(-1, N_REGIONS, STATE_DIM)

    # Plot oil levels over time
    plt.figure(figsize=(12, 8))

    # Oil subplot
    plt.subplot(3, 1, 1)
    for i in range(N_REGIONS):
        plt.plot(times, states_reshaped[:, i, 0], label=region_name(i), linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5, label="Disruption event")
    plt.ylabel("Oil supply")
    plt.title("Geopolitical Resource Dynamics - Oil Supply Over Time")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Fertilizer subplot
    plt.subplot(3, 1, 2)
    for i in range(N_REGIONS):
        plt.plot(times, states_reshaped[:, i, 1], label=region_name(i), linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Fertilizer supply")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Political stability subplot
    plt.subplot(3, 1, 3)
    for i in range(N_REGIONS):
        plt.plot(times, states_reshaped[:, i, 2], label=region_name(i), linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Political stability (0-1)")
    plt.xlabel("Time (days)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("simulation_results.png", dpi=150)
    print("Plot saved as simulation_results.png")

    # Also plot Hormuz disruption and delay over time
    plt.figure(figsize=(10, 6))

    # Vectorized computation of disruptions and delays
    disruptions = vmap(compute_hormuz_disruption)(times)
    delays = compute_delay(disruptions)  # compute_delay is elementwise

    plt.subplot(2, 1, 1)
    plt.plot(times, disruptions, "b-", linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Hormuz disruption factor")
    plt.title("Choke Point Dynamics")
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(times, delays, "g-", linewidth=2)
    plt.axvline(x=100, color="red", linestyle="--", alpha=0.5)
    plt.ylabel("Shipping delay (days)")
    plt.xlabel("Time (days)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("choke_point_dynamics.png", dpi=150)
    print("Plot saved as choke_point_dynamics.png")

    # Print summary statistics
    print("\nSimulation completed.")
    print(f"Final oil levels:")
    for i in range(N_REGIONS):
        final_oil = states_reshaped[-1, i, 0]
        print(f"  {region_name(i)}: {final_oil:.1f}")

    print(f"\nFinal political stability:")
    for i in range(N_REGIONS):
        final_stab = states_reshaped[-1, i, 2]
        print(f"  {region_name(i)}: {final_stab:.3f}")


if __name__ == "__main__":
    main()
