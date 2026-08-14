import pandas as pd
import json
param = {'sell_vol_pct': 0.1, 'max_amt': 800 * 10000, 'lag_ms_SH': 300, 'lag_ms_SZ': 30}
latest_version = '20210825'
thred_dict = {'Hml0DjModel': 0.0149,
              'Hml1DjModel': 0.0721,
              'Hml2DjModel': 0.1281,
              'Hml0PMMLModel': 0,
              'Hml1PMMLModel': 0,
              'Hml2PMMLModel': 0,
              'RisePctHighDjModel': 0.1194,
              'RisePctLowDjModel': 0.0782,
              'RollLgbClaModel': 0.537,#0.502,
              'TotalDjClaModel': 0.66,
              'TotalDjRegModel': 0.0535,
              'Type0lgbClaModel': 0.5,
              'Type1lgbClaModel': 0.552,
              'Type2lgbClaModel': 0.501,
              'Type0lrClaModel': 0.5,
              'Type1lrClaModel': 0.5039,
              'Type2lrClaModel': 0.5002,
              'Type0PMMLModel': 0,
              'Type1PMMLModel': 0,
              'Type2PMMLModel': 0,
              'Type0XgbModel': 0,
              'Type1XgbModel': 0,
              'Type2XgbModel': 0,
              'ZTBysModel': 0,
              'ZTDjRegModel': 0.0735,
              'ZTDjClaModel': 0.68}
thred_dict_v8 = {'Hml0DjModel': 0.069,
              'Hml1DjModel': 0.091,
              'Hml2DjModel': 0.074,
              #'Hml0PMMLModel': 0,
              #'Hml1PMMLModel': 0,
              #'Hml2PMMLModel': 0,
            'Hml0XgbModel': 0,
              'Hml1XgbModel': 0,
              'Hml2XgbModel': 0,
            'Hml0XgbWjModel': 0.551,
              'Hml1XgbWjModel': 0.554,
              'Hml2XgbWjModel': 0.65,
              'RisePctHighDjModel': 0.082,
              'RisePctLowDjModel': 0.059,
              #'RollLgbClaModel': 0.537,#0.502,
              #'TotalDjClaModel': 0.66,
              #'TotalDjRegModel': 0.0535,
            'TotalDjModel': 0.046,
            'TotalXgbModel': 0,
            'TotalXgbWjModel': 0.5858,
              #'Type0lgbClaModel': 0.5,
              #'Type1lgbClaModel': 0.552,
             # 'Type2lgbClaModel': 0.501,
             # 'Type0lrClaModel': 0.5,
             # 'Type1lrClaModel': 0.5039,
             # 'Type2lrClaModel': 0.5002,
              'Type0PMMLModel': 0,
              'Type1PMMLModel': 0,
              'Type2PMMLModel': 0,
              #'Type0XgbModel': 0,
              #'Type1XgbModel': 0,
             # 'Type2XgbModel': 0,
            'Type0XgbWjModel': 0.8,
              'Type1XgbWjModel': 0.618,
              'Type2XgbWjModel': 0.64,
              'ZTBysModel': 0,
              'ZTDjRegModel': 0.0735,
              'ZTDjClaModel': 0.68}

# TODO：谢总提供，我要，实盘模型和阈值
path_jup001_v1 = '/data/group/800463/日内强势股/实盘测试参数/模型参数/modelPathConfig_jup001_v1.json'
with open(path_jup001_v1, 'r', encoding='utf-8') as file_name:
    thred_jup001_v1 = json.load(file_name)
    thred_pd_jup001_v1 = pd.DataFrame(thred_jup001_v1)
thred_dict_jup001_v1 = dict(zip(thred_pd_jup001_v1['parentPath'].tolist(),thred_pd_jup001_v1['modelThres'].tolist()))

path_jup_v9 = '/data/group/800463/xiely/save-file/for_wj/modelPathConfig_jpt.json'
with open(path_jup_v9, 'r', encoding='utf-8') as file_name:
    thred_jup_v9 = json.load(file_name)
    thred_pd_jup_v9 = pd.DataFrame(thred_jup_v9)
thred_dict_jup_v9 = dict(zip(thred_pd_jup_v9['parentPath'].tolist(),thred_pd_jup_v9['modelThres'].tolist()))

# 20230516 by fengc jupiterZ上仿真啦！！！
path_jupz_v2 = '/data/group/800463/xiely/save-file/for_wj/sell/jupiterZ_0515_modelPathConfig.json'
with open(path_jupz_v2, 'r', encoding='utf-8') as file_name:
    thred_jupz_v2 = json.load(file_name)
    thred_pd_jupz_v2 = pd.DataFrame(thred_jupz_v2)
