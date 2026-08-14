import pandas as pd
from h5data.IO import IO

labels_file_pos = pd.read_hdf('/dfs/user/023859/share_file/for_skk/neptune/20250609/zz1000_labels_file_s1_short_term.h5')
labels_file_neg = pd.read_hdf('/dfs/user/023859/share_file/for_skk/neptune/20250609/zz1000_labels_file_s1_short_term_neg.h5')

profit_pos = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/zz1000_profit_interval.h5')
profit_neg = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/neg/zz1000_profit_interval.h5')

labels_file_pos['label_pct'] = profit_pos['pct']
labels_file_pos['label_Tc2b10'] = profit_pos['pct']
labels_file_pos['label_TNo2Tc'] = profit_pos['pct']
labels_file_pos['label_TNv2TNo'] = profit_pos['pct']
labels_file_pos = labels_file_pos[~labels_file_pos['label_pct'].isna()]

labels_file_neg['label_pct'] = profit_neg['pct']
labels_file_neg['label_Tc2b10'] = profit_neg['pct']
labels_file_neg['label_TNo2Tc'] = profit_neg['pct']
labels_file_neg['label_TNv2TNo'] = profit_neg['pct']
labels_file_neg = labels_file_neg[~labels_file_neg['label_pct'].isna()]

IO.pd_hdf5_writer(labels_file_pos, hdf5='/dfs/user/023859/share_file/for_wj/neptune/20250609_a/zz1000_labels_file_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(labels_file_neg, hdf5='/dfs/user/023859/share_file/for_wj/neptune/20250609_a/zz1000_labels_file_neg.h5', dataset='neptune')

