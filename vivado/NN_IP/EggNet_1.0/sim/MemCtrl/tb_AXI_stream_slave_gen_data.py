# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:37:54 2019

@author: lukas

Generates random test data to test AXI stream slave interface of memory 
controller and test the module using ghdl 
"""

# %% public imports
import os 
import shutil

# %% import custom modules
import vhdl_testbench as tb 

# %% parameter
KEEP_TEMPORARY_FILES = True
BLOCK_SIZE = 28*28
NUMBER_OF_TEST_BLOCKS = 3

# %% create tmp folder, delete folder if not tmp exists and create new one
if os.path.isdir('tmp'):
    shutil.rmtree('tmp')
    
try : os.mkdir('tmp')
except : print("Error creating tmp folder!")

# %% create test data file

random_data = tb.gen_testdata(BLOCK_SIZE,NUMBER_OF_TEST_BLOCKS)
             
# %% run ghdl 
# Saving console ouput in log file is not working on windows            
tb.run_ghdl_win(("..\..\hdl\EggNet_v1_0_S00_AXIS.vhd","tb_AXI_stream_slave.vhd"),"tb_EggNet_v1_0_S00_AXIS")


# %% check results 
error_count = 0

for i in range(NUMBER_OF_TEST_BLOCKS):
    with open("tmp/results{}.txt".format(i+1),"r") as f:
        for j in range(2*BLOCK_SIZE):
            block_select = 1-(i+1)%2
            result_data = int(f.readline())
            if block_select == 0 and j<BLOCK_SIZE:
                 if result_data != random_data[i,j]:
                     print("Error in block {}".format(i+1) + " in line {} ,".format(j+block_select*BLOCK_SIZE) \
                            + "{}".format(result_data) + " != {}".format(random_data[i,j]))
                     error_count += 1
            elif block_select == 0 and j>=BLOCK_SIZE and i==0:
                if result_data != 0:
                     print("Error in block {}".format(i+1) + " in line {} ,".format(j+block_select*BLOCK_SIZE) \
                            + "{}".format(result_data) + " != {}".format(0))
                     error_count += 1
            elif block_select == 0 and j>=BLOCK_SIZE:
                if result_data != random_data[i-1,j-BLOCK_SIZE]:
                     print("Error in block {}".format(i+1) + " in line {} ,".format(j+block_select*BLOCK_SIZE) \
                            + "{}".format(result_data) + " != {}".format(random_data[i-1,j-BLOCK_SIZE]))
                     error_count += 1           
            elif block_select == 1 and j<BLOCK_SIZE:
                 if result_data != random_data[i-1,j]:
                     print("Error in block {}".format(i+1) + " in line {} ,".format(j+block_select*BLOCK_SIZE) \
                            + "{}".format(result_data) + " != {}".format(random_data[i-1,j]))
                     error_count += 1
            elif block_select == 1 and j>=BLOCK_SIZE:
                if result_data != random_data[i,j-BLOCK_SIZE]:
                     print("Error in block {}".format(i+1) + " in line {} ,".format(j+block_select*BLOCK_SIZE) \
                            + "{}".format(result_data) + " != {}".format(random_data[i,j-BLOCK_SIZE]))
                     error_count += 1   
            else:
                    print("Error in porgram")
                    
if error_count == 0:
    print("Test completed successfully!")
else:
    print("{} errors occured".format(error_count))    
# %% delete tmp folder 
if not KEEP_TEMPORARY_FILES and error_count == 0:
    shutil.rmtree('tmp')
