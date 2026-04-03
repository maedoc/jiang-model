#!/usr/bin/env python3
"""
Quick verification of numba acceleration.
"""

import sys

sys.path.insert(0, ".")

import numpy as np
from ode_model_extended import ExtendedODEModel, load_parameters

try:
    from ode_model_extended_numba import ExtendedODEModelNumba, system_numba, HAS_NUMBA
except ImportError as e:
    print(f"Import error: {e}")
    HAS_NUMBA = False


def main():
    params = load_parameters("real_params.json")
    original = ExtendedODEModel(params)
    n = original.n_regions
    n_vars = original.n_vars_per_region
    dim = n * n_vars

    print(f"Regions: {n}, variables per region: {n_vars}, total ODEs: {dim}")

    # Random state near zero
    np.random.seed(42)
    y = np.random.randn(dim) * 0.1
    t = 0.0

    dydt_original = original.system(t, y)
    print("Original system computed.")

    if HAS_NUMBA:
        numba = ExtendedODEModelNumba(params)
        dydt_numba = numba.system(t, y)
        diff = np.abs(dydt_original - dydt_numba)
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)
        print(f"Max difference: {max_diff:.2e}")
        print(f"Mean difference: {mean_diff:.2e}")
        if max_diff < 1e-10:
            print("SUCCESS: Numba output matches original within tolerance.")
        else:
            print("WARNING: Differences larger than expected.")
            # Print first few differences
            for i in range(min(10, len(diff))):
                print(f"  {i}: {diff[i]:.2e}")
    else:
        print("Numba not available.")

    # Also test direct system_numba
    if HAS_NUMBA:
        dydt_direct = system_numba(
            t,
            y,
            params["oil_production"],
            params["oil_consumption"],
            params["fertilizer_production"],
            params["fertilizer_consumption"],
            params["water_availability"],
            params["water_consumption"],
            params["stability_decay"],
            params["stability_gain"],
            params["oil_trade_flow"],
            params["fertilizer_trade_flow"],
            params["water_trade_flow"],
            params["stability_coupling"],
            params["capital_flow"],
            params["financial_coupling"],
            params["debt_to_gdp"],
            n,
            n_vars,
        )
        diff2 = np.abs(dydt_original - dydt_direct)
        print(f"Direct numba max diff: {np.max(diff2):.2e}")

    # Performance test (crude)
    if HAS_NUMBA:
        import time

        repeats = 1000
        # Warm up
        for _ in range(10):
            original.system(t, y)
            numba.system(t, y)

        start = time.perf_counter()
        for _ in range(repeats):
            original.system(t, y)
        elapsed_original = time.perf_counter() - start

        start = time.perf_counter()
        for _ in range(repeats):
            numba.system(t, y)
        elapsed_numba = time.perf_counter() - start

        print(f"\nPerformance (1000 evaluations):")
        print(
            f"  Original: {elapsed_original:.4f} s ({elapsed_original / repeats * 1e6:.2f} µs per eval)"
        )
        print(
            f"  Numba:    {elapsed_numba:.4f} s ({elapsed_numba / repeats * 1e6:.2f} µs per eval)"
        )
        print(f"  Speedup:  {elapsed_original / elapsed_numba:.2f}x")


if __name__ == "__main__":
    main()
