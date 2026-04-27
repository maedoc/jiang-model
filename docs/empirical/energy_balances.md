# Production \u0026 Consumption Balances

## Regional table (2023, Energy Institute Statistical Review)

| Region | Production (kb/d) | Consumption (kb/d) | Balance | Import Dependence |
|--------|------------------|--------------------|---------|-------------------|
| Middle East | 30,362 | 9,646 | **+20,716** | Net exporter |
| North America | 27,050 | 23,296 | **+3,754** | Net exporter |
| CIS (Russia+) | 13,868 | 4,636 | **+9,232** | Net exporter |
| China | 4,198 | 16,577 | **−12,379** | **~75% import reliant** |
| Europe | 3,225 | 13,904 | **−10,679** | **~77% import reliant** |
| Asia Pacific (total) | 7,275 | 38,061 | **−30,786** | Net importer |

**Key insight for GT#21 narrative:** North America and Russia/CIS are the two major surplus regions. If Middle East exports are cut off, Asia and Europe must source from North America and Russia — validating the "dependency shift" mechanism in the model.

## Model translation

The model's trade matrix is calibrated so that:
- **Surplus regions** (Middle East, Russia, North America) have positive net exports
- **Deficit regions** (China, Europe, Asia Pacific) have negative net exports
- The **magnitude** of flows is scaled to ~200 model units/day globally

### Trade matrix structure

```python
# From real_params.json
oil_trade_flow[i, j] = net export from region j to region i
```

- `oil_trade_flow[:, j]` = exports *from* region j
- `oil_trade_flow[i, :]` = imports *to* region i

## Validation checks

| Check | Model | EI data | Agreement |
|-------|-------|---------|-----------|
| Middle East is largest exporter | ✓ | ✓ | Yes |
| China is largest importer | ✓ | ✓ | Yes |
| Europe deficit > North America surplus | ✓ | ✓ | Yes (Europe must import from Middle East + Russia) |
| Asia Pacific aggregate deficit | ✓ | ✓ | Yes |

!!! note
    The model aggregates Southeast Asia, Japan, India, and Australia/New Zealand into a single "Asia Pacific" balance. For finer-grained analysis (e.g., Japan vs. India import dependence), consult the per-country data in `data_loader.py`.
