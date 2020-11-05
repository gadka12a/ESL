#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.core.display import HTML
HTML(open('../css/custom.css', 'r').read())


# In[2]:


from pygmyhdl import *

@chunk
def pwm_simple(clk_i, pwm_o, threshold):

    cnt = Bus(len(threshold), name='cnt') 
    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold  


# In[3]:


initialize()

clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(3, init_val=3) 
pwm_simple(clk, pwm, threshold)

clk_sim(clk, num_cycles=24)
show_waveforms(start_time=13, tock=True)


# In[4]:


@chunk
def pwm_less_simple(clk_i, pwm_o, threshold, duration):
    
    import math
    length = math.ceil(math.log(duration, 2))
    cnt = Bus(length, name='cnt')
    
    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
        if cnt == duration-1:
            cnt.next = 0

    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold


# In[5]:


initialize()
clk = Wire(name='clk')
pwm = Wire(name='pwm')
pwm_less_simple(clk, pwm, threshold=3, duration=5)
clk_sim(clk, num_cycles=15)
show_waveforms()


# In[6]:


initialize()
clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(4, name='threshold')
pwm_less_simple(clk, pwm, threshold, 10)

def test_bench(num_cycles):
    clk.next = 0
    threshold.next = 3  
    yield delay(1)
    for cycle in range(num_cycles):
        clk.next = 0
        if cycle >= 14:
            threshold.next = 8
        yield delay(1)
        clk.next = 1
        yield delay(1)

simulate(test_bench(20))
show_waveforms(tick=True, start_time=19)


# In[7]:


@chunk
def pwm_glitchless(clk_i, pwm_o, threshold, interval):
    import math
    length = math.ceil(math.log(interval, 2))
    cnt = Bus(length)
    
    threshold_r = Bus(length, name='threshold_r')
    
    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
        if cnt == interval-1:
            cnt.next = 0
            threshold_r.next = threshold
        
    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold_r


# In[8]:


initialize()
clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(4, name='threshold')
pwm_glitchless(clk, pwm, threshold, 10)

simulate(test_bench(22))
show_waveforms(tick=True, start_time=19)


# In[9]:


#threshold = Bus(8)
#toVerilog(pwm_simple, clk, pwm, threshold)


# In[11]:


toVerilog(pwm_glitchless, clk, pwm, threshold, 227)
get_ipython().system('yosys -q -p "synth_ice40 -blif pwm_glitchless.blif" pwm_glitchless.v')
get_ipython().system('arachne-pnr -d 1k pwm_glitchless.blif -o pwm_glitchless.asc')


# In[12]:


@chunk
def ramp(clk_i, ramp_o):
    '''
    Inputs:
        clk_i: Clock input.
    Outputs:
        ramp_o: Multi-bit amplitude of ramp.
    '''
    
    # Delta is the increment (+1) or decrement (-1) for the counter.
    delta = Bus(len(ramp_o))
    
    @seq_logic(clk_i.posedge)
    def logic():
        # Add delta to the current ramp value to get the next ramp value.
        ramp_o.next = ramp_o + delta
        
        # When the ramp reaches the bottom, set delta to +1 to start back up the ramp.
        if ramp_o == 1:
            delta.next = 1
        
        # When the ramp reaches the top, set delta to -1 to start back down the ramp.
        elif ramp_o == ramp_o.max-2:
            delta.next = -1
            
        # After configuring the FPGA, the delta register is set to zero.
        # Set it to +1 and set the ramp value to +1 to get things going.
        elif delta == 0:
            delta.next = 1
            ramp_o.next = 1


# In[13]:


@chunk
def wax_wane(clk_i, led_o, length):
    rampout = Bus(length, name='ramp')  # Create the triangle ramp counter register.
    ramp(clk_i, rampout)  # Generate the ramp.
    pwm_simple(clk_i, led_o, rampout.o[length:length-4]) # Use the upper 4 ramp bits to drive the PWM threshold


# In[14]:


initialize()
clk = Wire(name='clk')
led = Wire(name='led')
wax_wane(clk, led, 6)  # Set ramp counter to 6 bits: 0, 1, 2, ..., 61, 62, 63, 62, 61, ..., 2, 1, 0, ...

clk_sim(clk, num_cycles=180)
t = 110  # Look in the middle of the simulation to see if anything is happening.
show_waveforms(tick=True, start_time=t, stop_time=t+40)


# In[15]:


toVerilog(wax_wane, clk, led, 23)


# In[16]:


with open('wax_wane.pcf', 'w') as pcf:
    pcf.write(
'''
set_io clk_i  21
set_io led_o  99
'''
    )


# In[17]:


get_ipython().system('yosys -q -p "synth_ice40 -blif wax_wane.blif" wax_wane.v')
get_ipython().system('arachne-pnr -q -d 1k -p wax_wane.pcf wax_wane.blif -o wax_wane.asc')
get_ipython().system('icepack wax_wane.asc wax_wane.bin')
get_ipython().system('iceprog wax_wane.bin')

