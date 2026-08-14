import pandas as pd
import os

emotion_factor_path = '/dfs/user/023859/neptune/20250428/20160101_20250331/'

def emotion_factor_test(emotion_factor_df, factor_name, label_df):
    df = label_df[['label_t2o10dc']].join(emotion_factor_df)
    # df = df.groupby('dt').mean()
    IC = df['label_t2o10dc'].corr(df[factor_name],method='spearman')
    return IC

emotion_factors = os.listdir(emotion_factor_path)
label_df = pd.read_pickle('/dfs/user/023859/neptune/20250428/label_df_detail_20160101_20250331.pkl')

for emotion_factor in emotion_factors:
    emotion_factor_df = pd.read_hdf(emotion_factor_path+emotion_factor)
    factor_name = emotion_factor.split('.')[0]
    IC = emotion_factor_test(emotion_factor_df, factor_name, label_df)
    print(factor_name, IC)