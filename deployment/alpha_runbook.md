# Alpha Node Operator Runbook
**Location:** Penrose, CO
**Hardware:** CM5 + LBE-1421 GPSDO

## Gate 1: Provisioning
Run the provisioning script in dry-run mode first to verify state.
```bash
bash deployment/alpha_node_provision.sh --dry-run
```
*Expected: List of steps prefixed with `[DRY-RUN]`. No apt or systemctl errors.*
*Abort: Syntax errors or unexpected side effects.*

If dry-run passes, execute live:
```bash
sudo bash deployment/alpha_node_provision.sh
```
*Sign-off: _________*

## Gate 2: GPSDO Lock Verification
Verify the LBE-1421 has achieved strict lock.
```bash
python3 scripts/verify_gpsdo_lock.py --device /dev/ttyUSB0 --threshold 1.0e-9
```
*Expected Output: `{"verdict": "PASS", "locked": true, "allan_dev": <val>}` and exit code 0.*
*Abort: Exit code 1 or `FAIL`.*

*Sign-off: _________*

## Gate 3: Node Agent Start
Start the digital twin agent.
```bash
sudo systemctl start 2mhd-node
sudo systemctl status 2mhd-node
```
*Expected: Service is active (running).*

*Sign-off: _________*

## Gate 4: First Campaign Record
Trigger the first field campaign. Reference [penrose_alpha_checklist.md](penrose_alpha_checklist.md) for full safety limits.
```bash
python3 scripts/record_campaign.py --site penrose_co --duration 3600
```
*Expected: Campaign ID generated, JSONL and HDF5 files written.*

*Sign-off: _________*

## Gate 5: Replay Analysis
Offload data to workstation and run replay analysis.
```bash
python3 scripts/run_replay_analysis.py --campaign <ID>
```
*Expected: Digest matches across runs, event verdicts output.*

*Sign-off: _________*
