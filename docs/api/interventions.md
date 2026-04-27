# Interventions

Interventions are composable, time-resolved modifications to model parameters. They are applied at each ODE step via:

```
params'(t) = I(t, params)
```

The `Intervention` dataclass holds a name, a time window, and a parameter-modification function.

::: interventions
