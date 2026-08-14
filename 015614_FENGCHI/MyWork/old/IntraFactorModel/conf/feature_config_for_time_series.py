# @Time : 2020/6/23 9:14
# @Author : Zhichen Lu
# @File : feature_config_for_time_series.py

# coding: utf-8
# Author：fengchi863
# Date ：2020/5/26 13:28

all_feature_list = [
    'alpha1',
    'alpha10',
    'alpha11',
    'alpha12',
    'alpha122',
    'alpha123',
    'alpha124',
    'alpha126_1',
    'alpha126_2',
    'alpha127',
    'alpha129',
    'alpha13',
    'alpha133_1',
    'alpha133_2',
    'alpha134',
    'alpha135',
    'alpha139',
    'alpha14',
    'alpha140',
    'alpha141',
    'alpha142',
    'alpha145',
    'alpha147',
    'alpha151',
    'alpha153',
    'alpha156',
    'alpha16',
    'alpha161',
    'alpha163',
    'alpha164',
    'alpha166',
    'alpha167',
    'alpha168',
    'alpha169',
    'alpha17',
    'alpha170',
    'alpha171',
    'alpha174',
    'alpha175',
    'alpha176',
    'alpha177',
    'alpha178',
    'alpha179',
    'alpha18',
    'alpha180',
    'alpha181',
    'alpha184',
    'alpha187',
    'alpha188',
    'alpha189',
    'alpha19',
    'alpha191',
    'alpha2',
    'alpha21',
    'alpha22',
    'alpha23',
    'alpha24',
    'alpha25',
    'alpha27',
    'alpha28',
    'alpha29',
    'alpha3',
    'alpha31',
    'alpha32',
    'alpha35',
    'alpha36',
    'alpha37',
    'alpha38',
    'alpha39',
    'alpha4',
    'alpha40',
    'alpha41',
    'alpha42',
    'alpha43',
    'alpha45',
    'alpha46',
    'alpha47',
    'alpha48',
    'alpha49',
    'alpha5',
    'alpha50',
    'alpha52',
    'alpha53',
    'alpha55',
    'alpha56',
    'alpha57',
    'alpha58',
    'alpha59',
    'alpha6',
    'alpha60',
    'alpha7',
    'alpha8',
    'alpha9',
    'boll1',
    'boll10',
    'boll11',
    'boll12',
    'boll2',
    'boll3',
    'boll4',
    'boll5',
    'boll6',
    'boll7',
    'boll8',
    'boll9',
    'factor101',
    'factor103',
    'factor105',
    'factor106',
    'factor107',
    'factor110',
    'factor112',
    'factor113',
    'factor114',
    'factor116',
    'factor118',
    'factor119',
    'factor120',
    'factor61',
    'factor62',
    'factor63',
    'factor64',
    'factor68',
    'factor69',
    'factor71',
    'factor72',
    'factor73',
    'factor74',
    'factor75',
    'factor78',
    'factor81',
    'factor83',
    'factor86',
    'factor87',
    'factor90',
    'factor91',
    'factor92',
    'factor94',
    'factor98',
    'factor99',
    'factor_dev01',
    'factor_dev02',
    'factor_dev03',
    'factor_dev04',
    'factor_dev05',
    'factor_dev07',
    'factor_dev08'
]

selected_feature_list_1min = ['factor_dev07', 'boll3', 'boll9', 'boll4', 'factor_dev03', 'boll10', 'boll5', 'boll7', 'boll6', 'factor_dev02', 'alpha25', 'boll8',
                              'alpha153', 'boll11', 'boll12', 'alpha163', 'alpha31', 'alpha126_2', 'alpha10', 'alpha19', 'factor_dev05', 'factor_dev01', 'alpha22',
                              'alpha57', 'alpha14', 'alpha3', 'alpha28', 'alpha21', 'alpha142', 'factor_dev08', 'alpha29', 'boll2', 'boll1', 'alpha47', 'alpha178',
                              'alpha59', 'factor78', 'alpha2', 'alpha23', 'alpha156', 'factor72', 'alpha9', 'alpha24', 'factor98', 'alpha127', 'factor_dev04',
                              'alpha11', 'alpha12', 'factor63', 'factor118']

