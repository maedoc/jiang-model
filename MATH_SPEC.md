# Mathematical Specification

## 1. Notation

| Symbol | Meaning |
|--------|---------|
| $i, j$ | Region indices ($1 \le i,j \le 12$) |
| $t$ | Time (days) |
| $S_i$ | Political stability $\in [0,1]$ |
| $O_i, F_i, W_i$ | Oil, fertilizer, water stocks |
| $M_i$ | Military expenditure |
| $I_i$ | Inequality (Gini) $\in [0,1]$ |
| $D_i$ | Sovereign debt / GDP ratio |
| $P_i^o, P_i^f, P_i^w$ | Oil, fertilizer, water prices |
| $\pi_i$ | Inflation rate |
| $r_i$ | Interest rate |
| $E_i$ | Exchange rate (local per USD) |
| $Y_i$ | Bond yield |
| $\bar{E}_i$ | 30-day moving average of exchange rate |

Total state dimension: $12 \times 15 = 180$ ODEs.

## 2. Transformations

Positive variables are log-transformed: $L = \ln(1 + x)$, and bounded variables use the logit transform: $\eta = \ln\bigl(\frac{p}{1-p}\bigr)$.

The ODE system computes derivatives $\dot{x}_i$ in physical units, then converts:

$$\frac{dL}{dt} = \frac{\dot{x}}{1 + x}, \qquad \frac{d\eta}{dt} = \frac{\dot{p}}{p(1 - p)}$$

**Log-transformed variables**: $O, F, W, M, D, P^o, P^f, P^w, E, \bar{E}$

**Logit-transformed variables**: $S, I$

**Untransformed**: $\pi, r, Y$

## 3. Intra-Region Dynamics

### 3.1 Resource Stocks

Production is modulated by stability with a baseline floor:

$$\dot{O}_i = \underbrace{P_i^{\text{oil}} \bigl(\beta + (1-\beta) S_i\bigr)}_{\text{production}} - C_i^{\text{oil}} + \underbrace{\sum_{j \neq i} T_{ij}^{\text{oil}}}_{\text{net trade}}$$

where $\beta = 0.5$ is the baseline production fraction. Fertilizer and water follow the same form.

### 3.2 Political Stability

$$\dot{S}_i = -\alpha_i^{\text{decay}} S_i + \alpha_i^{\text{gain}} \cdot a_i \cdot (1 - S_i) - \gamma_u \cdot U_i \cdot S_i$$

where:
- Resource abundance: $a_i = \tanh\bigl(\kappa_r (O_i + F_i + W_i)\bigr)$, $\kappa_r = 0.01$
- Social unrest: $U_i = \sigma(I_i - 0.6;\, k\!=\!10) \cdot \sigma(\pi_i - 0.1;\, k\!=\!20)$
- $\gamma_u = 0.1$ is the unrest strength

### 3.3 Military Expenditure

$$\dot{M}_i = \gamma_m \cdot \text{GDP}_i - \delta_m M_i - \gamma_{md} \cdot C_i^{\text{debt}} \cdot M_i$$

$\gamma_m = 0.01$, $\delta_m = 0.05$, $\gamma_{md} = 0.1$.

### 3.4 Inequality

$$\dot{I}_i = \gamma_{is}(1 - S_i) + \gamma_{id} D_i - \gamma_{ir} I_i$$

$\gamma_{is} = 0.01$, $\gamma_{id} = 0.005$, $\gamma_{ir} = 0.02$.

### 3.5 Sovereign Debt

$$\dot{D}_i = \underbrace{(G_i - T_i)}_{\text{primary deficit}} + \underbrace{(r_i / 365.25 - g_i) D_i}_{\text{interest-growth}} + \underbrace{\mu_d (\bar{D}_i - D_i)}_{\text{mean reversion}}$$

where:
- Government spending: $G_i = M_i \cdot \text{GDP}_i \cdot 0.01 \cdot A(D_i)$
- Tax revenue: $T_i = 0.30 \cdot \text{GDP}_i \cdot S_i$
- Austerity factor: $A(D) = \bigl(1 + e^{10(D - 2)}\bigr)^{-1}$
- Growth rate: $g_i = 0.02 \cdot S_i / 365.25$
- GDP proxy: $\text{GDP}_i = (P_i^{\text{oil}} + P_i^{\text{fert}}) \cdot S_i$, normalized

### 3.6 Commodity Prices

$$\dot{P}_i^o = \lambda_p \cdot b_i^o - \lambda_r (P_i^o - 1)$$

where the supply-demand balance is:
$$b_i^o = \frac{C_i^o - P_i^{\text{oil,prod}}}{C_i^o + P_i^{\text{oil,prod}} + \epsilon}$$

$\lambda_p = 0.01$, $\lambda_r = 0.05$. The normalized balance keeps $b \in [-1, 1]$.

Water price also receives a scarcity boost: $\dot{P}_i^w \mathrel{+}= 0.1 \cdot C_i^{\text{scarcity}}$.

### 3.7 Inflation

Using the log-price derivative (relative price change):

$$\dot{\pi}_i = w_o \frac{\dot{P}_i^o}{P_i^o + 1} + w_f \frac{\dot{P}_i^f}{P_i^f + 1} + w_w \frac{\dot{P}_i^w}{P_i^w + 1}$$

$w_o = 0.3$, $w_f = 0.3$, $w_w = 0.4$.

### 3.8 Interest Rate (Taylor Rule)

