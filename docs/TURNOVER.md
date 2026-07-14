# Collaborator Turnover — SERIES-2-MHD-GEN-4

**As of:** 2026-07-14 (end-of-day lock, tag `v5.0.0-pra-eod`)
**Repo:** https://github.com/DynoGator/SERIES-2-MHD-GEN-4 (public)
**Maintainer:** DynoGator / Resonant Genesis LLC

This is the "pick it up cold" document for anyone joining the project. Read it, then
`docs/ARCHITECTURE.md` for signal flow and `docs/FALSIFICATION.md` for what's proven
vs. killed. `docs/WHITEPAPER.md` is the theory of operation.

---

## 1. Where the project stands

- **Phases 0–8 complete.** Core physics → 1-D/2-D/CFD twin ladder → control/HIL →
  telemetry/GUI → production hardening (BOM, Docker, K8s, Grafana, compliance).
- **Tests: 197/197 passing** locally and in CI (Python 3.11 / 3.12 / 3.13).
- **CI is green on `main`** (GitHub Actions: test matrix + lint + build-deb).
- **Tagged** `v5.0.0-pra` (Phase 7) and `v5.0.0-pra-eod` (this lock).
- **Fully-burdened unit cost** closes at **$18,666.67** (target band $10k–$25k),
  16-week critical-path procurement lead time.

## 2. Quickstart

```bash
git clone https://github.com/DynoGator/SERIES-2-MHD-GEN-4.git
cd SERIES-2-MHD-GEN-4
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run the suite (repo root must be importable)
PYTHONPATH=. pytest tests/ -q            # 197 passed
# GUI/Qt tests are headless-safe: QT_QPA_PLATFORM=offscreen if no display

# Representative runs (scripts self-insert the repo root on sys.path)
python scripts/run_distributed_node.py --site penrose_co --duration 10.0
python scripts/run_hil_validation.py             # 60 s mock HIL campaign
python scripts/run_production_build.py           # BOM CSV -> tests -> docker -> report

# Container (no host Python needed)
docker build -f docker/Dockerfile -t 2mhd-twin:latest .
docker compose -f docker/docker-compose.yml config
```

## 3. Repo layout (high level)

| Path | What |
|------|------|
| `core/` | StateVector (24-elem frozen), SafetyMachine, RK45 integrator, units |
| `physics/` | mhd, thermo, mechanical, electromagnetic, acoustic, exergy, scavengers |
| `digital_twin/` | lumped → network_1d → channel_2d → cfd_bridge, hil_runner |
| `control/` | fpga, state_machine (15-state), pid, mpc |
| `hardware/` | fpga_interface, pps_capture, gpsdo_sync, vivado_build, rtl/ |
| `telemetry/` | dslv_zpdi_pipeline, streaming_server |
| `gui/` | PyQt6 app, widgets/ (incl. Production tab) |
| `config/` | system_config, sites, materials_db (physics + BOM), cost_model |
| `validation/` | gates G0–G9 |
| `docker/`, `k8s/`, `grafana/`, `compliance/` | Phase 8 deployment & commercial |
| `scripts/` | CLI entry points (all standalone-runnable) |
| `docs/` | WHITEPAPER, ARCHITECTURE, FALSIFICATION, daily changelogs, this file |

## 4. API contracts you must not break

See `docs/ARCHITECTURE.md` §2 for the table. Highlights:
- `StateVector` is frozen/24-element; mutate only via `.evolve()`; `from_array()` clamps.
- `DerivativeContribution` fields are `dydt` + `power_ledger` (not `derivatives`/`ledger`).
- `SafetyMachine` has no self-clear; `FAULT_LATCH` needs a two-ack + investigation reset.
- `TwinStateMachine.current_state` is a **property**; transition via `transition(StateEvent.X)`.

## 5. Open items (start here)

1. **Scavenger code-vs-doctrine mismatch — HIGH.** `docs/FALSIFICATION.md` §3: the
   whitepaper says SparkLoop=KILLED / MagneticLeakage=EARNED, but
   `digital_twin/validation_runner.py` marks all five `PENDING`, SparkLoop's model
   returns +150 W (passes its gate), and the test fixture fails MagneticLeakage.
   Decide ground truth and make code, tests, and docs agree; promote survivors to
   `EARNED` in the registry status (not just prose).
2. **Validation gate stubs.** G1, G2, G4–G7, G9 in `validation/gates.py` return
   hard-coded passes — scaffolding, not yet falsifying. Wire live criteria.
3. **Phase 9 (queued, not started):** Field Trial / Alpha Node deployment at Penrose, CO.

## 6. How to contribute

- Branch off `main`; open a PR. **CI must be green** (test matrix + lint + build-deb)
  and the full suite must pass before merge.
- Keep the falsifiability doctrine: quantitative prediction → A/B gate → replication.
  Negative results are valid results; a killed hypothesis is removed, not renamed.
- Docs travel with code: update WHITEPAPER/ARCHITECTURE/FALSIFICATION when behavior changes.

## 7. Branch & tag state at handoff

- `main` @ `8960ac9` — everything merged, CI green.
- Tags: `v5.0.0-pra`, `v5.0.0-pra-eod`.
- Feature branches `phase8-production` and `worktree-mhd-docs-scriptfix` are merged and
  safe to delete.

---
*The meter is the master. The commit is the signature. Build on.* 🔧⚡🐊
