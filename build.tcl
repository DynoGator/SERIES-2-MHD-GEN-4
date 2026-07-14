create_project mhd_fpga_top ./build -part xc7z020clg400-1 -force
set_property board_part myboard:1.0 [current_project]
add_files rtl/pps_tdc.v
add_files rtl/phase_controller.v
add_files rtl/spi_adc_bridge.v
add_files rtl/top.v
read_xdc constraints/mhd_fpga.xdc
update_compile_order -fileset sources_1
set_property strategy Performance_Explore [get_runs impl_1]
launch_runs synth_1 -jobs 4
wait_on_run synth_1
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
write_hw_platform -fixed -include_bit -force -file hw_handoff/mhd_fpga_top.xsa
