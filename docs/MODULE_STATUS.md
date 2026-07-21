# Digital Twin Module Status Registry

All modules in the `physics/` and `digital_twin/` directories must bear a header declaring their epistemological status:

- **SCAFFOLD**: Pure structural boilerplate, passes variables but performs no physics.
- **PLACEHOLDER-PHYSICS**: Contains mock physics (e.g., hardcoded constants, non-physical approximations) sufficient to keep the integration suite running, but not for validation. Propagates uncertainty end-to-end.
- **PROVISIONAL**: Realistic physics implementation pending final peer-review and experimental validation.
- **REAL**: Fully validated, anchored physics.

| Module Directory | Status | Notes |
|------------------|--------|-------|
| `digital_twin/` | SCAFFOLD/CONSTRAINED | Defines integration topology and physical bounds (Phase 2 constraint applied) |
| `physics/base.py` | SCAFFOLD | Interfaces |
| `physics/exergy/cascade.py` | PLACEHOLDER-PHYSICS | Awaiting physical heat flows |
| `physics/mhd/conductivity.py` | PLACEHOLDER-PHYSICS / PROVISIONAL | Includes both fallback and Saha equations (Physics stubbed) |
| `physics/mhd/faraday_channel.py` | PLACEHOLDER-PHYSICS | Propagates placeholder conductivity |
| `physics/thermo/accumulator.py` | PROVISIONAL | FROSS accumulator volume clamped to non-negative physical bounds |
| `physics/scavengers/` | PROVISIONAL | All scavengers require hardware A/B test |

Any output derived from `PLACEHOLDER-PHYSICS` modules will result in an `INDETERMINATE` gate verdict.

## Known Test Failures (xfail)

| Test Name | Category | Reason |
|-----------|----------|--------|
| `test_sigma_against_reference[2000.0-0.01-101325.0-1.0-0.5]` | `xfail(strict=True)` pending-physics | Saha equation lacks collision cross-sections for accurate conductivity |
| `test_sigma_against_reference[2500.0-0.01-101325.0-20.0-0.5]` | `xfail(strict=True)` pending-physics | Saha equation lacks collision cross-sections for accurate conductivity |
| `test_sigma_against_reference[3000.0-0.01-101325.0-100.0-0.5]` | `xfail(strict=True)` pending-physics | Saha equation lacks collision cross-sections for accurate conductivity |
