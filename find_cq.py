# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 11:15:58 2022

@author: Carolyn Elya
"""
import pandas as pd

# from https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python
import tkinter as tk
from tkinter import filedialog as fd

## prevent GUI elements downstream of file choice dialog from tkinter from displaying (slight convenience)
root = tk.Tk()
root.withdraw()

# ask for path of qPCR data > pick .pcrd file within directory
qPCR_pcrd = fd.askopenfilename()

# Figure out name of csv file with data (so you don't have to remember which output to use!)
qPCR_pre= qPCR_pcrd.split('.pcrd')

#qPCR_results = qPCR_pre[0] + ' -  Quantification Amplification Results_SYBR.csv'
qPCR_results = qPCR_pre[0] + ' -  Quantification Amplification Results.xlsx'
qPCR_output = qPCR_pre[0] + '-Cq values.csv'

# Open a new output file to write results to
hOut = open(qPCR_output,'w')
hOut.write('Well,Cq\n')

# Read in qPCR data to pandas dataframe
#qData = pd.read_csv(qPCR_results)
qData = pd.read_excel(qPCR_results)

# Find qDf [slope] (difference between cycles for each well)
qDf = qData.diff()

# Find qDDF [slope of slope] (difference between slopes for each well)
qDDf = qDf.diff()

# Determine whether value of each qDDf is negative (False) or positive (True)
qDDf_tf = qDDf > 0

# Establish the pattern we want to find in qDDf. Cq occurs somewhere between the last cycle where qDDf > 0 and first cycle where qDDF < 0
pattern = [True,True,True,False,False,False]

# For each well in data (which corresponds to each column in pandas dataframe)...
for j in range (2,qData.shape[1]):
    
    # findVal indicates if we've encountered a Cq. Set to 0 at the start of checking each column
    findVal = 0
    
    # We're going to look for the pattern of three positive slopes of slopes followed by three negative
    for i in range(len(pattern),len(qDDf)+1):
        
        # If we find this, we will figure out cq by finding precise point of inflection between cycles 
        #(averaging between two slopes of slopes and adding to first cycle #)
        if all(qDDf_tf[qData.columns[j]][i-len(pattern):i] == pattern) and not findVal:
            cq = (qDDf[qData.columns[j]][i-3]/(qDDf[qData.columns[j]][i-3] - qDDf[qData.columns[j]][i-4]))+i-3
            
            # Write this value to csv file
            hOut.write('%s,%.2f\n' %(qData.columns[j],cq))
            
            # Indicate that we've found our Cq
            findVal = 1
        
        # If we've reached the last cycle and haven't found our Cq, spit out "NaN" as Cq value in csv file
        elif i==len(qDDf) and not findVal:
            hOut.write('%s,NaN\n' %(qData.columns[j]))

# Close csv file, so you can open it :) 
hOut.close()

