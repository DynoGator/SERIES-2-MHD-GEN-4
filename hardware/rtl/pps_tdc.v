module pps_tdc (
    input wire clk,
    input wire rst,
    input wire pps_in,
    output reg [63:0] tdc_count
);
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            tdc_count <= 64'd0;
        end else if (pps_in) begin
            tdc_count <= tdc_count + 1;
        end
    end
endmodule
