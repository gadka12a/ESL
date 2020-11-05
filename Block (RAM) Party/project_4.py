#!/usr/bin/env python
# coding: utf-8

# In[2]:



def print_stats(yosys_log):
    stat_start_line = yosys_log.grep(r'^2\.27\. ')
    stat_end_line = yosys_log.grep(r'^2\.28\. ')
    start_index = yosys_log.index(stat_start_line[0])
    end_index = yosys_log.index(stat_end_line[0])
    print('\n'.join(yosys_log[start_index+2:end_index-1]))


# In[3]:


from pygmyhdl import *

@chunk
def ram(clk_i, en_i, wr_i, addr_i, data_i, data_o):
    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    

    @seq_logic(clk_i.posedge)
    def logic():
        if en_i:

            if wr_i:
                mem[addr_i.val].next = data_i
            else:
                data_o.next = mem[addr_i.val]


# In[4]:


initialize() 
clk = Wire(name='clk')
en = Wire(name='en')
wr = Wire(name='wr')
addr = Bus(8, name='addr')
data_i = Bus(8, name='data_i')
data_o = Bus(8, name='data_o')


ram(clk_i=clk, en_i=en, wr_i=wr, addr_i=addr, data_i=data_i, data_o=data_o)

def ram_test_bench():
    '''RAM test bench: write 10 values to RAM, then read them back.'''
    
    en.next = 1  

    wr.next = 1  
    for i in range(10):
        addr.next = i            
        data_i.next = 3 * i + 1 
        

        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)


    wr.next = 0  
    for i in range(10):
        addr.next = i   

        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

simulate(ram_test_bench())

show_text_table('en clk wr addr data_i data_o')


# In[5]:


#toVerilog(ram, clk_i=Wire(), en_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))


# In[6]:


#print_stats(log)   


# In[7]:


@chunk
def ram(clk_i,wr_i, addr_i, data_i, data_o):
    
    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[addr_i.val].next = data_i
        else:
            data_o.next = mem[addr_i.val]
                
#toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))
#print_stats(log)


# In[8]:


@chunk
def simpler_ram(clk_i,wr_i, addr_i, data_i, data_o):

    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[addr_i.val].next = data_i
        data_o.next = mem[addr_i.val]
                
#toVerilog(simpler_ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))
#print_stats(log)


# This reduces the resource usage by a single LUT:

# In[9]:


@chunk
def dualport_ram(clk_i, wr_i, wr_addr_i, rd_addr_i, data_i, data_o):

    mem = [Bus(len(data_i)) for _ in range(2**len(wr_addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[wr_addr_i.val].next = data_i
        data_o.next = mem[rd_addr_i.val]


# In[10]:


initialize()

clk = Wire(name='clk')
wr = Wire(name='wr')
wr_addr = Bus(8, name='wr_addr') 
rd_addr = Bus(8, name='rd_addr') 
data_i = Bus(8, name='data_i')
data_o = Bus(8, name='data_o')

dualport_ram(clk_i=clk, wr_i=wr, wr_addr_i=wr_addr, rd_addr_i=rd_addr, data_i=data_i, data_o=data_o)

def ram_test_bench():
    for i in range(10): 
        
        wr_addr.next = i
        data_i.next = 3 * i + 1
        wr.next = 1

        rd_addr.next = i - 3
        
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

simulate(ram_test_bench())

show_text_table('clk wr wr_addr data_i rd_addr data_o')


# In[11]:


#toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(9), data_i=Bus(10), data_o=Bus(10))
#print_stats(log)


# In[12]:


#toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(7), data_i=Bus(24), data_o=Bus(24))
#print_stats(log)


# In[13]:


#toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(9), data_i=Bus(24), data_o=Bus(24))
#print_stats(log)


# In[14]:


@chunk
def gen_reset(clk_i, reset_o):
    '''
    Generate a reset pulse to initialize everything.
    Inputs:
        clk_i:   Input clock.
    Outputs:
        reset_o: Active-high reset pulse.
    '''
    cntr = Bus(1) 
    
    @seq_logic(clk_i.posedge)
    def logic():
        if cntr < 1:

            cntr.next = cntr.next + 1
            reset_o.next = 1
        else:

            reset_o.next = 0

@chunk
def sample_en(clk_i, do_sample_o, frq_in=12e6, frq_sample=100):

    from math import ceil, log2
    rollover = int(ceil(frq_in / frq_sample)) - 1
    cntr = Bus(int(ceil(log2(frq_in/frq_sample))))

    @seq_logic(clk_i.posedge)
    def counter():
        cntr.next = cntr + 1     
        do_sample_o.next = 0      
        if cntr == rollover:
            do_sample_o.next = 1
            cntr.next = 0 

@chunk
def record_play(clk_i, button_a, button_b, leds_o):

    reset = Wire()
    gen_reset(clk_i, reset)

    do_sample = Wire()
    sample_en(clk_i, do_sample)

    wr = Wire()
    addr = Bus(11)
    end_addr = Bus(len(addr)) 
    data_i = Bus(1)
    data_o = Bus(1)
    ram(clk_i, wr, addr, data_i, data_o)

    state = Bus(3)     
    INIT = 0             
    WAITING_TO_RECORD = 1 
    RECORDING = 2      
    WAITING_TO_PLAY = 3 
    PLAYING = 4


    @seq_logic(clk_i.posedge)
    def fsm():
        
        wr.next = 0  
        
        if reset:
            state.next = INIT
            
        elif do_sample:
        
            if state == INIT:
                leds_o.next = 0b10101 
                if button_a == 1:

                    state.next = WAITING_TO_RECORD
                    
            elif state == WAITING_TO_RECORD:
                leds_o.next = 0b11010 
                if button_a == 0:
                    addr.next = 0       
                    data_i.next = button_b  
                    wr.next = 1            
                    state.next = RECORDING 
                    
            elif state == RECORDING: 
                addr.next = addr + 1  
                data_i.next = button_b  
                wr.next = 1           
                leds_o.next = concat(1,button_b, button_b, button_b, button_b)
                if button_a == 1:
                    end_addr.next = addr+1
                    state.next = WAITING_TO_PLAY 
                    
            elif state == WAITING_TO_PLAY:
                leds_o.next = 0b10000  
                if button_a == 0:
                    addr.next = 0        
                    state.next = PLAYING  
                    
            elif state == PLAYING: 
                leds_o.next = concat(1,data_o[0],data_o[0],data_o[0],data_o[0])
                addr.next = addr + 1 
                if addr == end_addr:
                    addr.next = 0
                if button_a == 1:
                    state.next = WAITING_TO_RECORD


# In[15]:


toVerilog(record_play, clk_i=Wire(), button_a=Wire(), button_b=Wire(), leds_o=Bus(5))


# ## Summary
# 
# Once again, you've made it to the end of another ~~beating~~ tutorial.
# While battle-scarred and weary, your labors have earned you these treasures:
# 
# * How to write MyHDL that Yosys can recognize as a block RAM.
# 
# * How to read from and write to a RAM.
# 
# * How to create RAMs with various word widths and number of memory locations.
# 
# * How RAMs of different sizes are mapped into the fixed-size iCE40 BRAMs.
