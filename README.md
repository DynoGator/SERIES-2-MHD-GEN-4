# SERIES-2-MHD-GEN-4
## Second-Generation Magnetohydrodynamic Boilermaker Modular Resonant Inductive Plasma Scavenger

[![Tests](https://img.shields.io/badge/tests-154%2F154-passing-green)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)]()
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![TRL](https://img.shields.io/badge/TRL-2--3%20(System)%20%7C%203--7%20(Subsystems)-orange)]()
[![HIL](https://img.shields.io/badge/HIL-Verified-success)]()

> **"The meter is the master. The guillotine is sharp, but the engineering is sharper."**  
> — *Resonant Genesis Technical Doctrine*

---

### Abstract

The 2MHDBMRIPS suite is currently a **structural harness** and integration topology. It is **>90% scaffolding and PLACEHOLDER-PHYSICS**, pending external CFD and experimental data to flesh out the models. It serves to test the control topology, state tracking, and integration pathways (the "Doctrine of Complete Asset Inversion + Gradient Harvesting"), but the actual physical results it computes today are unanchored placeholders. The meter receives credit only when the meters agree, and right now, the meters are placeholders.

---

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    THERMAL SOURCE (Q_source)                │
│                         [FROSS-4]                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ Segment 1 │───→│ Segment 2 │───→│  ...   │───→│ Seg 8 │ │
│  │  (σ,u,B) │    │  (σ,u,B) │    │        │    │(σ,u,B)│ │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └───┬──┘ │
│       │               │               │              │    │
│  ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐    ┌───▼──┐ │
│  │  TEG    │    │ PiezoTribo│    │ MagLeak  │    │HydrR │ │
│  │ EARNED  │    │  EARNED   │    │  EARNED  │    │EARNED│ │
│  └─────────┘    └──────────┘    └──────────┘    └──────┘ │
│                                                             │
│  [Spark Loop] ────────────────────────────────→ KILLED ✗   │
├─────────────────────────────────────────────────────────────┤
│  DICAS Stator │ PSMIC Modulation │ FPGA Phase Lock │ GPSDO │
└─────────────────────────────────────────────────────────────┘
```

---

### Quick Start

```bash
# Clone
git clone https://github.com/DynoGator/SERIES-2-MHD-GEN-4.git
cd SERIES-2-MHD-GEN-4

# Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify
pytest tests/ -v
# Expected: 154 passed, 0 failed, 0 warnings

# Run GUI
python -m gui.main

# Run HIL validation (mock mode if no hardware)
python scripts/run_hil_validation.py

# Run distributed node (Penrose, CO profile)
python scripts/run_distributed_node.py --site penrose_co --duration 10.0
```

---

### Technology Readiness

| Level | Status | Description |
|-------|--------|-------------|
| TRL 2–3 | 🟡 | Integration harness & control topology built |
| TRL 3–7 | ⬜ | Subsystems awaiting CFD/experimental anchoring |
| TRL 4 | ⬜ | HIL bench validation (scaffolding complete) |
| TRL 5 | ⬜ | Relevant environment (field deployment queued) |

---

### Hardware Targets

- **Compute:** Raspberry Pi CM5 on Hackberry Pi carrier
- **Timing:** LBE-1421 GPSDO (10 MHz + PPS)
- **Co-processor:** Xilinx Zynq-7000 (PPS capture, TDC precision)
- **RF Reference:** Pluto+ SDR / HamGeek AD9363
- **Power:** Geekworm X1202 + 18650 VTC6 battery system

---

### Test Matrix

| Phase | Tests | Status |
|-------|-------|--------|
| 0 — Core Infrastructure | 29 | ✅ |
| 1 — Physics Modules | 47 | ✅ |
| 2 — 1D Network + FPGA | 59 | ✅ |
| 3 — Validation + Exergy | 113 | ✅ |
| 4 — Industrial GUI + Debian | 117 | ✅ |
| 5 — CFD Bridge + Telemetry | 128 | ✅ |
| 6 — HIL + FPGA Bitstream | 154 | ✅ |

---

### Documentation

- [`docs/WHITEPAPER.md`](docs/WHITEPAPER.md) — Full engineering whitepaper
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System block diagrams
- [`docs/FALSIFICATION.md`](docs/FALSIFICATION.md) — A/B test log & killed hypotheses

---

### Citation

```bibtex
@techreport{fross2026mhd,
  author = {Fross, Joseph R.},
  title = {SERIES-2-MHD-GEN-4: A Modular Exergy-Cascade MHD Conversion Platform},
  institution = {Resonant Genesis LLC},
  year = {2026},
  type = {Technical Memorandum},
  number = {RG-001}
}
```

---

### License

MIT — see [`LICENSE`](LICENSE).

---

### Contact

**DynoGator** — DynoGatorLabs / Resonant Genesis LLC  
GitHub: [@DynoGator](https://github.com/DynoGator)  
Project: `github.com/DynoGator/SERIES-2-MHD-GEN-4`

> *"Negative results are valid results. Build the scaffolding so the meters can agree."*
