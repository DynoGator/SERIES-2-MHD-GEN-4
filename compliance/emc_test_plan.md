# EMC Test Plan — 2MHDBMRIPS GEN-5.0-PRA

**Applicable standards:** **FCC Part 15** (US), **EN 61326-1** / **CISPR 11** (EU
industrial), covering radiated & conducted emissions and immunity.

| Field | Value |
|-------|-------|
| Test item | Full unit under representative load, mock and live HIL |
| Standard | CISPR 11 Class A, EN 61326-1, FCC Part 15 §15.109 |
| Pass/fail criteria | Emissions ≤ Class A; immunity per EN 61000-4-x with no loss of safety function |
| Estimated cost | **$6,000** |
| Timeline | 4 weeks |
| Responsible party | Third-party accredited EMC lab |

## Test matrix
| Test | Standard | Criteria |
|------|----------|----------|
| Radiated emissions | CISPR 11 / FCC §15.109 | ≤ Class A, 30 MHz–1 GHz |
| Conducted emissions | CISPR 11 / FCC §15.107 | ≤ Class A on mains |
| ESD immunity | EN 61000-4-2 | ±4 kV contact, ±8 kV air, safety retained |
| Radiated immunity | EN 61000-4-3 | 10 V/m, 80 MHz–1 GHz |
| EFT/burst | EN 61000-4-4 | ±2 kV power, ±1 kV signal |
| Surge | EN 61000-4-5 | ±1 kV L-L, ±2 kV L-E |

## Notes
Immunity acceptance requires the SafetyMachine to hold `ARMED`/`WARNING` correctly
and never spuriously clear a `FAULT_LATCH` under any injected disturbance.
