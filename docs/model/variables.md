# Regions \u0026 State Variables

## Regions (12)

| Index | Region | ISO3 mapping notes |
|-------|--------|-------------------|
| 0 | North America | USA, CAN, MEX |
| 1 | Europe | EU + UK, Norway, Switzerland |
| 2 | Russia | |
| 3 | Middle East | GCC, Iran, Iraq, Turkey, Egypt |
| 4 | China | Including Taiwan, HK, Macau |
| 5 | India | |
| 6 | Japan | |
| 7 | Southeast Asia | ASEAN members |
| 8 | Australia/New Zealand | |
| 9 | Africa (sub-Saharan) | |
| 10 | South America | |
| 11 | Central Asia/Caucasus | |

## State variables per region (15)

| Symbol | Physical meaning | Transform | Units |
|--------|---------------|-----------|-------|
| $O_i$ | Oil stock | Log: $L = \\ln(1 + x)$ | Model units (~kb/d equivalent) |
| $F_i$ | Fertilizer stock | Log: $L = \\ln(1 + x)$ | Model units |
| $W_i$ | Water stock | Log: $L = \\ln(1 + x)$ | Model units |
| $M_i$ | Military expenditure | Log: $L = \\ln(1 + x)$ | Model units |
| $S_i$ | Political stability | Logit: $\\eta = \\ln(p / (1-p))$ | Dimensionless [0, 1] |
| $I_i$ | Inequality (Gini) | Logit: $\\eta = \\ln(p / (1-p))$ | Dimensionless [0, 1] |
| $D_i$ | Sovereign debt / GDP | Log: $L = \\ln(1 + x)$ | Ratio |
| $P_i^o$ | Oil price | Log: $L = \\ln(1 + x)$ | Normalized index |
| $P_i^f$ | Fertilizer price | Log: $L = \\ln(1 + x)$ | Normalized index |
| $P_i^w$ | Water price | Log: $L = \\ln(1 + x)$ | Normalized index |
| $\\pi_i$ | Inflation rate | None | Annual rate |
| $r_i$ | Interest rate | None | Annual rate |
| $E_i$ | Exchange rate (local per USD) | Log: $L = \\ln(1 + x)$ | Ratio |
| $Y_i$ | Bond yield | None | Annual rate |
| $\\bar{E}_i$ | 30-day moving average exchange rate | Log: $L = \\ln(1 + x)$ | Ratio |

**Total state dimension:** $12 \\times 15 = 180$ ODEs.

## Transform conventions

### Log transform (positive variables)

$$L = \\ln(1 + x), \\quad \\frac{dL}{dt} = \\frac{\\dot{x}}{1 + x}$$

Applied to: $O, F, W, M, D, P^o, P^f, P^w, E, \\bar{E}$

### Logit transform (bounded variables)

$$\\eta = \\ln\\bigl(\\frac{p}{1-p}\\bigr), \\quad \\frac{d\\eta}{dt} = \\frac{\\dot{p}}{p(1-p)}$$

Applied to: $S, I$

### Untransformed

$\\pi, r, Y$ (rates already in natural units)

## Trajectory access

After simulation, variables are accessed via named properties:

```python
traj = model.simulate(t_span=(0, 365))
traj.oil_stock[region_idx, :]      # shape (12, T)
traj.stability[region_idx, :]       # shape (12, T)
traj.oil_price[region_idx, :]       # shape (12, T)
```

The `Trajectory` object handles inverse transforms automatically when plotting or summarizing.
