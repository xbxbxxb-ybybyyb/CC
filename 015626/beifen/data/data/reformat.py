# -*- coding: utf-8 -*-
"""
update_concensus_htsc

"""
import pandas as pd
import os
path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\der_report_research_3\\'
for file in os.listdir(path):
    print(file)
    csv_path = path + file
    df = pd.read_csv(csv_path)
    column_name = 'Unnamed: 0'
    df.drop(column_name, axis=1, inplace=True)
    df['CONTENT'] = df['CONTENT'].astype('str')
    df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace('\n', ''))
    df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace('\r', ''))
    df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace(',', '，'))
    df.to_csv('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\der_report_research_3\\' + file, sep=',', encoding='utf_8_sig')
