#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.core.display import HTML
HTML(open('../css/custom.css', 'r').read())


# In[2]:


from pygmyhdl import *

@chunk
def dff(clk_i, d_i, q_o):

    @seq_logic(clk_i.posedge)
    def logic():
        q_o.next = d_i


# In[3]:


@chunk
def register(clk_i, d_i, q_o):
    for k in range(len(d_i)):
        dff(clk_i, d_i.o[k], q_o.i[k])


# In[4]:


initialize()

clk = Wire(name='clk')
data_in = Bus(8, name='data_in')
data_out = Bus(8, name='data_out')

register(clk_i=clk, d_i=data_in, q_o=data_out)

from random import randint
def test_bench():
    for i in range(10):
        data_in.next = randint(0,256)
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

simulate(test_bench())

show_waveforms()


# In[5]:


@chunk
def full_adder_bit(a_i, b_i, c_i, s_o, c_o):

    @comb_logic
    def logic():
        s_o.next = a_i ^ b_i ^ c_i
        c_o.next = (a_i & b_i) | (a_i & c_i) | (b_i & c_i)


# In[6]:


initialize()

a_i, b_i, c_i = Wire(name='a_i'), Wire(name='b_i'), Wire(name='c_i')
sum_o, c_o = Wire(name='sum_o'), Wire(name='c_o')

full_adder_bit(a_i, b_i, c_i, sum_o, c_o)

exhaustive_sim(a_i, b_i, c_i)

show_text_table()


# In[7]:


@chunk
def adder(a_i, b_i, s_o):
    c = Bus(len(a_i)+1)
    c.i[0] = 0
    for k in range(len(a_i)):
        full_adder_bit(a_i=a_i.o[k], b_i=b_i.o[k], c_i=c.o[k], s_o=s_o.i[k], c_o=c.i[k+1])


# In[8]:


initialize()  
a = Bus(8, name='a')
b = Bus(8, name='b')
s = Bus(8, name='sum')

adder(a, b, s)
random_sim(a, b, num_tests=20)

show_text_table()


# In[9]:


@chunk
def counter(clk_i, cnt_o):
    
    one = Bus(length, init_val=1)  
    next_cnt = Bus(length)         
    
    adder(one, cnt_o, next_cnt)
    
    register(clk_i, next_cnt, cnt_o)


# In[10]:


@chunk
def blinker(clk_i, led_o, length):

    cnt = Bus(length, name='cnt')
    counter(clk_i, cnt)
    @comb_logic
    def output_logic():
        led_o.next = cnt[length-1]


# In[11]:


initialize()                 
clk = Wire(name='clk')      
led = Wire(name='led')     
blinker(clk, led, 3)         
clk_sim(clk, num_cycles=16) 
show_waveforms()             


# In[ ]:


toVerilog(blinker, clk_i=clk, led_o=led, length=22)


# In[ ]:


print(open('blinker.v').read())

