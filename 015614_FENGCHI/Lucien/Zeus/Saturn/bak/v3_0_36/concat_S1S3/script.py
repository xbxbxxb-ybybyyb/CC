# coding: utf-8
# Author：fengchi863
# Date ：2022/10/19 13:19

"""
合并SaturnS1以及SaturnS3的结果
合并逻辑：
S1与S3样本的并集作为总集合，然后总集合减去S1中预测为1的作为S3的准备触发的样本
S1的profit文件设置为S1的，S3的设置为S3的，两者合并成新的收益文件
S1的label文件中，是S3的部分的替换为S3的label，主要更换4个label。
"""
import pandas as pd
from LucienUtil import IO
from Zeus.Saturn.v3_0_36.path_conf import junk_path
from LucienUtil.FileUtil import FileUtil

filter_test_fpath = '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v1.csv'
all933_test_fpath = '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v1.csv'
filter_fit_fpath = '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v1.csv'
all933_fit_fpath = '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v1.csv'

filter_profit_fpath = '/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_500_1500.h5'
filter_label_fpath = '/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5'
all933_profit_fpath ='/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/p2_profit_933_0.20_0.10_500_1500_20160101_20211231.h5'
all933_label_fpath = '/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/sft_basic_origin.h5'

filter_test_pred = pd.read_csv(filter_test_fpath)
all933_test_pred = pd.read_csv(all933_test_fpath)
filter_fit_pred = pd.read_csv(filter_fit_fpath)
all933_fit_pred = pd.read_csv(all933_fit_fpath)

all933_pred = pd.concat([all933_test_pred.query('20191001 <= datelist <= 20200630'), all933_fit_pred.query('20200701 <= datelist <= 20201231')], axis=0)
filter_pred = pd.concat([filter_test_pred.query('20191001 <= datelist <= 20200630'), filter_fit_pred.query('20200701 <= datelist <= 20201231')], axis=0)
filter_pred_true = pd.concat([filter_test_pred.query('prediction == True & 20191001 <= datelist <= 20200630'), filter_fit_pred.query('prediction == True & 20200701 <= datelist <= 20201231')], axis=0)

all933_pred_index = list(set(all933_pred['Indexs'].tolist() + filter_pred['Indexs'].tolist()).difference(set(filter_pred_true['Indexs'].tolist())))
all933_pred = all933_pred.set_index('Indexs').loc[all933_pred_index].reset_index()
all933_pred['stockID'] = all933_pred['Indexs'].map(lambda x: x.split(' ')[0])
all933_pred['datelist'] = all933_pred['Indexs'].map(lambda x: int(x.split(' ')[1]))

filter_profit = pd.read_hdf(filter_profit_fpath)
filter_label = pd.read_hdf(filter_label_fpath)
all933_profit = pd.read_hdf(all933_profit_fpath)
all933_label = pd.read_hdf(all933_label_fpath)
filter_pred_true['index'] = filter_pred_true[['datelist', 'stockID']].apply(lambda x: tuple([pd.to_datetime(str(x['datelist'])), x['stockID']]), axis=1)
all933_pred['index'] = all933_pred[['datelist', 'stockID']].apply(lambda x: tuple([pd.to_datetime(str(x['datelist'])), x['stockID']]), axis=1)

profit1 = filter_profit.loc[filter_pred_true['index'].tolist()]
profit2 = all933_profit.loc[all933_pred['index'].tolist()]
new_profit = pd.concat([profit1, profit2], axis=0)

label1 = filter_label
label2 = all933_label.loc[all933_pred['index'].tolist()]
label1.loc[label2.index, 'label_v2o10d1'] = label2.loc[label2.index, 'label_v2o10d3']
label1.loc[label2.index, 'label_o2o10d1'] = label2.loc[label2.index, 'label_o2o10d3']
label1.loc[label2.index, 'label_Tc2To10d1'] = label2.loc[label2.index, 'label_Tc2To10d3']
label1.loc[label2.index, 'label_TNo2To10d1'] = label2.loc[label2.index, 'label_TNo2To10d3']
new_label = label1.copy()

new_profit = new_profit.sort_index()
new_label = new_label.sort_index()
IO.pd_hdf5_writer(new_profit, junk_path + 'new_profit.h5', dataset='new_profit', override=True)
IO.pd_hdf5_writer(new_label, junk_path + 'new_label.h5', dataset='new_label', override=True)

filter_pred_true = filter_pred_true.drop('index', axis=1)
filter_test_pred = filter_pred_true.query('20191001 <= datelist <= 20200630')
filter_fit_pred = filter_pred_true.query('20200701 <= datelist <= 20201231')
all933_pred = all933_pred.drop('index', axis=1)
all933_test_pred = all933_pred.query('20191001 <= datelist <= 20200630')
all933_fit_pred = all933_pred.query('20200701 <= datelist <= 20201231')

test_pred = pd.concat([filter_test_pred, all933_test_pred], axis=0).sort_values(['datelist', 'stockID']).reset_index(drop=True)
fit_pred = pd.concat([filter_fit_pred, all933_fit_pred], axis=0).sort_values(['datelist', 'stockID']).reset_index(drop=True)
test_pred['prediction'] = test_pred['prediction'].fillna(False)
fit_pred['prediction'] = fit_pred['prediction'].fillna(False)
test_pred.to_csv(junk_path + 'new_test_pred.csv')
fit_pred.to_csv(junk_path + 'new_fit_pred.csv')