thred_dict_jupz_v2 = dict(zip(thred_pd_jupz_v2['parentPath'].tolist(),thred_pd_jupz_v2['modelThres'].tolist()))

path_jup001_v3 = '/data/group/800463/xiely/save-file/for_wj/sell/europa_v3_modelPathConfig.json'
with open(path_jup001_v3, 'r', encoding='utf-8') as file_name:
    thred_jup001_v3 = json.load(file_name)
    thred_pd_jup001_v3 = pd.DataFrame(thred_jup001_v3)
thred_dict_jup001_v3 = dict(zip(thred_pd_jup001_v3['parentPath'].tolist(),thred_pd_jup001_v3['modelThres'].tolist()))


path_jup001_v2 = '/data/group/800463/xiely/save-file/for_wj/modelPathConfig_eur.json'
with open(path_jup001_v2, 'r', encoding='utf-8') as file_name:
    thred_jup001_v2 = json.load(file_name)
    thred_pd_jup001_v2 = pd.DataFrame(thred_jup001_v2)
thred_dict_jup001_v2 = dict(zip(thred_pd_jup001_v2['parentPath'].tolist(),thred_pd_jup001_v2['modelThres'].tolist()))

thred_dict_pj2_930 = {'openPctHighDjClaModel': 0.74,
                  'openPctHighWjClaModel': 0.555,
                  'openPctLowDjClaModel': 0.7,
                  'openPctLowWjClaModel': 0.57,
                  'pat3XgbClaModel': 0.5,
                  'pat4XgbClaModel': 0.5,
                  'totalDjClaModel': 0.64,
                  'totalWjClaModel': 0.5609}
thred_dict_pj2_931 = {'saturn931OpenPctHighDjModel': 0.1105,
                  'saturn931OpenPctHighWjModel': 0.891,
                  'saturn931OpenPctLowDjModel': 0.0817,
                  'saturn931OpenPctLowWjModel': 0.847,
                  'saturn931Pat3DjModel': 0.0768,
                  'saturn931Pat3XgbModel': 0,
                  'saturn931Pat4DjModel': 0.1744,
                  'saturn931Pat4XgbModel': 0,
                  'saturn931Pct5HighWjModel': 0.77,
                  'saturn931Pct5LowWjModel': 0.8,
                  'saturn931Ret2oHighDjModel': 0.1066,
                  'saturn931Ret2oHighPMMLModel': 0,
                  'saturn931Ret2oLowDjModel': 0.107,
                  'saturn931Ret2oLowPMMLModel': 0,
                  'saturn931TotalDjModel': 0.101,
                  'saturn931TotalWjModel': 0.81}

path_s1_v5 = '/data/group/800463/日内强势股/实盘测试参数/模型参数/modelPathConfig_S1_v5.json'
with open(path_s1_v5, 'r', encoding='utf-8') as file_name:
    thred_pj2_931_v5 = json.load(file_name)
    thred_pd_pj2_931_v5 = pd.DataFrame(thred_pj2_931_v5)
thred_dict_pj2_931_v5 = dict(zip(thred_pd_pj2_931_v5['parentPath'].tolist(),thred_pd_pj2_931_v5['modelThres'].tolist()))

thred_dict_v2 = {'TotalLgbClaWjModel':0.535,
              'HighPct5XgbClaModel':0.5,
              'LowPct5XgbClaModel': 0.5,
              'TotalDjClaModel':0.64,
              'TotalDjRegModel':0.082,
              'TotalLrModel':0,
              'TotalXgbModel':0,
              'manual_model_result_hml_reg_except_v1_v10':0.092,
              'manual_model_result_hml_reg_high_v1_v10':0.0943,
              'manual_model_result_hml_reg_low_v1_v10':0.0179,
              'RollType0lgbClaModel':0.535,
              'RollType1lgbClaModel':0.52,
              'RollType2lgbClaModel':0.535,
              'TotalLrClaWjModel':0.5352,
              'Type0XgbModel':0,
              'Type1XgbModel':0,
              'Type2XgbModel':0,
              'ZTBysModel':0,
              'ZTDjRegModel':0.057,
              'ZTDjClaModel':0.75}


