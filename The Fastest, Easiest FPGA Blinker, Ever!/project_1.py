import pygmyhdl

initialize()


@chunk
def blinker(clk_i, led_o, length):
    cnt = Bus(length, name='cnt')

    @seq_logic(clk_i.posedge)
    def counter_logic():
        cnt.next = cnt + 1

    @comb_logic
    def output_logic():
        led_o.next = cnt[length - 1]