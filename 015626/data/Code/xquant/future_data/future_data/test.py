import pandas as pd
a = pd.read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE_IM/temp_data/IM_cfg_hf_20201201_20220721.pkl')

df = a.reset_index().set_index(['dt','Ticker']).sort_index()
#a.to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE_IM/temp_data/IM_cfg_hf_20201201_20220721_sortindex.pkl')

#df = pd.read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE_IM/temp_data/IM_cfg_hf_20170104_20210101_sortindex.pkl')
cols = df.columns.tolist()
print('heihei')

for col in cols:
    print(col)
    df[col].unstack().between_time('930','1456').sort_index().to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE_IM/cfg_hf_data_zz1000/%s.pkl' % (col+'_1000'))