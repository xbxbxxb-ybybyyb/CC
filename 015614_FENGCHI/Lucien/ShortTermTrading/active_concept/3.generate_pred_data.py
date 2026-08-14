# coding: utf-8
# Author：fengchi863
# Date ：2023/11/2 11:08

import pandas as pd
from Zeus.Europa.v4_0_3.path_conf import *

rollDays = 3
if rollDays == 1:
    basic_data = pd.read_pickle(f'/data/user/015614/TEST/active_concept_test/basic_data_concept.pkl')
else:
    basic_data = pd.read_pickle(f'/data/user/015614/TEST/active_concept_test/basic_data_concept_roll{rollDays}.pkl')
basic_data = basic_data.loc[~basic_data['concept'].isna()]
basic_data['datelist'] = basic_data.index.get_level_values(0).map(lambda x: x.strftime('%Y%m%d'))
basic_data['Ticker'] = basic_data.index.get_level_values(1)
basic_data['Indexes'] = basic_data[['datelist', 'Ticker']].apply(lambda x: x['Ticker'] + ' ' + x['datelist'], axis=1)
basic_data = basic_data.set_index('Indexes')

period_list = ['period1', 'period2', 'period3']
testfit_list = ['test', 'fit']

pred_data_path ='/data/user/015614/Zeus/pred/Europa/v4_0_3/fsv10_pct_AllXgbRegModel/'

# method3
topN = 1
for topN in [1, 2, 3]:
    for period in period_list:
        for testfit in testfit_list:
            start_date = date_config[period][f'{testfit}_start_date']
            end_date = date_config[period][f'{testfit}_end_date']
            pred_data_fpath = pred_data_path + f'{start_date}~{end_date}.csv'
            pred_data = pd.read_csv(pred_data_fpath, index_col=0)

            cross_index = list(set(pred_data.index).intersection(basic_data.index))
            pred_data.loc[cross_index, 'concept'] = basic_data.loc[cross_index, 'concept']
            pred_data.loc[cross_index, 'ZT_Time'] = basic_data.loc[cross_index, 'ZT_Time']
            pred_data = pred_data.sort_values(['datelist', 'ZT_Time'])

            pred_data_copy = pred_data.copy()

            for dat in list(set(pred_data_copy['datelist'])):
                tmp_pred_data = pred_data_copy.query(f'datelist == {dat} & ZT_Time > 0')
                concept_counter = dict()
                for idx in range(len(tmp_pred_data)):
                    index = tmp_pred_data.iloc[idx].name
                    row_data = tmp_pred_data.iloc[idx]
                    concept_list = row_data['concept'].split(',')
                    ranks = ''
                    for concept in concept_list:
                        if concept not in concept_counter.keys():
                            concept_counter[concept] = 1
                        else:
                            concept_counter[concept] += 1

                        if ranks == '':
                            ranks += str(concept_counter[concept])
                        else:
                            ranks += f',{str(concept_counter[concept])}'
                    pred_data.loc[index, 'rank_in_ind'] = ranks

            def less_than_topN(ranks, topN):
                res = list(filter(lambda x: int(x) <= topN, ranks))
                return True if len(res) > 0 else False

            pred_data['prediction'] = False
            pred_data.loc[cross_index, 'prediction'] = pred_data.loc[cross_index, 'rank_in_ind'].apply(lambda x: less_than_topN(x.split(','), topN))

            save_path = f'/data/user/015614/Zeus/pred/Europa/v4_0_3_top{topN}_method1/fsv10_pct_AllXgbRegModel/'
            os.makedirs(save_path, exist_ok=True)
            pred_data.to_csv(save_path + f'{start_date}~{end_date}.csv')

    for period in period_list:
        for testfit in testfit_list:
            start_date = date_config[period][f'{testfit}_start_date']
            end_date = date_config[period][f'{testfit}_end_date']
            pred_data_fpath = pred_data_path + f'{start_date}~{end_date}.csv'
            pred_data = pd.read_csv(pred_data_fpath, index_col=0)

            cross_index = list(set(pred_data.index).intersection(basic_data.index))
            pred_data.loc[cross_index, 'concept'] = basic_data.loc[cross_index, 'concept']
            pred_data.loc[cross_index, 'ZT_Time'] = basic_data.loc[cross_index, 'ZT_Time']
            pred_data = pred_data.sort_values(['datelist', 'ZT_Time'])

            pred_data_copy = pred_data.copy()

            for dat in list(set(pred_data_copy['datelist'])):
                tmp_pred_data = pred_data_copy.query(f'datelist == {dat} & ZT_Time > 0')
                concept_counter = dict()
                for idx in range(len(tmp_pred_data)):
                    index = tmp_pred_data.iloc[idx].name
                    row_data = tmp_pred_data.iloc[idx]
                    concept_list = row_data['concept'].split(',')
                    ranks = ''
                    for concept in concept_list:
                        if concept not in concept_counter.keys():
                            concept_counter[concept] = 1
                        else:
                            concept_counter[concept] += 1

                        if ranks == '':
                            ranks += str(concept_counter[concept])
                        else:
                            ranks += f',{str(concept_counter[concept])}'
                    pred_data.loc[index, 'rank_in_ind'] = ranks


            def less_than_topN(ranks, topN):
                res = list(filter(lambda x: int(x) <= topN, ranks))
                return True if len(res) > 0 else False


            pred_data['prediction2'] = False
            pred_data.loc[cross_index, 'prediction2'] = pred_data.loc[cross_index, 'rank_in_ind'].apply(lambda x: less_than_topN(x.split(','), topN))
            pred_data['prediction'] = pred_data[['prediction', 'prediction2']].apply(lambda x: x['prediction'] | x['prediction2'], axis=1)

            save_path = f'/data/user/015614/Zeus/pred/Europa/v4_0_3_top{topN}_method2/fsv10_pct_AllXgbRegModel/'
            os.makedirs(save_path, exist_ok=True)
            pred_data.to_csv(save_path + f'{start_date}~{end_date}.csv')

