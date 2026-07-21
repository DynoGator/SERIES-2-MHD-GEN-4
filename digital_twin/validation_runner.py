# MODULE-STATUS: SCAFFOLD
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
            "SparkLoop": ScavengerEntry(SparkLoop, "PROVISIONAL", lambda r: r.net_delta_w < 50.0),
            "Thermoelectric": ScavengerEntry(Thermoelectric, "PROVISIONAL", lambda r: r.net_delta_w <= 0.0),
            "PiezoTribo": ScavengerEntry(PiezoTribo, "PROVISIONAL", lambda r: r.net_delta_w <= 0.0),
            "MagneticLeakage": ScavengerEntry(MagneticLeakage, "PROVISIONAL", lambda r: r.net_delta_w <= 0.0),
            "HydraulicRegen": ScavengerEntry(HydraulicRegen, "PROVISIONAL", lambda r: r.net_delta_w <= 0.0)
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
            
        # Exergy calc (Missing real inputs, so PLACEHOLDER)
        self.report.exergy_source = None
        self.report.net_work = None
        self.report.efficiency_ii = None
        self.report.destroyed_exergy = None
        
        return self.report

    def run_ab_campaign(self, scavenger_name: str) -> ABTestReport:
        entry = self.registry[scavenger_name]
        
        twin_with = self._create_twin()
        for m in twin_with.modules:
            if isinstance(m, entry.module_class):
                m.is_enabled = True
        twin_with.run(0.1)
        with_w = sum(l.power_generated_w - l.power_dissipated_w for l in twin_with.power_ledgers) / max(len(twin_with.power_ledgers), 1)
        
        twin_without = self._create_twin()
        for m in twin_without.modules:
            if isinstance(m, entry.module_class):
                m.kill("AB Test baseline")
        twin_without.run(0.1)
        without_w = sum(l.power_generated_w - l.power_dissipated_w for l in twin_without.power_ledgers) / max(len(twin_without.power_ledgers), 1)
        
        net_delta = with_w - without_w
        
        killed = entry.kill_criterion(ABTestReport(scavenger_name, with_w, without_w, net_delta, ""))
        status = "KILLED" if killed else "PROVISIONAL"
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
            status = res.verdict.name
            meas = str(res.measured_values)
            tol = str(res.tolerance_checks)
            notes = res.reason if res.reason else "OK"
            md += f"| {res.gate_id} | {status} | {meas} | {tol} | {notes} |\n"
            
        md += "\n## Scavenger A/B Tests\n"
        md += "| Scavenger | With (W) | Without (W) | Net Δ (W) | Status |\n"
        md += "|-----------|----------|-------------|-----------|--------|\n"
        for r in self.report.ab_reports:
            md += f"| {r.scavenger_name} | {r.with_w} | {r.without_w} | {r.net_delta_w} | {r.status} |\n"
            
        md += "\n## Exergy Summary\n"
        src = f"{self.report.exergy_source / 1000.0} kW" if self.report.exergy_source is not None else "PLACEHOLDER"
        net = f"{self.report.net_work / 1000.0} kW" if self.report.net_work is not None else "PLACEHOLDER"
        eff = f"{self.report.efficiency_ii * 100.0:.1f}%" if self.report.efficiency_ii is not None else "— (PLACEHOLDER)"
        des = str(self.report.destroyed_exergy) if self.report.destroyed_exergy is not None else "PLACEHOLDER"
        
        md += f"- Source exergy: {src}\n"
        md += f"- Net work output: {net}\n"
        md += f"- Second-law efficiency: {eff}\n"
        md += f"- Destroyed exergy by domain: {des}\n"
        
        return md
