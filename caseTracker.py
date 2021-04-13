#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/tugangui/caseTracker/blob/main/caseTracker.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[4]:


#@title
import pandas as pd
import numpy as np
import sys

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.discovery import build

OUTPUT_PATH = sys.argv[1]

def pull_sheet_data(SCOPES,SPREADSHEET_ID,RANGE_NAME):
    creds = gsheet_api_check(SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
    else:
        rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                  range=RANGE_NAME).execute()
        data = rows.get('values')
        print("COMPLETE: Data copied")
        return data

def gsheet_api_check(SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)    
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  

            with open('token.pickle', 'wb') as token:
              pickle.dump(creds, token)
              
    return creds


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1N3Hokc0vnnnVNJdbYiLleEjnS0T0zPEXiMjWxpdZKXw'

def parseSheetData(tab, columns_row, columns_length):
  print(tab)
  data = pull_sheet_data(SCOPES, SPREADSHEET_ID, tab)
  columns = data[columns_row]
  test = columns_row+1
  if(columns_length):
    for row in range(test, len(data)):
      for x in range(len(data[row]), columns_length):
        data[row].append('')

  return pd.DataFrame(data[test:], columns=columns)

U01 = parseSheetData('U01 ', 9, None)
U19_Salk = parseSheetData('U19 Salk Institute', 6, 30)
U19_CSHL = parseSheetData('U19 CSHL', 8, 30)
MCP = parseSheetData('MCP', 7, 30)
bg = parseSheetData('Basal Ganglia', 6, 28)
RF1 = parseSheetData('RF1 (HPF)', 14, 29)
BLA = parseSheetData('BLA project', 4, 29)

SURGEON_COLS = [9,7,8,8,7,7,8]

tabs = [U01, U19_Salk, U19_CSHL, MCP, bg, RF1, BLA]

distinctCases = pd.DataFrame()
tracersPathways = pd.DataFrame()
actualInjections = pd.DataFrame()
distinctCasesSurgeons = pd.DataFrame()

i=0

for index, tab in enumerate(tabs):
  s = SURGEON_COLS[index]
  casesSurgeons = tab.iloc[: , [1, s]].copy() 
  casesSurgeons.columns = ['Case', 'Surgeon']
  casesSurgeons = casesSurgeons.dropna()
  casesSurgeons = casesSurgeons.drop_duplicates(subset='Case', keep='first')
  casesSurgeons = casesSurgeons[casesSurgeons['Case'].str.startswith('S')]
  casesSurgeons['length']= (casesSurgeons['Case']).str.len()
  casesSurgeons = casesSurgeons[(casesSurgeons.length>=11) & (casesSurgeons.length<=13)] # some cases have asterisks?

  cases = pd.DataFrame(tab.iloc[:, 1].unique()) # Distinct cases
  cases = cases.applymap(str)
  cases = cases.loc[cases[0].str.startswith('S')]
  cases['length']= (cases[0]).str.len()
  cases = cases[(cases.length>=11) & (cases.length<=13)] # some cases have asterisks?

  tracers = pd.DataFrame(tab.iloc[:, 3]) # total tracers
  tracers['length']= (tracers['Tracers used']).str.len()
  tracers = tracers[(tracers.length>1)] # filter out blank entries

  if(s==0 or s==6):
      injections = pd.DataFrame(tab.iloc[:, 5]) # total injections
  else:
      injections = pd.DataFrame(tab.iloc[:, 4]) # total injections
  mapping = {injections.columns[0]:'0'}
  injections = injections.rename(columns=mapping)
  injections['length']= (injections['0']).str.len()
  injections = injections[(injections.length>1)] # filter out blank entries

  distinctCases = distinctCases.append(cases)
  tracersPathways = tracersPathways.append(tracers)
  actualInjections = actualInjections.append(injections)
  distinctCasesSurgeons = distinctCasesSurgeons.append(casesSurgeons)
  i += 1

distinctCasesSurgeons['Case'] = distinctCasesSurgeons['Case'].str.slice(stop=11)

def createFiles(data, name):
  data = data.dropna()
  if(name=='distinctCases'):
    data = pd.DataFrame(data.iloc[:, 0].unique())
  else:
    data = pd.DataFrame(data.iloc[:, 0])
  data.index = data.index + 1
  pd.DataFrame(data).to_csv(OUTPUT_PATH +'/'+name+'.csv', header=False, index=False)
  print('\n' + OUTPUT_PATH + '/'+name+'.csv')
  print('name: '+ str(data.size))

createFiles(distinctCases, 'distinctCases')
createFiles(tracersPathways, 'tracersPathways')
createFiles(actualInjections, 'actualInjections')

def get_organism_id(argument):
    switcher = {
        'SG': 7,
        'SP': 17,
        'SV': 18
    }
    return switcher.get(argument, 1)

cases = pd.Series(distinctCases.iloc[:,0])
f = open(OUTPUT_PATH + "/casetracker.sql", "w")

query = "INSERT IGNORE INTO organisms (id, species, strain, allele_type, gene_marker, description, code) VALUES (17, 'mouse', 'Parvalbumin-Cre', 'transgenic', 'Parvalbumin (PV)', 'These mice selectively express Cre recombinase in PV expressing cells', 'P');\n"
query = query + "INSERT IGNORE INTO organisms (id, species, strain, allele_type, gene_marker, description, code) VALUES (18, 'mouse', 'Vasoactive Intestinal Peptide-Cre', 'transgenic', 'Vasoactive Intestinal Peptide (VIP)', 'These mice selectively express Cre recombinase in VIP expressing cells', 'P');\n"
query = query + "INSERT INTO users(user_name, email, user_group, is_active) VALUES('Lei Gao', 'LeiGao@mednet.ucla.edu',4, 1 )ON DUPLICATE KEY UPDATE email='LeiGao@mednet.ucla.edu';\n"

#insert into animals + tissueDissections
for row in distinctCasesSurgeons.itertuples(index=False):
    casePrefix = get_organism_id(row[0][:2])
    query = query + "INSERT INTO animals (organism_id) SELECT " + str(casePrefix) + " FROM tissueDissections WHERE NOT EXISTS(SELECT NULL FROM tissueDissections td WHERE td.tissue_code='" + row[0] + "') LIMIT 1;\n"
    query = query + "INSERT IGNORE INTO tissueDissections (tissue_code, tissue_name, description, animal_id) VALUES ('" + row[0] +"', 'brain', 'brain', LAST_INSERT_ID());\n"

# insert into surgeries
#Lin, Lei, Marlene, Kevin
def usernames(argument):
    switcher = {
        'Monica': "Monica Song",
        'Lei': "Lei Gao",
        'Marlene': "Marlene Becerra"
    }
    return switcher.get(argument, "Lin Gou")

for row in distinctCasesSurgeons.itertuples(index=False):
    username = usernames(row[1].strip())
    query = query + "\nINSERT INTO surgeries (user_id, animal_id, tissue_dissection_id) SELECT (select id from users where user_name='" + username + "') as user_id, (select animal_id from tissueDissections where tissue_code='" + row[0] + "') as animal_id, (select id FROM tissueDissections WHERE tissue_code='" + row[0] + "') as tissue_code from surgeries WHERE NOT EXISTS(SELECT s.tissue_dissection_id FROM surgeries s INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='" + row[0] + "') LIMIT 1;"

f.write(query)
f.close()

