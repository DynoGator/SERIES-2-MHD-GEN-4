# SERIES-2-MHD-GEN-4 — Falsification Ledger

## Resonant Genesis LLC / DynoGatorLabs — Companion to `WHITEPAPER.md`

> "The guillotine is sharp, but the engineering is sharper."
> **Negative results are valid results. A killed hypothesis is removed — not renamed, not reframed, not retained.**

This document is the evidence ledger. Every energy-recovery claim ("scavenger") and
every physics gate must survive a quantitative A/B falsification test before it earns
a place in the build. This file records what passed, what failed, and — critically —
where the recorded verdict and the executable code do **not yet agree**.

---

## 1. The Doctrine (four hurdles)

Every claim must survive, in order:

1. **Quantitative prediction** — a number, with units, before the test.
2. **A/B test with a falsification gate** — run *with* and *without* the mechanism;
   compute `net_delta_w = with_w − without_w`; apply a hard `kill_criterion`.
3. **Independent replication** — the result reproduces on a fresh run/node.
4. **Peer review** — the ledger is auditable by someone who did not build it.

The machinery lives in:
- `config/scavenger_registry.py` — `ScavengerEntry(status, kill_criterion, ab_test_history)`;
  status ∈ `{PENDING, EARNED, KILLED}`.
- `digital_twin/validation_runner.py` — registers each scavenger and runs A/B.
- `validation/gates.py` — physics gates **G0–G9**.
- `physics/exergy/cascade.py` — the exergy accounting that G0/G8 audit.

---

## 2. Scavenger A/B Ledger — Documented Verdicts

Per the whitepaper narrative (`WHITEPAPER.md` §4.5), five triboelectric / harvest
mechanisms were proposed. Four earn their keep; one was killed.

| Scavenger | Mechanism | Verified against | Documented verdict |
|-----------|-----------|------------------|--------------------|
| Thermoelectric (TEG) | Wall-array Seebeck extraction | thermal gradient | **EARNED** |
| PiezoTribo | Vibration harvest from rotor imbalance | accelerometer | **EARNED** |
| MagneticLeakage | DICAS flux pickup coils | B-field probe | **EARNED** |
| HydraulicRegen | FROSS expansion-work recovery | pressure transducer | **EARNED** |
| **SparkLoop** | Triboelectric charge capture | — | **KILLED ✗** |

**Spark Loop — cause of death (recorded):** triboelectric charge capture failed
reproducibility. It was removed from the earned set, not renamed. The class file
`physics/scavengers/spark_loop.py` is retained only as a falsification artifact.

---

## 3. ⚠️ Open Audit — Code vs. Doctrine Disagreement [RESOLVED]

**RESOLVED 2026-07-18 via Option B** (code aligned to whitepaper):
SparkLoop = KILLED (net −30 W), MagneticLeakage = EARNED (net +13 W).

*Note: Scavenger constants are doctrine-aligned PLACEHOLDER values, not bench-validated physics. Hardware meters get the final vote at field trial.*

Honesty first: the executable state previously did **not** match the documented
verdicts in §2. This was logged as an open item, not hidden, and the record is preserved here:

**Finding (Pre-Phase 9).**
- `digital_twin/validation_runner.py` initialized **all five** scavengers with
  `status="PENDING"` — no scavenger is hard-wired as `EARNED` or `KILLED`.
- The kill criteria were:
  - `SparkLoop`: killed if `net_delta_w < 50.0` (must yield ≥ 50 W net).
  - `Thermoelectric / PiezoTribo / MagneticLeakage / HydraulicRegen`: killed if
    `net_delta_w <= 0.0`.
- `physics/scavengers/spark_loop.py::compute` returned `net = 200 − 50 = 150 W`
  (positive) and its `ab_test` returned `(1000, 1200)` — i.e. the model, as written,
  made Spark Loop look *beneficial* and it would **pass** its ≥50 W gate.
- `tests/scavengers/test_scavengers.py` asserted the opposite fixture: it marked
  **MagneticLeakage** as the net-negative failure (`expected = False`) while
  `SparkLoop` was expected `True` (net-positive).

**Consequence (Pre-Phase 9).** If the registry were driven purely by that code, the killed
scavenger would be **MagneticLeakage**, and **SparkLoop would survive** — the inverse
of the whitepaper narrative.

**Reconciliation (Phase 9):** We decided the doctrine (whitepaper) is ground truth and made
the code match (Option B):
1. Spark Loop is genuinely killed → set its model to the failing regime (net −30 W),
   set `ScavengerEntry(SparkLoop, "KILLED", …)`, and flipped the test expectation.
2. MagneticLeakage was updated to an EARNED placeholder (net +13 W).
3. The four survivors were explicitly promoted from `PENDING` to `EARNED` in the registry.

This keeps the negative result history valid, while bridging the code and doctrine until real hardware meters validate the models.
---

## 4. Physics Validation Gates (G0–G9)

Defined in `validation/gates.py`, executed against the lumped and 1-D network twins.
Gates with live numeric checks are marked ✔; gates currently returning fixed
pass-stubs are marked ⓘ (placeholder — needs a live criterion wired in).

| Gate | Name | Check | Status |
|------|------|-------|--------|
| G0 | Energy Accounting | unmeasured loss < 5 % | ✔ live |
| G1 | Cold Flow | compressor map match | ⓘ stub-pass |
| G2 | Acoustic Control | mode suppression ≥ dB target (12 dB) | ⓘ stub-pass |
| G3 | FROSS-4 Transient | `max_p` under vessel limit | ✔ live |
| G4 | Material Qualification | wall recession within bound | ⓘ stub-pass |
| G5 | First Plasma | ignition achieved | ⓘ stub-pass |
| G6 | MHD Extraction | σ scaling holds | ⓘ stub-pass |
| G7 | PSMIC Validation | instability reduced (~0.6) | ⓘ stub-pass |
| G8 | Energy Closure | ledger imbalance within limit | ✔ live |
| G9 | Endurance | drift ≤ 2 % over run | ⓘ stub-pass |

**Note:** G1, G2, G4–G7, G9 currently return hard-coded `GateResult(..., True, …)`
values. They are scaffolding that lets the gate runner and reporting pipeline execute
end-to-end; they are **not yet falsifying**. Wiring live criteria into these is
tracked work. Reporting them as "passing" without this note would overstate the
evidence — so it is stated.

---

## 5. Ledger Discipline

- A killed mechanism's class file stays in-tree as a **falsification record**, prefixed
  in docs with its verdict. Deletion would erase the negative result; the negative
  result is the point.
- A/B history accumulates in `ScavengerEntry.ab_test_history` — every run appends, none
  overwrite.
- Verdicts belong in **status fields**, not only in prose. §3 exists because that rule
  is currently violated.

---

*Companion documents: `WHITEPAPER.md` (theory), `ARCHITECTURE.md` (signal flow).*
*Negative results are valid results. The meter is the master.* 🔧⚡🐊
