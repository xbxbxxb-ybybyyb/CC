# coding: utf-8
# Author：fengchi863
# Date ：2023/4/18 9:20

import os
import pandas as pd
import json
import requests
from scipy import stats
import time
from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest


def save_dict2xls(data: dict, path=None, filename=None, verbose=True):
    os.makedirs(path, exist_ok=True)
    with pd.ExcelWriter(path + filename) as writer:
        for each in data:
            data[each].to_excel(writer, each)
    if verbose:
        print(f'{filename} has been saved in {path + filename}')

def send_file(file, filename=None, users=['015614']):
    if not filename:
        filename = 'tmp'
    if isinstance(file, pd.DataFrame):
        file.to_excel(f'/data/user/015614/fengc/tmp_data/{filename}.xlsx')
        file = f'/data/user/015614/fengc/tmp_data/{filename}.xlsx'

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)

start_date = 20160101
end_date = 20191231
sft = strongFactorTest(start_date, end_date)

root_path = '/data/user/015614/factor/factor_digging_20230822162308_20230822测试/'
note = root_path.split('_')[-1][:-1]
file_list = os.listdir(root_path)
xlsx_list = list(filter(lambda x: x.endswith(').xlsx'), file_list))
factor_fpath_list = list(filter(lambda x: x.endswith('.pkl'), file_list))
res_list = []
for xlsx in xlsx_list:
    tmp = pd.read_excel(root_path + xlsx, index_col=0)
    res_list.append(tmp)
res_df = pd.concat(res_list, axis=0)

# factor_df_list = []
# for factor_fpath in factor_fpath_list:
#     if factor_fpath != 'factor.pkl':
#         tmp = pd.read_pickle(root_path + factor_fpath)
#         factor_df_list.append(tmp)
#
# all_factor = pd.concat(factor_df_list, axis=1)

factor_df_list = []
for factor_fpath in factor_fpath_list:
    if factor_fpath != 'factor.pkl':
        tmp = pd.read_pickle(root_path + factor_fpath)
        tmp = tmp.reindex(index=sft.basic_df.index)
        factor_df_list.append(tmp)

print(f'开始拼接{len(factor_df_list)}个因子')
all_factor = pd.concat(factor_df_list, axis=1)
print('拼接完成')

res_df['highest_corr'] = res_df['high_corr_factor_corr'].map(lambda x: float(x.split('，')[0]))
# 计算相关性
corr_res = pd.DataFrame(index=all_factor.columns.tolist(), columns=all_factor.columns.tolist())
for idx1, factor_name1 in enumerate(all_factor.columns.tolist()):
    for idx2, factor_name2 in enumerate(all_factor.columns.tolist()):
        if idx1 > idx2:
            corr_res.iloc[idx1, idx2] = stats.spearmanr(all_factor[factor_name1].fillna(0), all_factor[factor_name2].fillna(0))[0]
            corr_res.iloc[idx2, idx1] = corr_res.iloc[idx1, idx2]

# corr_res = all_factor.corr()  # 计算耗时太高，采用分批计算方案

corr_res = corr_res.applymap(abs)
for index in res_df.index:
    self_highest_corr = corr_res.loc[index.replace('/', '%')].sort_values(ascending=False)
    res_df.loc[index, 'self_high_corr'] = ','.join(self_highest_corr[self_highest_corr > 0.7].index.tolist())
    res_df.loc[index, 'self_high_factor'] = ','.join(self_highest_corr[self_highest_corr > 0.7].map(lambda x: str(round(x, 3))).tolist())

output_dict = {'score': res_df,
               'corr': corr_res}
save_dict2xls(output_dict, root_path, f'因子寻优结果_{note}.xlsx')
send_file(root_path + f'因子寻优结果_{note}.xlsx')