from xquant.thirdpartydata.factordata import FactorData
import pandas as pd
import datetime
import time
from joblib import Parallel, delayed


def get_data(date, columns, save_path):
    s = FactorData()
    df = s.get_factor_value("GOGOAL2_FID_STOCKMEDIACOUNT", factors=columns, RECORDTIME=date)
    print(date, df.shape)
    df.to_pickle(f'{save_path}{date}.pkl')
    return
start_date = '20230605' # 20230605
end_date = '20250325'
save_path = '/dfs/user/015585/20250417_飞笛媒体数据/'
columns = ['TRADINGCODE','MEDIANEWSNUM', 'SOCIALNEWSNUM', 'MEDIANUM', 'BIGVSUM', 'INTERACTSUM','RECORDTIME']
date_list = [pd.Timestamp(start_date) + datetime.timedelta(days=i) for i in range((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1)]
date_list = [x.strftime('%Y%m%d') for x in date_list]

factor_df_list = Parallel(n_jobs=8)(delayed(get_data)(date, columns, save_path) for date in date_list)






# print(df.head())