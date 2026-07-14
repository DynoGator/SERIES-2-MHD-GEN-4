import os
from typing import List

class VivadoBuild:
    def __init__(self, project_name: str = "mhd_fpga_top", part: str = "xc7z020clg400-1"):
        self.project_name = project_name
        self.part = part
        self.sources = []
        self.constraints = []
        self.strategy = "Performance_Explore"

    def add_rtl_sources(self, sources: List[str]) -> None:
        self.sources.extend(sources)

    def add_constraints(self, xdc_path: str) -> None:
        self.constraints.append(xdc_path)

    def set_build_strategy(self, strategy: str = "Performance_Explore") -> None:
        self.strategy = strategy

    def generate_tcl(self, output_path: str) -> None:
        tcl = [
            f"create_project {self.project_name} ./build -part {self.part} -force",
            f"set_property board_part myboard:1.0 [current_project]" # generic stub
        ]
        
        for src in self.sources:
            tcl.append(f"add_files {src}")
            
        for xdc in self.constraints:
            tcl.append(f"read_xdc {xdc}")
            
        tcl.append("update_compile_order -fileset sources_1")
        
        tcl.append(f"set_property strategy {self.strategy} [get_runs impl_1]")
        
        tcl.append("launch_runs synth_1 -jobs 4")
        tcl.append("wait_on_run synth_1")
        tcl.append("launch_runs impl_1 -to_step write_bitstream -jobs 4")
        tcl.append("wait_on_run impl_1")
        
        tcl.append(f"write_hw_platform -fixed -include_bit -force -file hw_handoff/{self.project_name}.xsa")
        
        with open(output_path, "w") as f:
            f.write("\n".join(tcl) + "\n")
