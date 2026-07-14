# FCC Pre-Check — 2MHDBMRIPS GEN-5.0-PRA

**Applicable standard:** FCC Part 15, Subpart B (Unintentional Radiators) and
Subpart C where the SDR/RF front end applies. The 10 MHz GPSDO reference and the
LibreSDR-class RF section are the primary emitters of interest.

| Field | Value |
|-------|-------|
| Test item | 10 MHz GPSDO reference, Zynq-7000 digital section, SDR front end |
| Standard | FCC Part 15 §15.109 (radiated), §15.107 (conducted) |
| Pass/fail criteria | Radiated emissions ≤ Class A limits (industrial); conducted ≤ 79 dBµV quasi-peak, 30–230 MHz |
| Estimated cost | **$5,000** (pre-scan) |
| Timeline | 3 weeks |
| Responsible party | Internal pre-scan → third-party accredited lab for final |

## Checklist
- [ ] Shielded enclosure bonding verified (< 2.5 mΩ)
- [ ] GPSDO 10 MHz harmonics measured to 1 GHz
- [ ] Switching-supply (X1202) conducted emissions on AC/DC lines
- [ ] SDR TX disabled or type-accepted module used
- [ ] Ferrite suppression on all external I/O cables
- [ ] Pre-scan report archived with the unit serial number

## Notes
Grid-tied or emissions-relevant behavior is device-specific. Final grant of
authorization requires an accredited lab; this pre-check de-risks that visit.