# method1
for period in period_list:
    for testfit in testfit_list:
        start_date = date_config[period][f'{testfit}_start_date']
        end_date = date_config[period][f'{testfit}_end_date']
        pred_data_fpath = pred_data_path + f'{start_date}~{end_date}.csv'
        pred_data = pd.read_csv(pred_data_fpath, index_col=0)

        cross_index = list(set(pred_data.index).intersection(basic_data.index))
        pred_data.loc[cross_index, 'concept'] = basic_data.loc[cross_index, 'concept']
        pred_data['prediction'] = False
        pred_data.loc[cross_index, 'prediction'] = True

        save_path = f'/data/user/015614/Zeus/pred/Europa/v4_0_3_all_method1/fsv10_pct_AllXgbRegModel/'
        os.makedirs(save_path, exist_ok=True)
        pred_data.to_csv(save_path + f'{start_date}~{end_date}.csv')

# method2
for period in period_list:
    for testfit in testfit_list:
        start_date = date_config[period][f'{testfit}_start_date']
        end_date = date_config[period][f'{testfit}_end_date']
        pred_data_fpath = pred_data_path + f'{start_date}~{end_date}.csv'
        pred_data = pd.read_csv(pred_data_fpath, index_col=0)

        cross_index = list(set(pred_data.index).intersection(basic_data.index))
        pred_data.loc[cross_index, 'concept'] = basic_data.loc[cross_index, 'concept']
        pred_data.loc[cross_index, 'prediction'] = True

        save_path = f'/data/user/015614/Zeus/pred/Europa/v4_0_3_all_method2/fsv10_pct_AllXgbRegModel/'
        os.makedirs(save_path, exist_ok=True)
        pred_data.to_csv(save_path + f'{start_date}~{end_date}.csv')