$$\dot{r}_i = \underbrace{0.5(r^* - r_i)}_{\text{reversion}} + \underbrace{1.5(\pi_i - \pi^*)}_{\text{inflation gap}} + \underbrace{0.5(D_i - \bar{D}_i)}_{\text{debt gap}} + \underbrace{0.02 \cdot C_i^{\text{debt}}}_{\text{risk premium}}$$

$r^* = 0.03$, $\pi^* = 0.02$.

### 3.9 Exchange Rate

$$\dot{E}_i = 0.001 \cdot \text{TB}_i - 0.01(E_i - 1) + 0.05 \cdot C_i^{\text{currency}} \cdot E_i + \sum_j \text{capital flow}$$

Trade balance: $\text{TB}_i = (P_i^{\text{oil,prod}} - C_i^o) + (P_i^{\text{fert,prod}} - C_i^f) + (A_i^w - C_i^w)$

### 3.10 Bond Yield

$$\dot{Y}_i = 0.1 \bigl(r_i + 0.02 \cdot C_i^{\text{debt}} - Y_i\bigr)$$

### 3.11 Exchange Rate Moving Average

$$\dot{\bar{E}}_i = \frac{E_i - \bar{E}_i}{30}$$

## 4. Inter-Region Coupling

### 4.1 Resource Trade

Bilateral flow from region $j$ to $i$:

$$T_{ij}^{\text{oil}} = \tau_{ij}^o \cdot s_{\text{trade}} \cdot S_j \cdot \frac{O_j}{O_j + K_h}$$

where $\tau_{ij}^o$ is the base trade matrix entry, $s_{\text{trade}} = 0.01$ is the scale factor, and $K_h = 1000$ is the Monod half-saturation constant.

Conservation: $\dot{O}_i \mathrel{+}= T_{ij}$, $\dot{O}_j \mathrel{-}= T_{ij}$.

### 4.2 Stability Diffusion

$$\delta S_i^{(j)} = c_{ij} (S_j - S_i) S_i (1 - S_i)$$

The logistic factor $S_i(1-S_i)$ ensures coupling is strongest at intermediate stability and vanishes at the boundaries.

### 4.3 Financial Contagion

**Capital flows** (exchange rate coupling):
$$\delta E_i^{(j)} = 0.001 \cdot \phi_{ij} (E_j - E_i)$$

**Interest rate coupling**:
$$\delta r_i^{(j)} = 0.01 \cdot f_{ij} (r_j - r_i)$$

### 4.4 Price-Mediated Trade (Extension)

When enabled, additional trade flows are driven by regional price differentials:

$$T_{ij}^{\text{price}} = \eta_p \cdot \max(P_i - P_j, 0) \cdot \frac{S_j}{1 + c_t} \quad \text{subject to} \quad T_{ij}^{\text{price}} \le \alpha_t \cdot X_j$$

where $\eta_p$ is price elasticity, $c_t$ is transport cost, and $\alpha_t$ is the maximum tradeable fraction per day. This closes the economic loop: scarcity raises prices, which attract imports, which reduce scarcity.

## 5. Nonlinear Thresholds

All thresholds use the smooth sigmoid $\sigma(x; k, x_0) = (1 + e^{-k(x-x_0)})^{-1}$:

| Crisis | Trigger | Parameters | Effect |
|--------|---------|------------|--------|
| **Debt crisis** | $D_i > 1.0$ | $k=10$ | Suppresses military, adds risk premium |
| **Currency crisis** | 30-day depreciation > 20% | $k=20$ | Capital flight |
| **Social unrest** | $I_i > 0.6$ AND $\pi_i > 0.1$ | $k=10, 20$ | Reduces stability |
| **Water scarcity** | $W_i < 0.1 W_i^0$ | $k=0.1$ | Water price spike |

## 6. Interventions

Interventions modify the parameter dict at each time step $t$:

$$\text{params}'(t) = \mathcal{I}(t, \text{params})$$

Built-in types:
- **Chokepoint disruption**: $\tau_{*j}(t) \leftarrow (1 - s \cdot \rho(t)) \tau_{*j}$ where $\rho(t)$ is a ramp function
- **Bilateral sanction**: $\tau_{ij}(t) \leftarrow (1 - s \cdot \rho(t)) \tau_{ij}$ for specific $(i,j)$
- **Supply shock**: $P_i^{\text{prod}}(t) \leftarrow (1 - s \cdot \rho(t)) P_i^{\text{prod}}$

## 7. Regions

| Index | Region | Notes |
|-------|--------|-------|
| 0 | North America | USA, Canada, Mexico |
| 1 | Europe | EU + UK, Norway, Switzerland |
| 2 | Russia | |
| 3 | Middle East | GCC, Iran, Iraq, Turkey, Egypt |
| 4 | China | Including Taiwan, HK |
| 5 | India | |
| 6 | Japan | |
| 7 | Southeast Asia | ASEAN members |
| 8 | Australia/New Zealand | |
| 9 | Africa (sub-Saharan) | |
| 10 | South America | |
| 11 | Central Asia/Caucasus | |

## 8. Assumptions and Limitations

1. **GDP proxy**: $(P^{\text{oil}} + P^{\text{fert}}) \times S$ — captures resource-dependent economies but omits services, manufacturing
2. **Trade flows**: Bilateral matrix from production surplus allocation, not price-responsive (unless price-mediated extension enabled)
3. **No explicit banking sector**: Interest rate via Taylor rule, no credit creation
4. **No substitution**: Oil, fertilizer, water are independent — no interconversion
5. **Deterministic**: No stochastic shocks — all uncertainty enters via parameter choices
6. **Daily resolution**: Annual rates converted via $1/365.25$ factor
7. **System is stiff**: Requires implicit solver (BDF); explicit methods diverge
