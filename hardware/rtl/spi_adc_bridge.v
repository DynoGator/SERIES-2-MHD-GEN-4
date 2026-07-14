module spi_adc_bridge (
    input wire clk,
    input wire rst,
    output wire mosi,
    input wire miso,
    output wire sck,
    output wire cs_n
);
    assign mosi = 1'b0;
    assign sck = clk;
    assign cs_n = 1'b1;
endmodule
