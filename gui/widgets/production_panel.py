"""
Phase 8 — Production tab.

Shows BOM summary (top-10 most expensive), cost-to-date vs. target gauge,
regulatory compliance checklist, and a unit serial-number entry field.
"""
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QGroupBox, QFormLayout,
)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class ProductionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        summary = self._load_summary()

        # --- Cost-to-date vs target -----------------------------------------
        cost_box = QGroupBox("Unit Cost vs. Target")
        cost_layout = QVBoxLayout(cost_box)
        target = summary.get("target", 18000)
        total = summary.get("total", 0.0)
        self.cost_label = QLabel(
            f"Unit cost: ${total:,.2f}  /  target ${target:,.0f} "
            f"(band ${summary.get('min', 10000):,}–${summary.get('max', 25000):,})"
        )
        cost_layout.addWidget(self.cost_label)
        self.cost_gauge = QProgressBar()
        self.cost_gauge.setRange(0, int(summary.get("max", 25000)))
        self.cost_gauge.setValue(int(min(total, summary.get("max", 25000))))
        cost_layout.addWidget(self.cost_gauge)
        layout.addWidget(cost_box)

        # --- BOM top-10 ------------------------------------------------------
        bom_box = QGroupBox("Bill of Materials — Top 10 by Cost")
        bom_layout = QVBoxLayout(bom_box)
        self.bom_table = QTableWidget()
        items = summary.get("top_items", [])
        self.bom_table.setColumnCount(3)
        self.bom_table.setHorizontalHeaderLabels(["Item", "Line $", "Lead (wk)"])
        self.bom_table.setRowCount(len(items))
        for row, it in enumerate(items):
            self.bom_table.setItem(row, 0, QTableWidgetItem(str(it["name"])))
            self.bom_table.setItem(row, 1, QTableWidgetItem(f"${it['line_cost_usd']:,.2f}"))
            self.bom_table.setItem(row, 2, QTableWidgetItem(f"{it['lead_time_weeks']:.0f}"))
        bom_layout.addWidget(self.bom_table)
        layout.addWidget(bom_box)

        # --- Compliance checklist -------------------------------------------
        comp_box = QGroupBox("Regulatory Compliance")
        comp_layout = QHBoxLayout(comp_box)
        self.chk_fcc = QCheckBox("FCC")
        self.chk_ce = QCheckBox("CE")
        self.chk_ul = QCheckBox("UL")
        for c in (self.chk_fcc, self.chk_ce, self.chk_ul):
            comp_layout.addWidget(c)
        layout.addWidget(comp_box)

        # --- Serial number ---------------------------------------------------
        serial_box = QGroupBox("Unit Identity")
        serial_form = QFormLayout(serial_box)
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("e.g. 2MHD-PRA-0001")
        serial_form.addRow("Serial number:", self.serial_input)
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("e.g. BATCH-2026-07")
        serial_form.addRow("Batch number:", self.batch_input)
        layout.addWidget(serial_box)

    def compliance_status(self) -> dict:
        return {
            "fcc": self.chk_fcc.isChecked(),
            "ce": self.chk_ce.isChecked(),
            "ul": self.chk_ul.isChecked(),
        }

    def _load_summary(self) -> dict:
        """Best-effort load; the GUI must never crash if the BOM is absent."""
        try:
            from config.materials_db import BOMGenerator
            gen = BOMGenerator(
                materials_db_path=os.path.join(_ROOT, "config", "materials_db.yaml"),
                cost_model_path=os.path.join(_ROOT, "config", "cost_model.yaml"),
            )
            cost = gen.get_cost_summary()
            bom = gen.generate_bom(1)
            import yaml
            with open(os.path.join(_ROOT, "config", "cost_model.yaml")) as f:
                target = yaml.safe_load(f)["unit_cost_target_usd"]
            top = sorted(bom["items"], key=lambda x: x["line_cost_usd"], reverse=True)[:10]
            return {
                "total": cost["total"],
                "target": target["target"],
                "min": target["min"],
                "max": target["max"],
                "top_items": top,
            }
        except Exception:
            return {"total": 0.0, "target": 18000, "min": 10000, "max": 25000, "top_items": []}
