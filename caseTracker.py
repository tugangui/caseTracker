# -*- coding: utf-8 -*-
"""casetracker2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ui22FiyujrquL-QPZerLIcgFrwLKrb5J
"""

import pandas as pd
import numpy as np
import os
import re
import json
from collections import OrderedDict
import sys
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.discovery import build

OUTPUT_PATH = sys.argv[1]
#@title
if os.path.exists(OUTPUT_PATH +"/casetracker.sql"):
  os.remove(OUTPUT_PATH +"/casetracker.sql")

f = open(OUTPUT_PATH +"/casetracker.sql", "a")

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

def parseSheetData(tab):
  print(tab)
  data = pull_sheet_data(SCOPES, SPREADSHEET_ID, tab)
  return pd.DataFrame(data)

output_file = './u19_salk_parsed.json'

# Regex
ID_PATTERN = re.compile(r'[A-Z]{2}[0-9]{6}-[0-9]{2}')
LOCATION_RE = re.compile(r'^[0-9]?\.?\s?([\w +/_\.\'-]+\b)')
COORDINATES_RE = re.compile(r'(\((\+?\-?\d+\.?\d*\,? ?)+\))')
TRACER_RE = re.compile(r'^[0-9]?\.?\s?([\w +/_\.\'-]+\b)')
LAYERS_RE = re.compile(r'L[0-9]')
TWO_REGIONS_RE = re.compile(r'[a-zA-Z]+ *\+ *[a-zA-Z]+')
SAME_AS_RE = re.compile(r'same')

# Values and substitutions
TECHS = ('ru', 'lei', 'lin', 'marlene', 'stanley', 'sarvia', 'nick', 'danny',
         'fernando')
TECHS_ALT = {'sa': 'sarvia'}
THICKNESS = ('50',)
PLANES = ('C',)
PLANES_ALT = {'coronal': 'C', 'c': 'C'}
STRATEGIES = ('TRIO', 'quadruple retrograde', 'triple anterograde',)
STRATEGIES_ALT = {'trio': 'TRIO',
                  'quadruple retrograde': 'quadruple retrograde',
                  'triple anterograde': 'triple anterograde',
                  'quad': 'quadruple retrograde',
                  'triple ant': 'triple anterograde'}

U01_COLS = ("count", "case", "strategy", "tracer", "target", "target2", "adjusted", "actual", 
               "quality", "surgeon", "perfusion_date", "notes", "plane", "thickness", 
               "sectioning_date", "sectioning_tech", "rescan", "immunostained_for", 
               "staining_date", "staining_tech", "mounting_date", "mounting_tech", "img_process",
              "vsi_path", "osp_path", "image_tech", "dimension", "qa_by")

