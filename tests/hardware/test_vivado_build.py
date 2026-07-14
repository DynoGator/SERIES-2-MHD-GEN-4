import pytest
import os
from hardware.vivado_build import VivadoBuild

def test_tcl_generated(tmp_path):
    build = VivadoBuild()
    tcl_path = os.path.join(tmp_path, "build.tcl")
    build.generate_tcl(tcl_path)
    
    assert os.path.exists(tcl_path)
    with open(tcl_path, "r") as f:
        content = f.read()
        assert "create_project" in content

def test_rtl_sources_in_tcl(tmp_path):
    build = VivadoBuild()
    build.add_rtl_sources(["rtl/top.v"])
    tcl_path = os.path.join(tmp_path, "build.tcl")
    build.generate_tcl(tcl_path)
    
    with open(tcl_path, "r") as f:
        content = f.read()
        assert "add_files rtl/top.v" in content

def test_constraints_in_tcl(tmp_path):
    build = VivadoBuild()
    build.add_constraints("constraints/mhd.xdc")
    tcl_path = os.path.join(tmp_path, "build.tcl")
    build.generate_tcl(tcl_path)
    
    with open(tcl_path, "r") as f:
        content = f.read()
        assert "read_xdc constraints/mhd.xdc" in content

def test_build_strategy_set(tmp_path):
    build = VivadoBuild()
    build.set_build_strategy("Performance_Explore")
    tcl_path = os.path.join(tmp_path, "build.tcl")
    build.generate_tcl(tcl_path)
    
    with open(tcl_path, "r") as f:
        content = f.read()
        assert "set_property strategy Performance_Explore" in content
