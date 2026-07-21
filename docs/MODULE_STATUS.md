# Digital Twin Module Status Registry

All modules in the `physics/` and `digital_twin/` directories must bear a header declaring their epistemological status:

- **SCAFFOLD**: Pure structural boilerplate, passes variables but performs no physics.
- **PLACEHOLDER-PHYSICS**: Contains mock physics (e.g., hardcoded constants, non-physical approximations) sufficient to keep the integration suite running, but not for validation. Propagates uncertainty end-to-end.
- **PROVISIONAL**: Realistic physics implementation pending final peer-review and experimental validation.
- **REAL**: Fully validated, anchored physics.

| Module Directory | Status | Notes |
|------------------|--------|-------|
| `digital_twin/` | SCAFFOLD | Defines integration topology |
| `physics/base.py` | SCAFFOLD | Interfaces |
| `physics/exergy/cascade.py` | PLACEHOLDER-PHYSICS | Awaiting physical heat flows |
| `physics/mhd/conductivity.py` | PLACEHOLDER-PHYSICS / PROVISIONAL | Includes both fallback and Saha equations |
| `physics/mhd/faraday_channel.py` | PLACEHOLDER-PHYSICS | Propagates placeholder conductivity |
| `physics/scavengers/` | PROVISIONAL | All scavengers require hardware A/B test |

Any output derived from `PLACEHOLDER-PHYSICS` modules will result in an `INDETERMINATE` gate verdict.
