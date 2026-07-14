# CE Marking — 2MHDBMRIPS GEN-5.0-PRA

**Applicable standards:** Machinery Directive **2006/42/EC**, Low Voltage Directive
**2014/35/EU**, EMC Directive **2014/30/EU**.

| Field | Value |
|-------|-------|
| Test item | Complete power unit (mechanical + electrical + control) |
| Standard | 2006/42/EC (machinery), 2014/35/EU (LVD), 2014/30/EU (EMC) |
| Pass/fail criteria | Risk assessment closed per EN ISO 12100; LVD isolation/creepage per EN 61010-1; EMC per EN 61326 |
| Estimated cost | **$8,000** |
| Timeline | 8 weeks |
| Responsible party | Internal Technical File authoring → Notified Body review |

## Checklist
- [ ] Technical File assembled (drawings, risk assessment, test reports)
- [ ] EN ISO 12100 hazard analysis (rotating machinery, high temperature, pressure)
- [ ] Emergency stop per EN ISO 13850 (maps to SafetyMachine EMERGENCY_DUMP)
- [ ] Creepage/clearance per EN 61010-1 for the HV extraction bus
- [ ] Declaration of Conformity drafted and signed
- [ ] CE mark affixed with unit serial number

## Notes
The SafetyMachine `FAULT_LATCH` two-acknowledgment reset satisfies the "no automatic
restart after fault" requirement of the Machinery Directive.
