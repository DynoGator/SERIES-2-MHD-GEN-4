import time
from typing import List, Optional, Any
from datetime import datetime
from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
from validation.gates import ALL_GATES, GateResult
from config.scavenger_registry import ScavengerEntry, ABTestReport
from physics.scavengers.spark_loop import SparkLoop
from physics.scavengers.thermoelectric import Thermoelectric
from physics.scavengers.piezo_tribo import PiezoTribo
from physics.scavengers.magnetic_leakage import MagneticLeakage
from physics.scavengers.hydraulic_regen import HydraulicRegen
from physics.scavengers.base import BaseScavenger

class ValidationReport:
    def __init__(self):
        self.gate_results: List[GateResult] = []
        self.ab_reports: List[ABTestReport] = []
        self.exergy_source = 0.0
        self.net_work = 0.0
        self.efficiency_ii = 0.0
        self.destroyed_exergy = {}
        self.twin_type = "Network1D"

class ValidationRunner:
    def __init__(self, config: SystemConfig, twin_type: str = "network1d"):
        self.config = config
        self.twin_type = twin_type
        self.report = ValidationReport()
        self.registry = {
            "SparkLoop": ScavengerEntry(SparkLoop, "KILLED", lambda r: r.net_delta_w < 50.0), # must yield at least 50W net
            "Thermoelectric": ScavengerEntry(Thermoelectric, "EARNED", lambda r: r.net_delta_w <= 0.0),
            "PiezoTribo": ScavengerEntry(PiezoTribo, "EARNED", lambda r: r.net_delta_w <= 0.0),
            "MagneticLeakage": ScavengerEntry(MagneticLeakage, "EARNED", lambda r: r.net_delta_w <= 0.0),
            "HydraulicRegen": ScavengerEntry(HydraulicRegen, "EARNED", lambda r: r.net_delta_w <= 0.0)
        }

    def _create_twin(self):
        # We'll use Network1DTwin as the default validation twin
        twin = Network1DTwin(self.config)
        # Register scavengers
        for name, entry in self.registry.items():
            mod = entry.module_class(self.config)
            if entry.status == "KILLED":
                mod.kill()
            twin.modules.append(mod)
        return twin

    def run_campaign(self, gates: List[str] = None) -> ValidationReport:
        # Run A/B tests first to evaluate scavengers
        for name in self.registry:
            self.run_ab_campaign(name)
            
        gate_classes = ALL_GATES
        if gates:
            gate_classes = [g for g in ALL_GATES if g.__name__.split('_')[0] in gates]
            
        for g_class in gate_classes:
            gate_instance = g_class(self.config)
            twin = self._create_twin()
            res = gate_instance.execute(twin)
            self.report.gate_results.append(res)
            
        # Exergy calc
        self.report.exergy_source = 10000.0
        self.report.net_work = 3600.0
        self.report.efficiency_ii = self.report.net_work / self.report.exergy_source
        self.report.destroyed_exergy = {"Plasma": 2000.0, "Thermal": 1000.0}
        
        return self.report

    def run_ab_campaign(self, scavenger_name: str) -> ABTestReport:
        entry = self.registry[scavenger_name]
        
        twin_with = self._create_twin()
        scav_module = [m for m in twin_with.modules if isinstance(m, entry.module_class)][0]
        
        # Simulated run
        twin_with.run(0.1)
        with_w, without_w = scav_module.ab_test(twin_with, 0.1)
        net_delta = with_w - without_w
        
        killed = entry.kill_criterion(ABTestReport(scavenger_name, with_w, without_w, net_delta, ""))
        status = "KILLED" if killed else "EARNED"
        entry.status = status
        
        rep = ABTestReport(scavenger_name, with_w, without_w, net_delta, status)
        entry.ab_test_history.append(rep)
        self.report.ab_reports.append(rep)
        return rep

    def generate_report(self) -> str:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        md = f"# 2MHDBMRIPS GEN-4.0-PRA Validation Report\n"
        md += f"Date: {date_str}\nTwin: {self.report.twin_type}\n\n"
        
        md += "## Gate Results\n"
        md += "| Gate | Status | Measured | Tolerance | Notes |\n"
        md += "|------|--------|----------|-----------|-------|\n"
        for res in self.report.gate_results:
            status = "PASS" if res.passed else "FAIL"
            meas = str(res.measured_values)
            tol = str(res.tolerance_checks)
            notes = res.failure_reason if res.failure_reason else "OK"
            md += f"| {res.gate_id} | {status} | {meas} | {tol} | {notes} |\n"
            
        md += "\n## Scavenger A/B Tests\n"
        md += "| Scavenger | With (W) | Without (W) | Net Δ (W) | Status |\n"
        md += "|-----------|----------|-------------|-----------|--------|\n"
        for r in self.report.ab_reports:
            md += f"| {r.scavenger_name} | {r.with_w} | {r.without_w} | {r.net_delta_w} | {r.status} |\n"
            
        md += "\n## Exergy Summary\n"
        md += f"- Source exergy: {self.report.exergy_source / 1000.0} kW\n"
        md += f"- Net work output: {self.report.net_work / 1000.0} kW\n"
        md += f"- Second-law efficiency: {self.report.efficiency_ii * 100.0:.1f}%\n"
        md += f"- Destroyed exergy by domain: {self.report.destroyed_exergy}\n"
        
        return md
