# @Time : 2021/8/10 14:28
# @Author : Zhichen Lu
# @File : signal_integration.py

import os
from Script.lzc.pitches_integration import out_signal
import pandas as pd
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration, get_signal_by_val_pct_threshold_integration_NoMaxThreshold


# file_list=[
#             '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_d_ic_h_d.pkl',
#             '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_t_ic_h_t.pkl',
#             '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_c_ic_h_c.pkl',
#             '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
#             '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
#  ]
file_list=[
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
            '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
            '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
            '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
 ]

for each in file_list[:3]:
    if os.path.exists(each):
        os.remove(each)
    # if os.path.exists(each.replace('.pkl','/20210813.pkl')):
    #     os.remove(each.replace('.pkl','/20210813.pkl'))
start,end = 20210802,20210813
for each in file_list:
    if not os.path.exists(each):
        out_signal(each.replace('.pkl', '/'),end_date=end)


signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(0.05, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, start,
                                                                                      'actual_label',
                                                                                      'new',
                                                                                      head=None,end=end)
pd.to_pickle([signal,pred_ret],f'/data/user/015664/AFuckingTrigger/for5minFactor/sample_{start}_{end}_MIX20210909.pkl')
print(f'/data/user/015664/AFuckingTrigger/for5minFactor/sample_{start}_{end}_MIX20210907.pkl')