CSHL_COLS = ("count", "case", "strategy", "tracer", "target", "adjusted", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "rescan", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "img_process",
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

U19_COLS = ("count", "case", "strategy", "tracer", "target", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "empty", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "rescan", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "img_process",
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

MCP_COLS = ("count", "case", "strategy", "tracer", "target", "adjusted", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "img_process", "location",
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

BG_COLS = ("count", "case", "strategy", "tracer", "target", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "microscopy", 
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

RF1_COLS = ("count", "case", "strategy", "tracer", "target", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "rescan", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "img_process",
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

BLA_COLS = ("count", "case", "strategy", "tracer", "desired", "target", "actual", "quality",
          "surgeon", "perfusion_date", "notes", "plane", "thickness", "sectioning_date",
          "sectioning_tech", "immunostained_for", "staining_date",
          "staining_tech", "mounting_date", "mounting_tech", "img_process",
          "vsi_path", "osp_path", "image_tech", "dimension", "registration", "threshold",
          "overlap", "qa_by")

COLUMNS = {'U01 ': U01_COLS, 'U19 CSHL': CSHL_COLS, 'U19 Salk Institute': U19_COLS, 'MCP': MCP_COLS, 
           'Basal Ganglia': BG_COLS, 'RF1 (HPF)': RF1_COLS, 'BLA project': BLA_COLS}

SKIPROWS = {'U01 ': 8, 'U19 CSHL': 8, 'U19 Salk Institute': 6, 'MCP': 7,
            'Basal Ganglia': 6, 'RF1 (HPF)': 13, 'BLA project': 4}

f.write('DROP PROCEDURE IF EXISTS update_injectionSitesLocationsARAStructures;')
f.write("\nUPDATE araStructures set abbreviation='SSp-ul_1' where abbreviation='SSp_ul_1';\nUPDATE araStructures set abbreviation='SSp-ul_2/3' where abbreviation='SSp_ul_2/3';\nUPDATE araStructures set abbreviation='SSp-ul_4' where abbreviation='SSp_ul_4';\nUPDATE araStructures set abbreviation='SSp-ul_5' where abbreviation='SSp_ul_5';\nUPDATE araStructures set abbreviation='SSp-ul_6a' where abbreviation='SSp_ul_6a';\nUPDATE araStructures set abbreviation='SSp-ul_6b' where abbreviation='SSp_ul_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSp-bfd_1' where abbreviation='SSp_bfd_1';\nUPDATE araStructures set abbreviation='SSp-bfd_2/3' where abbreviation='SSp_bfd_2/3';\nUPDATE araStructures set abbreviation='SSp-bfd_4' where abbreviation='SSp_bfd_4';\nUPDATE araStructures set abbreviation='SSp-bfd_5' where abbreviation='SSp_bfd_5';\nUPDATE araStructures set abbreviation='SSp-bfd_6a' where abbreviation='SSp_bfd_6a';\nUPDATE araStructures set abbreviation='SSp-bfd_6b' where abbreviation='SSp_bfd_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSp-ll_1' where abbreviation='SSp_ll_1';\nUPDATE araStructures set abbreviation='SSp-ll_2/3' where abbreviation='SSp_ll_2/3';\nUPDATE araStructures set abbreviation='SSp-ll_4' where abbreviation='SSp_ll_4';\nUPDATE araStructures set abbreviation='SSp-ll_5' where abbreviation='SSp_ll_5';\nUPDATE araStructures set abbreviation='SSp-ll_6a' where abbreviation='SSp_ll_6a';\nUPDATE araStructures set abbreviation='SSp-ll_6b' where abbreviation='SSp_ll_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSp-m_1' where abbreviation='SSp_m_1';\nUPDATE araStructures set abbreviation='SSp-m_2/3' where abbreviation='SSp_m_2/3';\nUPDATE araStructures set abbreviation='SSp-m_4' where abbreviation='SSp_m_4';\nUPDATE araStructures set abbreviation='SSp-m_5' where abbreviation='SSp_m_5';\nUPDATE araStructures set abbreviation='SSp-m_6a' where abbreviation='SSp_m_6a';\nUPDATE araStructures set abbreviation='SSp-m_6b' where abbreviation='SSp_m_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSp-n_1' where abbreviation='SSp_n_1';\nUPDATE araStructures set abbreviation='SSp-n_2/3' where abbreviation='SSp_n_2/3';\nUPDATE araStructures set abbreviation='SSp-n_4' where abbreviation='SSp_n_4';\nUPDATE araStructures set abbreviation='SSp-n_5' where abbreviation='SSp_n_5';\nUPDATE araStructures set abbreviation='SSp-n_6a' where abbreviation='SSp_n_6a';\nUPDATE araStructures set abbreviation='SSp-n_6b' where abbreviation='SSp_n_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSp-tr_1' where abbreviation='SSp_tr_1';\nUPDATE araStructures set abbreviation='SSp-tr_2/3' where abbreviation='SSp_tr_2/3';\nUPDATE araStructures set abbreviation='SSp-tr_4' where abbreviation='SSp_tr_4';\nUPDATE araStructures set abbreviation='SSp-tr_5' where abbreviation='SSp_tr_5';\nUPDATE araStructures set abbreviation='SSp-tr_6a' where abbreviation='SSp_tr_6a';\nUPDATE araStructures set abbreviation='SSp-tr_6b' where abbreviation='SSp_tr_6b';")
f.write("\nUPDATE araStructures set abbreviation='SSs-1' where abbreviation='SSs_1';\nUPDATE araStructures set abbreviation='SSs-2/3' where abbreviation='SSs_2/3';\nUPDATE araStructures set abbreviation='SSs-4' where abbreviation='SSs_4';\nUPDATE araStructures set abbreviation='SSs-5' where abbreviation='SSs_5';\nUPDATE araStructures set abbreviation='SSs-6a' where abbreviation='SSs_6a';\nUPDATE araStructures set abbreviation='SSs-6b' where abbreviation='SSs_6b';")
f.write('\ndelimiter $$\ncreate procedure insert_new_structure(structure varchar(255))\nbegin\nIF EXISTS (select id from araStructures where abbreviation COLLATE UTF8_GENERAL_CI LIKE structure)\nTHEN\nupdate araStructures set abbreviation=abbreviation;\nELSE\nINSERT IGNORE INTO araStructures (abbreviation) values(structure);\nEND IF;\nend$$\nDELIMITER ;\n')

def replace_l(ele):
  if ele != "PL":
    return ele.replace("L", "_")
  else:
    return ele

def prepare_df(df):
    '''
        Moves non case id and strategy vals to notes columns, foward fills case and strategy columns
        fills na values as empty strings
        
        assumes no empty cols or rows, and that case_id and strategy name are both on the 
        first row of case rows at least
        ex.
         x  a b c d e f
        c1 s1 # # # # #
              # # # # #
              # # # # #
        c2 s2 @ @ @ @ @ 
              @ @ @ @ @
              @ @ @ @ @
           
        
    '''
    df = df.copy()
    
    if 'count' in df.columns:
        df.drop(columns=['count'], inplace=True)
    
    df['case_col_notes'] = df['case'][~df['case'].str.match(r'[A-Z]{2}[0-9]{6}-[0-9]{2}', na=False)]
    df.loc[~df['case'].str.match(r'[A-Z]{2}[0-9]{6}-[0-9]{2}', na=False), ['case']] = np.nan
    df['case'] = df[['case']].fillna(method='ffill')

    df['trio_col_notes'] = df['strategy'][~df['strategy'].str.match('TRIO', na=False)]
    df.loc[~df['strategy'].str.match('TRIO', na=False), ['strategy']] = np.nan
    df['strategy'] = df[['strategy']].fillna(method='ffill')
    
    df.fillna('', inplace=True)
    
    return df
    

def get_project_dict(df, project):
    for case_id, data in df.iterrows():
        case_id = case_id[0:11]
        # if first row with this case id
        if case_id not in project:
            project[case_id] = {
                'case_name': case_id,
                'notes': data["notes"],
                'surgery': {
                    'planned_for': get_tech(data["surgeon"]),
                    'surgeon': get_tech(data["surgeon"]),
                    'perfusion_date': get_date_or_none(data["perfusion_date"]),
                    'strategy': data["strategy"],
                    'injections': [
                        {
                            "target_loc": get_location(str(data['target'])),
                            "target_coords": get_coordinates(str(data['target'])),
                            "actual_loc": get_location(str(data['actual'])),
                            "actual_coords": get_coordinates(str(data['actual'])),
                            "adjust_loc": "",
                            "adjust_coords": "",
                            "quality": data['quality'],
                            "tracer": {
                                "name": get_tracer(data["tracer"]),
                                "notes": "",
                            }
                        }
                    ]
                },
                'section': {
                    "plane": get_plane(data["plane"]),
                    "thickness": data["thickness"],
                    "sectioning_date": get_date_or_none(data["sectioning_date"]),
                    "sectioning_tech": get_tech(data["sectioning_tech"])
                },
                "stain": {
                    "staining_date": get_date_or_none(data["staining_date"]),
                    "staining_tech": get_tech(data["staining_tech"]),
                    "immunostained_for": data["immunostained_for"]
                },
                "mount": {
                    "mounting_date": get_date_or_none(data["mounting_date"]),
                    "mounting_tech": get_tech(data["mounting_tech"]),
                },
                "image_process": {
                    "vsi_path": data["vsi_path"],
                    "osp_path": data["osp_path"],
                    "image_tech": get_tech(data["image_tech"]),
                    "dimension": data["dimension"],
                    "qa_by": get_tech(data["qa_by"])
                },
                "scan": {
                    "quality": "",
                }
            }
            case_ = project[case_id]

            add_to_notes(case_, data["case_col_notes"])
            add_to_notes(case_, data["trio_col_notes"])

        else:

            case_ = project[case_id]
            case_['surgery']['injections'].append({
                "target_loc": get_location(str(data['target'])),
                "target_coords": get_coordinates(str(data['target'])),
                "actual_loc": get_location(str(data['actual'])),
                "actual_coords": get_coordinates(str(data['actual'])),
                "adjust_loc": "",
                "adjust_coords": "",
                "quality": data['quality'],
                "tracer": {
                    "name": get_tracer(data["tracer"]),
                    "notes": "",
                }
            })
            if data['surgeon'] != '': #surgeons are often on second row (why) and i'm too lazy to fix it
              case_['surgery']['surgeon'] = data['surgeon']

            for prop in ["surgeon", "perfusion_date", "notes", "plane", "thickness", 
                         "sectioning_date","sectioning_tech", "immunostained_for", 
                         "staining_date", "staining_tech", "mounting_date", "mounting_tech", 
                         "vsi_path", "osp_path", "image_tech", "dimension", 
                          "qa_by", "case_col_notes", 
                         "trio_col_notes"]:

                if prop == 'notes':
                    add_to_notes(case_, data[prop])
                else:
                    add_to_notes(case_, data[prop], prefix=prop)
    
    return project


def get_date_or_none(date_string):
    date_comp = date_string.split('/')
    if len(date_comp) == 3:
        return '-'.join([date_comp[2], date_comp[0], date_comp[1]])
    else:
        return None

def get_location(data):
    loc = LOCATION_RE.search(data)
    if loc:
      result = loc.groups(0)[0]
    else:
      result = ''
    result = re.sub('ARA *[0-9]+', '', result)
    result = re.sub('ara', '', result)
    result = re.sub('level', '_', result)
    result = re.sub('Lvl', '_', result)
    result = re.sub(' [0-9]{1,2}', '', result)
    result = re.sub('[0-9]\_[0-9]{1,2}', '', result)
    result = re.sub('^_[0-9]{2}', '', result)
    result = re.sub('and', '/', result)
    result = re.sub('layer', '_', result)
    result = re.sub('Injection did not work', '', result)
    result = re.sub("\'", "\\'", result)
      # insert 
    if SAME_AS_RE.search(result):
      result = result.split("same as")[0]

    extra = ['dorsomedial', 'ventrolateral', 'ventral', 'controlateral', 'contralateral', 'Contralateral', 'caudal', 'rostral', 'medial', 'lateral', 'Lateral', 'dorsal lat', 'dorsal', 'Dorsal', 'contra', 'ipsi lateral', 'vent med', 'ventro', "lat", 'contral', 'control', 'more', 'med-rost', 'lat-cost', 'med-caud', 'lat-caud', 'contra-', 'ipsi-', 'Ipsi', 'dorso', "pole", 'trunk', 'Contra', 'caud']
    extra_tail = ['where', 'deep', 'mid', 'mouth region', 'shell', "can't be seen", 'center point', 'secondary', 'fiber bundle', 'aspect'] 
    for e in extra:
      if e.lower() in result.lower():
        result = re.sub(e, '', result)
    for e in extra_tail:
      if e in result:
        result = result.split(e)[0]
    result = re.sub('^_', '', result)
    if "+" in result:
      result = result.replace(" ", "")
      result = result.replace("+","/")
      f.write("\nCALL insert_new_structure('"+result+"');")
    if LAYERS_RE.search(result):
      if("PL" in result):
        input_split = re.split('(PL)', result)
        output_split = list(map(replace_l, input_split))
        result = "".join(output_split)
        result = result.replace(" ", "")
      else:
        result = result.replace("L", "_")
        result = result.replace(" ", "")
      f.write("\nCALL insert_new_structure('"+result+"');")
    result = re.sub(" \_ ", "", result)
    return result
   
def get_coordinates(data):
    coords = COORDINATES_RE.search(data)
    return coords.groups(0)[0] if coords else ''

def get_tracer(data):
    tracer = TRACER_RE.search(data)
    if tracer:
      result = tracer.groups(0)[0]
    else:
      result = 'n/a'
    result = re.sub(r'- ?far far red', '', result)
    result = re.sub(r'- ?far red', '', result)
    result = re.sub(r' ?\+ ?', '+', result)
    result = re.sub(r' ?- ?', '-', result)
    result = re.sub(r'only', '', result)
    result = re.sub(r'Transgenic mouse', '', result)
    extra = ['Tracers used', 'PAG ARA', 'ARA', 'Houri', 'Hongwei', 'Lei', 'SW', 'MF', 'TB', 'CM', 'DL', 'SU', 'progress', 'slide', 'tissue', 'triple', 'rostral', 'channel', 'levels', 'Q1', 'Q2', 'Q3', 'Q4']
    for e in extra:
      if e in result:
        result = 'n/a'
    if len(result) == 1 and result.isdigit():
      result = 'n/a'
    return result

def get_tech(data):
    tech = data.lower()
    if tech in TECHS:
        return tech
    elif tech in TECHS_ALT:
        return TECHS_ALT[tech]
    else:
        return tech

def get_plane(plane):
    if plane in PLANES:
        return plane
    elif plane in PLANES_ALT:
        return PLANES_ALT[plane]

def add_to_notes(case_dictionary, note, prefix=None):
    note = str(note)
    if len(note) > 0:
        if prefix:
            note = "{}: {}".format(prefix, note)
        
        case_dictionary['notes'] += "\n" + note

def save_json(item):
    with open(output_file, 'w') as f:
        f.write(json.dumps(item, indent=4))

def process(df, name, project, save=False):
    cols = COLUMNS[name]
    df.columns = cols
    prepped_df = prepare_df(df)
    good_df = prepped_df.set_index(['case'])
    project_dict = get_project_dict(good_df, project)
    
    if save:
        save_json(project_dict)

    return project_dict

def get_organism_id(argument):
    switcher = {
        'SG': 7,
        'SP': 17,
        'SV': 18
    }
    return switcher.get(argument, 1)
  
#Lin, Lei, Marlene, Kevin
def get_usernames(argument):
    switcher = {
        'monica': "Monica Song",
        'lei': "Lei Gao",
        'marlene': "Marlene Becerra",
        'nick': "Nick Foster",
    }
    return switcher.get(argument, "Lin Gou")

TRACKERS = {}

U01 = parseSheetData('U01 ')
U19_Salk = parseSheetData('U19 Salk Institute')
U19_CSHL = parseSheetData('U19 CSHL')
MCP = parseSheetData('MCP')
bg = parseSheetData('Basal Ganglia')
RF1 = parseSheetData('RF1 (HPF)')
BLA = parseSheetData('BLA project')

TRACKERS = {'U01 ': U01, 'U19 CSHL': U19_CSHL, 'U19 Salk Institute': U19_Salk, 'MCP': MCP, 'Basal Ganglia': bg, 'RF1 (HPF)': RF1, 'BLA project': BLA}

project = {}
for name, tracker in TRACKERS.items():
  tracker_df = tracker
  tracker_df = tracker_df.iloc[SKIPROWS[name]:]
  project = process(tracker_df, name, project, save=True)

save_json(project)

def get_organism_id(argument):
    switcher = {
        'SG': '7',
        'SP': '17',
        'SV': '18'
    }
    return switcher.get(argument, '1')
f.write("\ndelete from araStructures where abbreviation = 'Scig_b';")
f.write("delete from araStructures where abbreviation = 'Gpe';")
f.write("delete from araStructures where abbreviation = 'SUBd_m';")
f.write("delete from araStructures where abbreviation = 'SUBd_sr';")
f.write("delete from araStructures where abbreviation = 'SUBd_sp';")
f.write("delete from araStructures where abbreviation = 'SUBv_sp';")
f.write("delete from araStructures where abbreviation = 'SUBv_m';")
f.write("delete from araStructures where abbreviation = 'SUBv_sr';")
f.write("\nINSERT IGNORE INTO organisms (id, species, strain, allele_type, gene_marker, description, code) VALUES (17, 'mouse', 'Parvalbumin-Cre', 'transgenic', 'Parvalbumin (PV)', 'These mice selectively express Cre recombinase in PV expressing cells', 'P');")
f.write("\nINSERT IGNORE INTO organisms (id, species, strain, allele_type, gene_marker, description, code) VALUES (18, 'mouse', 'Vasoactive Intestinal Peptide-Cre', 'transgenic', 'Vasoactive Intestinal Peptide (VIP)', 'These mice selectively express Cre recombinase in VIP expressing cells', 'P');")
f.write("\nINSERT INTO users(login_name, user_name, email, user_group, is_active) VALUES('lgao','Lei Gao', 'LeiGao@mednet.ucla.edu',4, 1 )ON DUPLICATE KEY UPDATE email='LeiGao@mednet.ucla.edu';")
f.write("\nINSERT INTO users(login_name, user_name, email, user_group, is_active) VALUES('mbecerra', 'Marlene Becerra', 'mbecerra@loni.usc.edu', 4, 0)ON DUPLICATE KEY UPDATE email='mbecerra@loni.usc.edu';")
f.write("\nINSERT INTO users(login_name, user_name, email, user_group, is_active) VALUES('nfoster', 'Nick Foster', 'nnfoster@mednet.ucla.edu',4, 1)ON DUPLICATE KEY UPDATE email='nnfoster@mednet.ucla.edu';")
f.write("\nDROP TRIGGER IF EXISTS after_injectionSites_insert;DROP TRIGGER IF EXISTS after_injectionSitesLocations_insert;DROP TRIGGER IF EXISTS injectionSitesStains_insert;DROP procedure if exists update_injectionSitesLocationsARAStructures;")
f.write("\nDROP PROCEDURE IF EXISTS update_injectionSitesLocationsARAStructures;")
f.write("\nDROP PROCEDURE IF EXISTS insert_animals_tissueDissections_surgeries_injectionSites;")
f.write("\nDROP PROCEDURE IF EXISTS insert_or_update_tracers;")
f.write("\nDELIMITER $$\nCREATE TRIGGER after_injectionSites_insert AFTER INSERT ON injectionSites\nFOR EACH ROW\nBEGIN\nINSERT INTO injectionSitesLocations(injection_sites_id, types) VALUES(new.id, 'target');\nINSERT INTO injectionSitesLocations(injection_sites_id, types) VALUES(new.id, 'actual');\nEND $$\nDELIMITER ;")
f.write("\nDELIMITER $$\nCREATE TRIGGER injectionSitesStains_insert AFTER INSERT ON injectionSites\nFOR EACH ROW\nBEGIN\nINSERT INTO injectionSitesStains(injection_sites_id, stain_id) VALUES(new.id, 0);\nEND $$\nDELIMITER ;")
f.write("\nCREATE TRIGGER after_injectionSitesLocations_insert AFTER INSERT ON injectionSitesLocations FOR EACH ROW INSERT INTO injectionSitesLocationsARAStructures(injection_sites_location_id, ara_structure_id) VALUES(NEW.id,100162);")
f.write("\ndelimiter $$\nCREATE PROCEDURE update_injectionSitesLocationsARAStructures(structure varchar(255), tissuecode varchar(255), typeo varchar(255), ind int)\nBEGIN\nIF EXISTS (SELECT id FROM araStructures WHERE abbreviation COLLATE UTF8_GENERAL_CI LIKE structure)\nTHEN\nupdate injectionSitesLocationsARAStructures set ara_structure_id=(SELECT id from araStructures where abbreviation COLLATE UTF8_GENERAL_CI like structure)\nWHERE injection_sites_location_id=(SELECT id from injectionSitesLocations where injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code=tissuecode order by id desc limit ind,1) AND types=typeo);\nELSE\nupdate injectionSitesLocationsARAStructures set ara_structure_id=1\nWHERE injection_sites_location_id=(SELECT id from injectionSitesLocations where injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code=tissuecode order by id desc limit ind,1) AND types=typeo);\nEND IF;\nend$$\nDELIMITER ;")
f.write("\ndelimiter $$\nCREATE PROCEDURE insert_or_update_tracers(tracer varchar(255), formattracer varchar (255))\nBEGIN\nIF NOT EXISTS (SELECT id FROM tracers WHERE display_name COLLATE UTF8_GENERAL_CI LIKE formattracer OR abbreviated_name COLLATE UTF8_GENERAL_CI LIKE formattracer OR name COLLATE UTF8_GENERAL_CI LIKE formattracer)\nTHEN\nINSERT INTO tracers (name, display_name, abbreviated_name, description) VALUES (tracer, tracer, tracer, tracer);\nEND IF;\nend$$\nDELIMITER ;")
f.write("\nDELIMITER $$\nCREATE PROCEDURE insert_animals_tissueDissections_surgeries_injectionSites(tissuecode varchar(255), username varchar(255), injections INT)\nBEGIN\nDECLARE x INT;\nSET x = 1;\nIF NOT EXISTS (SELECT id FROM tissueDissections WHERE tissue_code=tissuecode)\nTHEN\nINSERT INTO animals (organism_id) values (1);\nINSERT INTO tissueDissections(tissue_code, tissue_name, description, animal_id) VALUES (tissuecode, 'brain', 'brain', LAST_INSERT_ID());\nINSERT INTO surgeries (user_id, animal_id, tissue_dissection_id) SELECT (select id from users where user_name=username) as user_id, (select animal_id from tissueDissections where tissue_code=tissuecode) as animal_id, LAST_INSERT_ID() as tissue_dissection_id;\nloop_label:  LOOP\nIF  x > injections THEN\nLEAVE  loop_label;\nEND IF;\nINSERT INTO injectionSites (surgery_id) SELECT (SELECT surgeries.id FROM surgeries INNER JOIN tissueDissections td ON surgeries.tissue_dissection_id=td.id WHERE td.tissue_code=tissuecode) AS surgery_id;\nSET x = x + 1;\nEND LOOP;\nEND IF;\nEND$$\nDELIMITER ;")
for id, info in project.items():
  if id != '':
    injections = info['surgery']['injections']
    username = get_usernames(info['surgery']['surgeon'].lower())
    case_prefix = get_organism_id(id[:2])
    f.write("\nCALL insert_animals_tissueDissections_surgeries_injectionSites('"+id+"', '"+username+"', "+str(len(injections))+");")

pattern = r'[\(\)\+ ,]'
for id, info in project.items():
  if id != '':
    injections = info['surgery']['injections']
    new_injections = []
# if no injections
    for injection in injections:
      flag = False
      if not injection['target_loc'].isdigit() and len(injection['target_loc']) > 1:
          flag = True
      if not injection['actual_loc'].isdigit() and len(injection['actual_loc']) > 1:
          flag = True
      if flag:
          new_injections.append(injection)
    injections = new_injections
    ind = len(injections) - 1
    for injection in injections:
      tracer = injection['tracer']['name']
      format_tracer = tracer.replace(' ', '_')
      format_tracer = format_tracer.replace('.', '_')
      format_tracer = format_tracer.replace('-', '_')
      target_loc = injection['target_loc'].replace(' ', '')
      target_loc = target_loc.replace('-', '_')
      target_loc = target_loc.replace('.', '_')
      if target_loc == 'MOpul':
        target_loc = "MOp_ul"
      if target_loc == 'CPint':
        target_loc = "CP"
      actual_loc = injection['actual_loc'].replace(' ', '')
      actual_loc = actual_loc.replace('-', '_')
      actual_loc = actual_loc.replace('.', '_')
      if actual_loc == 'MOpul':
        actual_loc = "MOp_ul"
      if actual_loc == 'CPint':
        actual_loc = "CP"
      end_underscore = re.compile(r'\_$')
      beg_underscore = re.compile(r'^_')
      while end_underscore.search(target_loc):
        target_loc = target_loc[:-1]
      while end_underscore.search(actual_loc):
        actual_loc = actual_loc[:-1]
      while beg_underscore.search(actual_loc):
        actual_loc = actual_loc[1:]
      while beg_underscore.search(target_loc):
        target_loc = target_loc[1:]
      if injection['target_coords'] != '':
          i = injection['target_coords'].split(",")
          target_x = re.sub(pattern, '', i[0])
          target_y = re.sub(pattern, '', i[1])
          target_z = re.sub(pattern, '', i[2])
      else:
          target_x = target_y = target_z = 'NULL'
      if injection['actual_coords'] != '':
          i = injection['actual_coords'].split(",")
          actual_x = re.sub(pattern, '', i[0])
          actual_y = re.sub(pattern, '', i[1])
          actual_z = re.sub(pattern, '', i[2])
      else:
          actual_x = actual_y = actual_z = 'NULL'
      f.write("\nUPDATE injectionSitesLocations set x=" + target_x + ", y=" + target_y + ", z=" + target_z + ", types='target' WHERE injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='"+id+"' order by id desc limit "+str(ind)+",1) AND types='target';")
      f.write("\nUPDATE injectionSitesLocations set x=" + actual_x + ", y=" + actual_y + ", z=" + actual_z + ", types='actual' WHERE injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='"+id+"' order by id desc limit "+str(ind)+",1) AND types='actual';")   
      f.write("\nCALL insert_or_update_tracers('" + tracer + "', '"+format_tracer+"');")
      f.write("\nUPDATE injectionSitesStains SET stain_id=(SELECT id FROM tracers WHERE display_name COLLATE UTF8_GENERAL_CI LIKE '"+tracer+"' OR abbreviated_name COLLATE UTF8_GENERAL_CI LIKE '"+tracer+"' OR name COLLATE UTF8_GENERAL_CI LIKE '"+tracer+"') WHERE injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='"+id+"' order by id desc limit "+str(ind)+",1);")

      # if + insert
      if target_loc != '':
        if target_loc != 'CM' and target_loc != 'ECT' and target_loc != 'ect' and target_loc !='cm':
          f.write("\nCALL update_injectionSitesLocationsARAStructures('"+target_loc+"', '"+id+"', 'target',"+str(ind)+");")
        else:
          f.write("\nupdate injectionSitesLocationsARAStructures set ara_structure_id=(SELECT id from araStructures where abbreviation like '"+target_loc+"')\nWHERE injection_sites_location_id=(SELECT id from injectionSitesLocations where injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='"+id+"' order by id desc limit "+str(ind)+",1) AND types='target');")
      
      if actual_loc != '':
        if actual_loc != 'CM' and actual_loc != 'ECT' and actual_loc != 'ect' and actual_loc !='cm':
          f.write("\nCALL update_injectionSitesLocationsARAStructures('"+actual_loc+"', '"+id+"', 'actual',"+str(ind)+");")
        else:
          f.write("\nupdate injectionSitesLocationsARAStructures set ara_structure_id=(SELECT id from araStructures where abbreviation like '"+actual_loc+"')\nWHERE injection_sites_location_id=(SELECT id from injectionSitesLocations where injection_sites_id=(SELECT i.id FROM injectionSites i INNER JOIN surgeries s ON i.surgery_id=s.id INNER JOIN tissueDissections td on s.tissue_dissection_id=td.id WHERE td.tissue_code='"+id+"' order by id desc limit "+str(ind)+",1) AND types='actual');")
      
      ind = ind - 1

f.write("\nDROP TRIGGER after_injectionSites_insert;\nDROP TRIGGER after_injectionSitesLocations_insert;");
f.write("\nDROP TRIGGER injectionSitesStains_insert;")
f.write("\nDROP PROCEDURE update_injectionSitesLocationsARAStructures;\nDROP PROCEDURE insert_animals_tissueDissections_surgeries_injectionSites;")
f.write("\nDROP PROCEDURE insert_or_update_tracers;\nDROP PROCEDURE insert_new_structure;")
f.close()
