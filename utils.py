import pandas as pd
import os
import datetime
import re

def convert_to_seconds(row):
    try:
        hours, minutes, seconds = map(float, row.split(":"))
        total_seconds = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return total_seconds
    except Exception as e:
        print(f"Error processing row: {row}, Error: {e}")
        return None

def get_n_cols(fpath: str):
    """
    Get the number of columns
    """
    f = open(fpath, 'r')
    for line in f.readlines():
        row = line.strip().rsplit(",")
        if len(row) > 0 and row[0] == "System Time":
            return len(row)
    return 0

def is_match_date_string(ds: str):
    pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"
    if re.match(pattern, ds):
        return True
    return False

def extract_origin_csv(fpath: str):
    """
    The following content is the header of tester.
    %	Time								
    @	16								
    Label	Fuction	Set	Record Time	Change					
            "Charge	CC-CV	I=2.500	V=3.700"	00:15.0	"Time=05:00:00--Next	EC=0.125--Next"					
    $	16	Loop (S1)=1/2000	Loop (S2)=8/100						
    System Time	Step Time	V	I	T	R	P	mAh	Wh	Total Time
    """
    f = open(fpath, 'r')
    rows = []
    last_time_per_step_list = []
    step_name = None
    n_cols = get_n_cols(fpath=fpath)

    try:
        for line in f.readlines():
            row = line.strip().rsplit(",")
            if len(row) > 0 and row[0] in {"%", "@", "Label", "", "$", "System Time", "Start Time"}: #content
                if len(row) == 5 and row[0] == "" and row[1] == "": #header line 4
                    step_name = row[2]         
                elif len(row) == 2 and row[0] == '%': # header line 1
                    last_time_per_step_list.append(len(rows)-1)
                else:
                    pass
            else:
                if len(row) == n_cols and is_match_date_string(row[0]): # ensure the number of columns matches the data columns
                    row.append(step_name)
                    rows.append(row)

        last_time_per_step_list.append(len(rows) -1)
    
    except:
        raise Exception("此檔案並非'承德充放電機'檔案格式，請確認選擇檔案。")

    
    return rows, last_time_per_step_list