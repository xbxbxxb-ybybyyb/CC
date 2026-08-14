# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

import pandas as pd

from Zeus.Saturn.v4_0_14.path_conf import date_config
import json
PERIOD = 'period1'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'test'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
test_out_begin, test_out_end = date_dict[f'test_start_date'], date_dict[f'test_end_date']

sel_models = ['fsv8_emotion_XgbRegModel', 'fsv10_emotion_XgbRegModel', 'fsv11_emotion_XgbRegModel', 'fsrs_emotion_XgbRegModel',
                       'fsv8_noEmotion_XgbRegModel', 'fsv10_noEmotion_XgbRegModel', 'fsv11_noEmotion_XgbRegModel', 'fsrs_noEmotion_XgbRegModel',
                       'fsv8_emotion_LgbRegModel', 'fsv10_emotion_LgbRegModel', 'fsv11_emotion_LgbRegModel', 'fsrs_emotion_LgbRegModel',
                       'fsv8_noEmotion_LgbRegModel', 'fsv10_noEmotion_LgbRegModel', 'fsv11_noEmotion_LgbRegModel', 'fsrs_noEmotion_LgbRegModel',]
pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Europa/v2_0_19/{x}/{out_begin}~{out_end}_{x}_{SUB_VERSION}.csv' for x in sel_models
]

backtest_fpath = f'/data/user/015614/junkData/回测结果/{test_out_begin}~{test_out_end}_SaturnS1_fac_20230626_FSV8_all_label_v2o10d1_graded_period{PERIOD[-1]}_v413_all_merge_test_模型评价_20230630.xlsx'
diff_threshold = pd.read_excel(backtest_fpath, sheet_name='不同参与率统计')
threshold_list = []
attend_min = 0.24
attend_max = 0.26
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    cur_model = diff_threshold.iloc[1 + idx + idx * 31: 1 + idx + (idx + 1) * 31]
    print(cur_model.shape)
    cur_model = cur_model.set_index('Unnamed: 0')
    cur_model = cur_model.query(f'{attend_min} <= 实际参与率 <= {attend_max}')
    cur_model['indicator'] = cur_model['累计盈利'] * cur_model['收益夏普比率']
    cur_model = cur_model.sort_values('indicator', ascending=False)
    threshold = float(cur_model.iloc[0].name)
    attend_ratio = cur_model.iloc[0]['实际参与率']
    print('参与率：', attend_ratio)

    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)

# threshold_list = [0.014687, 0.014395, 0.014268, 0.018012, 0.012915, 0.012331, 0.012873, 0.013595]   # period1
# threshold_list = [0.014687, 0.014395, 0.014268, 0.018012, 0.012915, 0.012331, 0.012873, 0.013595]   # period1
# threshold_list = [0.014687, 0.014395, 0.014268, 0.018012, 0.012915, 0.012331, 0.012873, 0.013595]   # period1
# for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
#     pred_data = pd.read_csv(pred_data_fpath, index_col=0)
#     threshold = threshold_list[idx]
#     pred_data['prediction'] = pred_data['pred_Reg'] > threshold
#     pred_data.to_csv(pred_data_fpath)

# for idx, pred_path in enumerate(pred_data_fpath_list):
#     with open(pred_path + '_score_threshold.json', 'w') as f:
#         json.dump([threshold_list[idx]], f, ensure_ascii=False, indent=2)
