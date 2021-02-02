#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/tugangui/caseTracker/blob/main/caseTracker.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[4]:


#@title
import pandas as pd
import numpy as np

xls = "/content/Copy of Hongwei Dong lab case tracker.xlsx"
U01 = pd.read_excel(xls, 'U01 ')
U19_Salk = pd.read_excel(xls, 'U19 Salk Institute')
U19_CSHL = pd.read_excel(xls, 'U19 CSHL')
MCP = pd.read_excel(xls, 'MCP')
bg = pd.read_excel(xls, 'Basal Ganglia')
RF1 = pd.read_excel(xls, 'RF1 (HPF)')
BLA = pd.read_excel(xls,'BLA project')

tabs = [U01, U19_Salk, U19_CSHL, MCP, bg, RF1, BLA]

distinctCases = pd.DataFrame()
tracersPathways = pd.DataFrame()
actualInjections = pd.DataFrame()

for tab in tabs:
  
  cases = pd.DataFrame(tab.iloc[:, 1].unique()) # Distinct cases
  cases = cases.applymap(str)
  cases = cases.loc[cases[0].str.startswith('S')]
  cases['length']= (cases[0]).str.len()
  cases = cases[(cases.length>=11) & (cases.length<=13)] # some cases have asterisks?
  tracers = pd.DataFrame(tab.iloc[:, 3]) # total
  injections = pd.DataFrame(tab.iloc[:, 4]) # total

  distinctCases = distinctCases.append(cases)
  tracersPathways = tracersPathways.append(tracers)
  actualInjections = actualInjections.append(injections)

tracersPathways = tracersPathways.dropna()
actualInjections = actualInjections.dropna()
distinctCases = distinctCases.dropna()

distinctCases = pd.DataFrame(distinctCases.iloc[:,0].unique())
distinctCases.index = distinctCases.index + 1
distinctCases.to_csv('/distinctCases.csv', header=False)
print('Distinct cases: ' + str(distinctCases.iloc[:, 0].unique().size))

tracersPathways = tracersPathways.iloc[:, 0]
tracersPathways.index = tracersPathways.index + 1
pd.DataFrame(tracersPathways).to_csv('/tracersPathways.csv', header=False)
print('Total pathways: ' + str(tracersPathways.size))

pd.DataFrame(actualInjections.iloc[:, 0]).to_csv('/actualInjections.csv')
print('Total injections: ' + str(actualInjections.size))

