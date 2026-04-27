# Nonlinear Thresholds

All thresholds use the smooth sigmoid:

$$\\sigma(x; k, x_0) = \\frac{1}{1 + e^{-k(x-x_0)}}$$

This avoids discontinuous jumps and preserves differentiability for the ODE solver.

## Debt crisis

| Attribute | Value |
|-----------|-------|
| **Trigger** | $D_i > 1.0$ (debt/GDP > 100%) |
| **Sharpness** | $k = 10$ |
| **Effect on military** | Suppresses growth: $\\gamma_{md} \\cdot C_i^{\\text{debt}} \\cdot M_i$ |
| **Effect on interest rate** | Adds risk premium: $+0.02 \\cdot C_i^{\\text{debt}}$ |

The debt crisis sigmoid modulates military expenditure growth and the Taylor-rule risk premium. At $D_i = 1.0$, the effect is half-maximal; by $D_i = 1.3$, it is near-saturated.

## Currency crisis

| Attribute | Value |
|-----------|-------|
| **Trigger** | 30-day depreciation > 20% ($\\bar{E}_i < 0.8 E_i$) |
| **Sharpness** | $k = 20$ |
| **Effect** | Capital flight: $+0.05 \\cdot C_i^{\\text{currency}} \\cdot E_i$ |

The exchange rate moving average $\\bar{E}_i$ smooths day-to-day noise. A sustained 20% drop over 30 days triggers the capital-flight term in the exchange-rate ODE.

## Social unrest

| Attribute | Value |
|-----------|-------|
| **Trigger** | $I_i > 0.6$ AND $\\pi_i > 0.1$ |
| **Sharpness** | $k_{\\text{ineq}} = 10$, $k_{\\text{inf}} = 20$ |
| **Effect** | Reduces stability gain: $-\\gamma_u \\cdot U_i \\cdot S_i$ |

The unrest term $U_i$ is the product of two sigmoids:

$$U_i = \\sigma(I_i - 0.6;\\, k\\!=\\!10) \\cdot \\sigma(\\pi_i - 0.1;\\, k\\!=\\!20)$$

Both conditions must be met simultaneously for full effect.

## Water scarcity

| Attribute | Value |
|-----------|-------|
| **Trigger** | $W_i < 0.1 W_i^0$ (stock below 10% of initial) |
| **Sharpness** | $k = 0.1$ (very gradual) |
| **Effect** | Water price spike: $\\dot{P}_i^w \\mathrel{+}= 0.1 \\cdot C_i^{\\text{scarcity}}$ |

The low sharpness ($k=0.1$) means the price effect ramps slowly as stocks decline, rather than jumping discontinuously at the 10% boundary.

## Threshold summary table

| Crisis | Trigger variable | Threshold | Sharpness $k$ | Effect variable | Effect magnitude |
|--------|-----------------|-----------|--------------|-----------------|------------------|
| Debt crisis | $D_i$ | 1.0 | 10 | Military growth, interest rate | $\\gamma_{md}=0.1$, $+0.02$ premium |
| Currency crisis | $E_i / \\bar{E}_i$ | 0.8 (20% drop) | 20 | Exchange rate derivative | $+0.05 \\cdot C^{\\text{currency}} \\cdot E_i$ |
| Social unrest | $I_i$, $\\pi_i$ | 0.6, 0.1 | 10, 20 | Stability derivative | $-\\gamma_u \\cdot U_i \\cdot S_i$ |
| Water scarcity | $W_i / W_i^0$ | 0.1 | 0.1 | Water price derivative | $+0.1 \\cdot C^{\\text{scarcity}}$ |
