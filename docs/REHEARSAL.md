# Phase 13: Full-Dress Rehearsal

## Mission Timeline (Gates)

The rehearsal executes the following sequence. Any failure triggers an immediate abort on the bench.

1. **PROVISION_DRYRUN**: Verifies the deployment script has zero live side-effects and logs all critical host setup (apt, systemd).
2. **GPSDO_LOCK**: Runs the pre-flight gate. Proves hardware state logic properly bounds the Allan deviation before accepting data.
3. **CALIBRATION**: Executes field calibration, generating a baseline profile.
4. **AGENT_START**: Spins up the `NodeAgent` daemon. Proves heartbeats reach the `CentralAggregator`.
5. **CAMPAIGN_RECORD**: Generates telemetry using the `PenroseSignalModel`, injecting a correlated 5-sigma geomagnetic spike across `alpha` and `beta` nodes with latency.
6. **ANOMALY_WINDOW**: Proves detection state over recorded streams.
7. **BROKER_KILL**: Simulates network partition. The `MeshFallback` transition to `DEGRADED`.
8. **BROKER_RESTORE**: Mesh transition continues to `MESH`, then back to `BROKERED` upon recovery.
9. **OFFLOAD_REPLAY**: Replays the campaign deterministicly to generate an immutable digest.
10. **CONSENSUS_VERDICT**: Verifies the correlated spike is `CONFIRMED` and lone noise is `REJECTED_UNCORROBORATED`.

## Known Limitations

This rehearsal is a software bench test. It does **NOT** prove:

- **Real RF Environment**: Environmental EMI and ionospheric scatter are approximated by noise curves.
- **Physical GPSDO Timing**: We are mocking the LBE-1421. Actual hardware locks take time and can drop due to sky visibility.
- **Thermal Reality**: The thermal model is deterministic. A real Pelican case in July sun in Penrose, CO may exceed operational limits.
- **Network Stack Reality**: `inproc://` ZMQ is not `tcp://` over a cellular modem with jitter and packet loss.

*Honesty is doctrine. The meter is the master.*
