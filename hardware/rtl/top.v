module top (
    input wire clk_in,
    input wire rst_in,
    input wire pps_in
);
    wire [63:0] tdc_val;
    pps_tdc tdc_inst (
        .clk(clk_in),
        .rst(rst_in),
        .pps_in(pps_in),
        .tdc_count(tdc_val)
    );
endmodule
