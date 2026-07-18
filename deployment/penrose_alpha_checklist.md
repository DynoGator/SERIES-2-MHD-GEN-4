# Penrose Alpha Node Deployment Checklist

## 1. Site Survey & RF-Quiet Check
- [ ] Inspect 10m radius for EMI sources (transformers, unshielded lines).
- [ ] Sweep area with handheld RF meter; verify ambient noise < -80 dBm.
- [ ] Pass/Fail: _______ Sign-off: _______

## 2. Mechanical/Case Prep
- [ ] Unpack Pelican case; inspect seals and O-rings for integrity.
- [ ] Verify shock mounts for CM5 and Zynq-7000 are secure.
- [ ] Pass/Fail: _______ Sign-off: _______

## 3. Power System
- [ ] Verify 18650 VTC6 battery 1 state of charge (>3.8V unloaded).
- [ ] Verify 18650 VTC6 battery 2 state of charge (>3.8V unloaded).
- [ ] Engage X1202 power management module; verify 5V/3.3V rails stable.
- [ ] Pass/Fail: _______ Sign-off: _______

## 4. GPSDO Lock Verification
- [ ] Connect GPS antenna to LBE-1421.
- [ ] Monitor 1PPS output; verify 3D lock acquired within 15 minutes.
- [ ] Confirm Allan deviation threshold is within spec (< 1e-10 at tau=1s).
- [ ] Pass/Fail: _______ Sign-off: _______

## 5. Sensor Baseline
- [ ] Mount and connect geomagnetic, thermal, and acoustic sensors.
- [ ] Verify raw I2C/SPI readings on Hackberry Pi are non-zero and updating.
- [ ] Pass/Fail: _______ Sign-off: _______

## 6. Calibration Campaign Execution
- [ ] Power on CM5 and run `alpha_node_provision.sh`.
- [ ] Execute `field_calibration.py --site penrose_co --duration 1.0`.
- [ ] Verify calibration JSON payload generated successfully.
- [ ] Pass/Fail: _______ Sign-off: _______

## 7. Anomaly Response Procedure
- [ ] Start `anomaly_detector.py` service.
- [ ] Inject synthetic GPSDO_UNLOCK anomaly.
- [ ] Verify anomaly detector successfully triggers and logs the event.
- [ ] Pass/Fail: _______ Sign-off: _______

## 8. Comms/ZMQ Link Check
- [ ] Establish ZMQ connection to base station via local mesh.
- [ ] Verify heartbeat rate (1Hz) is received by Grafana dashboard.
- [ ] Pass/Fail: _______ Sign-off: _______

## 9. Teardown & Data Offload
- [ ] Sync all local SQLite/H5 logs to external NVMe.
- [ ] Power down CM5 gracefully; disengage X1202.
- [ ] Stow all components in Pelican case.
- [ ] Pass/Fail: _______ Sign-off: _______

## 10. Abort Criteria
- [ ] If battery voltage < 3.5V, ABORT.
- [ ] If GPSDO lock is lost for > 5 minutes, ABORT.
- [ ] If thermal runaway detected (> 60C ambient inside case), ABORT.
- [ ] Acknowledged: _______ Sign-off: _______
