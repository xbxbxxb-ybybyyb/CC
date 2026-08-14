# -*- coding: utf-8 -*-
# @Time    : 2021/5/17 16:05
# @Author  : wangweidi
import pandas as pd
import numpy as np
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()

def update_preclose(today):
    last_tradingday = s.tradingday(today, -2)[0]
    print(last_tradingday)

    df = pd.DataFrame()
    df['code'] = list(s.hset('MARKET', last_tradingday, 'ALLA')['stock'])
    close_df = s.get_factor_value('WIND_AShareEODPrices',
                                  factors=['S_INFO_WINDCODE', 'S_DQ_CLOSE'],
                                  TRADE_DT=['>=%s'%(last_tradingday), '<=%s'%(last_tradingday)]).rename(columns={'S_DQ_CLOSE':'unadjfactor_preclose', 'S_INFO_WINDCODE':'code'}).set_index('code')
    df = df.join(close_df, on='code')
    
#    preclose_df = s.get_factor_value('WIND_AShareEODPrices',
#                                     factors=['S_INFO_WINDCODE', 'S_DQ_PRECLOSE'],
#                                     TRADE_DT=['>=%s'%(today), '<=%s'%(today)]).rename(columns={'S_DQ_PRECLOSE':'RDF_preclose', 'S_INFO_WINDCODE':'code'}).set_index('code')
#    df = df.join(preclose_df, on='code')

    ex_df = s.get_factor_value('WIND_AshareEXRightDividendRecord',
                               factors=['S_INFO_WINDCODE', 'CASH_DIVIDEND_RATIO', 'BONUS_SHARE_RATIO', 'CONVERSED_RATIO'],
                               EX_DATE=['>=%s'%(today), '<=%s'%(today)]).rename(columns={'S_INFO_WINDCODE':'code',
                                                                                         'CASH_DIVIDEND_RATIO':'cash_dividend',
                                                                                         'BONUS_SHARE_RATIO':'share_dividend',
                                                                                         'CONVERSED_RATIO':'share_conversed'})
    if len(ex_df)==0:
        df['self_preclose'] = df['unadjfactor_preclose']
    else:
        df = df.join(ex_df.set_index('code'), on='code')
        df['self_preclose'] = (df['unadjfactor_preclose'] - df['cash_dividend'].fillna(0)) / (1+df['share_dividend'].fillna(0)+df['share_conversed'].fillna(0))
        df['self_preclose'] = df['self_preclose'].apply(lambda x:np.floor(x * 100 +0.5)/ 100)
    if 'RDF_preclose' in df.columns:
        return df[['code', 'unadjfactor_preclose', 'RDF_preclose', 'self_preclose']].set_index('code')
    else:
        return df[['code', 'unadjfactor_preclose', 'self_preclose']].set_index('code')


today = dt.datetime.now().strftime('%Y%m%d')
df = update_preclose(today)
df.to_pickle('/data/group/800463/param/pre_close/%s.pkl'%(today))
#df.to_pickle('/data/user/013600/param/pre_close/%s.pkl'%(today))

df['diff_self_unadj'] = df['self_preclose'] - df['unadjfactor_preclose']
a = df[df['diff_self_unadj'].abs()>0.001]
from xquant.xqutils.helper import link
lm = link.LinkMessage()
message = today + '\npre_close updated, diff num:%d\ncode    unadj_preclose   self_preclose   diff\n'%(len(a))
for index, inf in a.iterrows():
    message += '%s  %.2f     %.2f     %.3f\n'%(index, inf['unadjfactor_preclose'], inf['self_preclose'], inf['diff_self_unadj'])
lm.sendMessage(message)
