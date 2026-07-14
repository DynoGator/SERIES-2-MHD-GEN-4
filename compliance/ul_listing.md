# UL Listing — 2MHDBMRIPS GEN-5.0-PRA

**Applicable standards:** **UL 508A** (Industrial Control Panels) and **UL 1998**
(Software in Programmable Components).

| Field | Value |
|-------|-------|
| Test item | Control panel assembly + embedded twin/safety software |
| Standard | UL 508A (panel), UL 1998 (safety-related software) |
| Pass/fail criteria | SCCR rating adequate for install; software risk analysis per UL 1998 §5; no single fault defeats E-stop |
| Estimated cost | **$12,000** |
| Timeline | 12 weeks |
| Responsible party | Third-party (UL / accredited NRTL) |

## Checklist
- [ ] Short-Circuit Current Rating (SCCR) determined and marked
- [ ] Wiring, spacings, and component certifications per UL 508A
- [ ] UL 1998 software risk analysis for SafetyMachine and TwinStateMachine
- [ ] Watchdog / fail-safe demonstrated (FAULT_LATCH, no self-clear)
- [ ] Field evaluation vs. full listing decision documented
- [ ] Listing mark + serial number applied

## Notes
UL 1998 credit is aided by the falsifiable test suite: 163/163 automated tests plus
the two-acknowledgment fault reset provide the documented safety-software evidence.