thred_dict_pj3_931 = {'ceres931cbMoreDjModel' : 0.1076,
                          'ceres931cbOneDjModel' : 0.0023,
                          'ceres931Pct5HighDjModel' : 0.0506,
                          'ceres931Pct5HighWjModel' : 0.619,
                          'ceres931inTimeXlyModel' : 0,
                          'ceres931Pct5LowDjModel' : 0.0447,
                          'ceres931Pct5LowWjModel' : 0.538,
                          'ceres931outTimeXlyModel' : 0,
                          'ceres931t1PctHighXlyModel' : 0,
                          'ceres931t1PctLowXlyModel' : 0,
                          'ceres931TotalDjModel' : 0.0433,
                          'ceres931totalOpenDjModel' : 0.0633,
                          'ceres931totalXlyModel' :0,
                          'ceres931TotalWjModel' : 0.584,
                          'ceres931ulLongXlyModel' : 0,
                          'ceres931ulShortXlyModel' : 0}
thred_dict_pj3_931_v2 = {'ceres931cbMoreDjModel' :0.073,
                          'ceres931cbOneDjModel' : 0.017,
                          'ceres931Pct5HighDjModel' : 0.032,
                          'ceres931Pct5HighWjModel' : 0.489,
                          #'ceres931inTimeXlyModel' : 0,
                          'ceres931Pct5LowDjModel' : 0.039,
                          'ceres931Pct5LowWjModel' : 0.79,
                          #'ceres931outTimeXlyModel' : 0,
                          'ceres931t1PctHighXlyModel' : 0,
                          'ceres931t1PctLowXlyModel' : 0,
                          'ceres931TotalDjModel' : 0.032,
                          'ceres931totalOpenDjModel' : 0.034,
                          'ceres931totalXlyModel' :0,
                          #'ceres931TotalWjModel' : 0.584,
                          'ceres931ulLongXlyModel' : 0,
                          'ceres931ulShortXlyModel' : 0,
                         'ceres931OpenMedWjModel':0.749,
                         'ceres931OpenOthWjModel':0.6}
thred_pj3_vote_num = 5
latest_version_pj3 = '20220128'

path_sell3_v1 = '/data/group/800463/xiely/save-file/for_wj/sell//sell_v3_modelPathConfig.json'
with open(path_sell3_v1, 'r', encoding='utf-8') as file_name:
    thred_pj2_931_sell3 = json.load(file_name)
    thred_pj2_931_sell3 = pd.DataFrame(thred_pj2_931_sell3)
thred_dict_pj2_931_sell3 = dict(zip(thred_pj2_931_sell3['parentPath'].tolist(),thred_pj2_931_sell3['modelThres'].tolist()))
thred_pj2sell3_vote_num= 4

path_sell1_v1 = '/data/group/800463/xiely/save-file/for_wj/sell/sell_v1_modelPathConfig.json'
with open(path_sell1_v1, 'r', encoding='utf-8') as file_name:
    thred_pj2_931_sell1 = json.load(file_name)
    thred_pj2_931_sell1 = pd.DataFrame(thred_pj2_931_sell1)
thred_dict_pj2_931_sell1 = dict(zip(thred_pj2_931_sell1['parentPath'].tolist(),thred_pj2_931_sell1['modelThres'].tolist()))
thred_pj2sell1_vote_num= 4

path_cers1_v3 = '/data/group/800463/日内强势股/实盘测试参数/模型参数/modelPathConfig_cerS1_v3.json'
with open(path_cers1_v3, 'r', encoding='utf-8') as file_name:
    thred_pj3_931_v3 = json.load(file_name)
    thred_pd_pj3_931_v3 = pd.DataFrame(thred_pj3_931_v3)
thred_dict_pj3_931_v3 = dict(zip(thred_pd_pj3_931_v3['parentPath'].tolist(),thred_pd_pj3_931_v3['modelThres'].tolist()))
thred_pj3_vote_num_v3= 3




white_list_list = ['/data/group/800463/stock_list/white_list/']
'''thred_dict = {'TotalLgbClaWjModel':0.535,
              'TotalXgbRegWjModel':1.1,
              'HighPct5XgbClaModel':0.5,
              'LowPct5XgbClaModel': 0.5,
              'TotalDjClaModel':0.64,
              'TotalDjRegModel':0.082,
              'TotalLrModel':0,
              'TotalXgbModel':0,
              'manual_model_result_hml_reg_except_v1_v10':0.092,
              'manual_model_result_hml_reg_high_v1_v10':0.0943,
              'manual_model_result_hml_reg_low_v1_v10':0.0179,
              'RollType0lgbClaModel':0.535,
              'RollType1lgbClaModel':0.52,
              'RollType2lgbClaModel':0.535,
              'TotalLrClaWjModel':0.5352,
              'Type0XgbModel':0,
              'Type1XgbModel':0,
              'Type2XgbModel':0,
              'ZTBysModel':0,
              'ZTDjRegModel':0.057,
              'ZTDjClaModel':0.75}'''