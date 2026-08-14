# @Time : 2020/10/14 16:59
# @Author : Zhichen Lu
# @File : label_calc.py
import pandas as pd
import numpy as np
from System.LoadLabel.LabelDataSet import LabelDataSet
from StrongStockModel.conf.path_config import label_path

source_path = '/data/group/800319/junkBigFactor/'
# file_list = os.listdir(source_path)

date_list = np.load(source_path+'date_list.npy')
code_list = np.load(source_path+'code_list.npy')
time_list = np.load(source_path+'time_list.npy')

lds = LabelDataSet(20140101,20191231)
label = lds.calc_pctchg_N(code_list.tolist(),start_date=date_list[0],end_date=date_list[-1],load_local=False)
label.index = pd.MultiIndex.from_tuples(label.index.tolist())
label_5min = label.swaplevel(0,1).loc[time_list.tolist()].swaplevel(0,1)
label_5min.to_hdf(label_path+'pct_240m_freq_5min.h5','pct_240m_freq_5min',format='t')


start_date = 20160205
end_date = 20170309
start = date_list.tolist().index(start_date) * 48
end = date_list.tolist().index(end_date) * 48 + 48

part = pd.read_hdf(label_path+'pct_240m_freq_5min.h5','pct_240m_freq_5min',start=start,stop=end)
