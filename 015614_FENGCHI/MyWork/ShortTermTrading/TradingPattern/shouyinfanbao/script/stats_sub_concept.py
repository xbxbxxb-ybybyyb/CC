# coding: utf-8
# Author：fengchi863
# Date ：2021/1/19 8:33

from ShortTermTrading.Util.System import fetch_man_made_monitor_list
from ShortTermTrading.conf.path_conf import *
import pandas as pd

monitor_list = fetch_man_made_monitor_list()
monitor_concept_df = pd.read_excel(man_made_concept_data_path)
monitor_concept_df = monitor_concept_df[monitor_concept_df['Unnamed: 0'] != 'A20132.SH']
monitor_concept_df['主题'] = monitor_concept_df['概念板块'] + '_' + monitor_concept_df['子主题']

concept = monitor_concept_df[monitor_concept_df['个股名称']=='天晟新材']['主题']
print(monitor_concept_df[monitor_concept_df['主题']==concept])