selected_feature_list_5min = ['alpha124', 'alpha163', 'boll3', 'boll4', 'factor_dev07', 'boll9', 'boll5', 'factor_dev03', 'boll10', 'boll6', 'factor_dev02',
                              'boll7', 'boll8', 'alpha170', 'factor114', 'alpha25', 'alpha126_2', 'boll11', 'alpha37', 'boll12', 'alpha166', 'alpha142',
                              'alpha153', 'alpha46', 'alpha18', 'alpha10', 'alpha22', 'alpha19', 'factor91', 'alpha31', 'alpha184', 'alpha7', 'factor120',
                              'alpha178', 'alpha21', 'alpha14', 'alpha48', 'alpha181', 'alpha28', 'alpha17', 'alpha45', 'alpha134', 'alpha3', 'alpha171',
                              'factor_dev05', 'alpha29', 'boll1', 'alpha23', 'boll2', 'factor_dev08']

drop_list = ['alpha1', 'alpha6', 'alpha7', 'alpha8', 'alpha10', 'alpha12', 'alpha16', 'alpha17', 'alpha25', 'alpha32',
             'alpha35',
             'alpha36', 'alpha37', 'alpha39', 'alpha41', 'alpha42', 'alpha45', 'alpha48', 'alpha56', 'factor107',
             'factor114',
             'factor99', 'factor113', 'factor64', 'factor105', 'factor90', 'factor62', 'factor91', 'factor83',
             'factor101',
             'factor73', 'factor119', 'factor74', 'factor120', 'factor61', 'factor87', 'factor92', 'alpha123',
             'alpha124', 'alpha126_2',
             'alpha133_1', 'alpha133_2', 'alpha134', 'alpha139', 'alpha140', 'alpha141', 'alpha142', 'alpha156',
             'alpha163', 'alpha164', 'alpha166', 'alpha170', 'alpha171',
             'alpha180', 'alpha184', 'alpha188', 'alpha176', 'alpha179']
sparse_list = ['alpha126_1', 'alpha129', 'alpha14', 'alpha140', 'alpha16', 'alpha167', 'alpha175', 'alpha177', 'alpha187', 'alpha2', 'alpha3', 'alpha38', 'alpha4', 'alpha53',
               'alpha58', 'alpha59', 'alpha60', 'factor103', 'factor75', 'factor87', 'factor98']

drop_list = list(set(drop_list).union(set(sparse_list)))
#
# selected_list = []
# f = open('./intrafactormodel/FactorRedfine/factor_definition.txt.py')
# factor_list = []
# for line in f.readlines():
#     # print(line)
#     line_ = line.split('=')
#     if len(line_)<2:
#         continue
#     factor_name = line_[0]#.split('=')
#     factor_list.append(factor_name.strip())
#     formula = '='.join(line_[1:])
#     # print(formula)
#     if 'cross' in formula:
#         drop_list.append(factor_name.strip())
#     else:
#         selected_list.append(factor_name.strip())
# f.close()
# import pandas as pd
#
# check = pd.DataFrame(factor_list)
# check['no_cross'] = check[0].apply(lambda x: x in drop_list) * 1
# check.to_excel('/data/user/015664/cross_judge.xlsx')

non_scale_list = ['alpha133_2', 'alpha156', 'alpha139', 'alpha188', 'alpha164',
                  'alpha49', 'alpha47', 'alpha163', 'alpha166']
non_scale_list = list(set(non_scale_list) - set(drop_list))
scale_list = list(set(all_feature_list) - set(non_scale_list) - set(drop_list))
scale_list_1min = list(set(selected_feature_list_1min) - set(non_scale_list) - set(drop_list))
non_scale_list_1min = list(set(selected_feature_list_1min).intersection(set(non_scale_list)))
scale_list_5min = list(set(selected_feature_list_5min) - set(non_scale_list) - set(drop_list))
non_scale_list_5min = list(set(selected_feature_list_5min).intersection(set(non_scale_list)))
