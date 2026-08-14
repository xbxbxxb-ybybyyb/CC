import pandas as pd
import numpy as np
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250528
start_date, end_date = 20170110,20241231

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
profit = pd.read_pickle(os.path.join(strategy_path,f'label_df_s1_20170110_20241231.pkl')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

label_pos = profit.copy()[['label_t2o9d1_pos','label_T_close_is_zt','label_Next_close_is_zt']].rename(columns={'label_t2o9d1_pos':'label_t2o9d1'})
label_neg = profit.copy()[['label_t2o9d1_neg','label_T_close_is_zt','label_Next_close_is_zt']].rename(columns={'label_t2o9d1_neg':'label_t2o9d1'})
label_pos['label_Tc2b9'] = label_pos['label_t2o9d1']
label_pos['label_TNo2Tc'] = label_pos['label_t2o9d1']
label_pos['label_TNv2TNo'] = label_pos['label_t2o9d1']
label_neg['label_Tc2b9'] = label_neg['label_t2o9d1']
label_neg['label_TNo2Tc'] = label_neg['label_t2o9d1']
label_neg['label_TNv2TNo'] = label_neg['label_t2o9d1']

IO.pd_hdf5_writer(label_pos, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_labels_file_s1_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(label_neg, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_labels_file_s1_neg.h5', dataset='neptune')
IO.pd_hdf5_writer(label_pos, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(label_neg, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_neg.h5', dataset='neptune')

profit['buy_vol']=np.nan
profit['buy_vwap']=np.nan
profit['pct_T']=np.nan
profit['buy_tick_num']=np.nan
profit['last_buy_time']=np.nan
profit['target_vol']=np.nan
profit['pct_T1']=np.nan
profit['sell_len']=np.nan
profit['date_list']=np.nan
profit['touch_list']=np.nan
profit['vol_list']=np.nan
profit['Sell_ratio']=np.nan
profit_pos = profit.copy()[['buy_vol','buy_amt','buy_vwap','pct_T','buy_tick_num','last_buy_time','target_vol','pct_T1','sell_len','date_list','touch_list','vol_list','Sell_ratio','label_t2o9d1_pos']].rename(columns={'label_t2o9d1_pos':'pct'})
profit_neg = profit.copy()[['buy_vol','buy_amt','buy_vwap','pct_T','buy_tick_num','last_buy_time','target_vol','pct_T1','sell_len','date_list','touch_list','vol_list','Sell_ratio','label_t2o9d1_neg']].rename(columns={'label_t2o9d1_neg':'pct'})

IO.pd_hdf5_writer(profit_pos, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_profit_interval_s1_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(profit_neg, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_profit_interval_s1_neg.h5', dataset='neptune')
IO.pd_hdf5_writer(profit_pos, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_profit_interval_s1_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(profit_neg, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_profit_interval_s1_neg.h5', dataset='neptune')