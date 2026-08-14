import pandas as pd
import os
import numpy
import re
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

def get_clean_text(text):
    if text is None:
        clean_text = ''
    elif type(text) != str:
        clean_text = ''
    else:
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        clean_text = clean_text.replace('\n',' ')
        clean_text = clean_text.replace('\r',' ')
        clean_text = clean_text.replace('\t',' ')
        clean_text = clean_text.replace('\xa0',' ')
        clean_text = clean_text.replace('\u00A0',' ')
        clean_text = clean_text.replace('\u3000', '')
        clean_text = clean_text.replace('\\', '')
        clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text
def parallel_clean_text_main(file):
    print(file)
    df = pd.read_pickle(base_path + file, compression='gzip')
    df['content'] = df['content'].apply(lambda x : get_clean_text(x))
    df.to_pickle(base_path + file, compression='gzip')
    return
base_path = '/dfs/group/800463/data/news_data/news_data_combo/'
file_list = list(os.listdir(base_path))
file_list.sort()

Parallel(n_jobs=24)(delayed(parallel_clean_text_main)(file) for file in file_list)

#
# no_done_list = []
# def parallel_main(date):
#     df = pd.read_pickle(base_path + date + '.pkl', compression='gzip')
#     try:
#         print(date)
#         if not 'is_value_by_time' in list(df.columns):
#             no_done_list.append(date)
#         else:
#             print(date , '已进行过去重')
#     except Exception as e:
#         print(e)
#         print(date,'error')
#     return
# base_path = '/dfs/group/800463/data/news_data/news_data_combo/'
# start_date = '20160101'
# end_date = '20240630'
# date_list = os.listdir(base_path)
# date_list = [x.replace('.pkl','') for x in date_list]
# date_list = [x for x in date_list if x >= start_date and x <= end_date]
# date_list.sort()
# for date in date_list:
#     parallel_main(date)
# no_done_list = pd.DataFrame(no_done_list)



