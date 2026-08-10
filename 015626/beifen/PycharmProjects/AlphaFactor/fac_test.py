import pandas as pd
import numpy as np
import datetime
import time
import os
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def check_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def adj_date_format(df,format='%Y/%m/%d'):
    # 把index中的datetime转换成str
    output = df.copy()
    output.index = pd.Series(output.index).apply(lambda x:x.strftime(format))
    return output

def get_trading_date_range(sdate,edate,path='Z:/warehouse/prod/CALENDAR/CHINA_STOCK/DAILY/HTSC/CALENDAR_CHINA_STOCK_DAILY_HTSC.h5'):
    # 提取成交日列表
    pd_trading_dates=IO.read_data([sdate,edate],alt=path)
    return pd_trading_dates.sort_index().index.get_level_values('dt').tolist()

def quaterly_to_daily(sdate,edate,df):
    # 把季频数据按公告日期（0331 0630 0930 1231）向下填充映射到每个交易日
    trading_days = get_trading_date_range(sdate,edate)
    merge_dts = pd.Series(trading_days+df.index.tolist()).drop_duplicates().sort_values().tolist()
    tmp = df.reindex(merge_dts).fillna(method='ffill')
    output = tmp.reindex(trading_days)
    return output

def get_data_from_con_forecast(sdate,edate,fac_name,adj=None,table_name='con_forecast_zx'):
    # 提取中信一级行业指数一致预期数据
    ticker_list = ['CC10', 'CC11', 'CC12', 'CC20', 'CC21', 'CC22', 'CC23', 'CC24', 'CC25', 'CC26', 'CC27', 'CC28',
                   'CC30', 'CC31', 'CC32', 'CC33', 'CC34', 'CC35', 'CC36', 'CC37', 'CC40', 'CC41', 'CC42', 'CC50',
                   'CC60', 'CC61', 'CC62', 'CC63', 'CC70']
    name_dict = {'CC10': 'ind1', 'CC11': 'ind2', 'CC12': 'ind3', 'CC20': 'ind4', 'CC21': 'ind5', 'CC22': 'ind6',
                 'CC23': 'ind7', 'CC24': 'ind8', 'CC25': 'ind9', 'CC26': 'ind10', 'CC27': 'ind11', 'CC28': 'ind12',
                 'CC30': 'ind13', 'CC31': 'ind14', 'CC32': 'ind15', 'CC33': 'ind16', 'CC34': 'ind17', 'CC35': 'ind18',
                 'CC36': 'ind19', 'CC37': 'ind20', 'CC40': 'ind21', 'CC41': 'ind29', 'CC42': 'ind22', 'CC50': 'ind23',
                 'CC60': 'ind24', 'CC61': 'ind25', 'CC62': 'ind26', 'CC63': 'ind27', 'CC70': 'ind28'}
    adj_sdate = (pd.to_datetime(sdate,format='%Y%m%d')-datetime.timedelta(days=0 if adj==None else 31*15)).strftime('%Y%m%d') #把起点前移以保证有充分数据做调整
    if table_name == 'con_forecast_zx':
        facpath = 'Z:/warehouse/prod/DATABASE/SUNTIME/con_forecast_zx/con_forecast_zx.h5'
        raw_df = IO.read_data([adj_sdate, str(edate)], columns=[fac_name, 'STOCK_TYPE', 'RPT_DATE', 'RPT_TYPE'], universe=ticker_list, alt=facpath)
        tmp_fac_df = raw_df[(raw_df['STOCK_TYPE']==4)&(raw_df['RPT_TYPE']==4)].sort_index().loc[(slice(None),ticker_list),:].drop(columns=['STOCK_TYPE','RPT_TYPE'])
        # 每年5月1日之前取对上一年年报的预测，之后取对当年年报的预测
        tmp_func = lambda x: 1 if x['RPT_DATE']==(x.name[0].year-1 if x.name[0].month<5 else x.name[0].year) else 0
        tmp_fac_df['flag'] = tmp_fac_df.apply(tmp_func,axis=1,raw=False)
        output = tmp_fac_df[tmp_fac_df['flag']==1][fac_name].unstack().rename(columns=name_dict)
        fac_name = fac_name+'_FY1'
    elif table_name == 'con_forecast_c2_zx':
        facpath = 'Z:/warehouse/prod/DATABASE/SUNTIME/con_forecast_c2_zx/con_forecast_c2_zx.h5'
        raw_df = IO.read_data([adj_sdate, edate], columns=[fac_name, 'STOCK_TYPE'],universe=ticker_list, alt=facpath)
        tmp_fac_df = raw_df[raw_df['STOCK_TYPE']==4].sort_index().drop(columns=['STOCK_TYPE'])
        output = tmp_fac_df[fac_name].unstack().rename(columns=name_dict)
    return output,fac_name

def get_data_from_basic_info(sdate, edate, fac_name, adj=None, facpath='A:/weiyc/data/Industry/basic_info/basic_info.h5'):
    # 提取日频API数据
    ticker_list = ['b101000000000000', 'b102000000000000', 'b103000000000000', 'b104000000000000',
                   'b105000000000000', 'b106000000000000', 'b107000000000000', 'b108000000000000',
                   'b109000000000000', 'b10a000000000000', 'b10b000000000000', 'b10c000000000000',
                   'b10d000000000000', 'b10e000000000000', 'b10f000000000000', 'b10g000000000000',
                   'b10h000000000000', 'b10i000000000000', 'b10j000000000000', 'b10k000000000000',
                   'b10l000000000000', 'b10m000000000000', 'b10n000000000000', 'b10o000000000000',
                   'b10p000000000000', 'b10q000000000000', 'b10r000000000000', 'b10s000000000000',
                   'b10t000000000000']
    name_dict = {'b101000000000000': 'ind1', 'b102000000000000': 'ind2', 'b103000000000000': 'ind3',
                 'b104000000000000': 'ind4', 'b105000000000000': 'ind5', 'b106000000000000': 'ind6',
                 'b107000000000000': 'ind7', 'b108000000000000': 'ind8', 'b109000000000000': 'ind9',
                 'b10a000000000000': 'ind10', 'b10b000000000000': 'ind11', 'b10c000000000000': 'ind12',
                 'b10d000000000000': 'ind13', 'b10e000000000000': 'ind14', 'b10f000000000000': 'ind15',
                 'b10g000000000000': 'ind16', 'b10h000000000000': 'ind17', 'b10i000000000000': 'ind18',
                 'b10j000000000000': 'ind19', 'b10k000000000000': 'ind20', 'b10l000000000000': 'ind21',
                 'b10m000000000000': 'ind29', 'b10n000000000000': 'ind22', 'b10o000000000000': 'ind23',
                 'b10p000000000000': 'ind24', 'b10q000000000000': 'ind25', 'b10r000000000000': 'ind26',
                 'b10s000000000000': 'ind27', 'b10t000000000000': 'ind28'}
    adj_sdate = (pd.to_datetime(sdate, format='%Y%m%d') - datetime.timedelta(days=0 if adj == None else 31 * 15)).strftime('%Y%m%d')  # 把起点前移以保证有充分数据做调整
    raw_df = IO.read_data([adj_sdate, str(edate)], columns=[fac_name],universe=ticker_list, alt=facpath)[fac_name].unstack().rename(columns=name_dict)
    return raw_df

def get_data_from_financial_report(sdate, edate, fac_name, adj=None, table_name='financial_report'):
    # 提取季频API数据
    ticker_list = ['b101000000000000', 'b102000000000000', 'b103000000000000', 'b104000000000000',
                   'b105000000000000', 'b106000000000000', 'b107000000000000', 'b108000000000000',
                   'b109000000000000', 'b10a000000000000', 'b10b000000000000', 'b10c000000000000',
                   'b10d000000000000', 'b10e000000000000', 'b10f000000000000', 'b10g000000000000',
                   'b10h000000000000', 'b10i000000000000', 'b10j000000000000', 'b10k000000000000',
                   'b10l000000000000', 'b10m000000000000', 'b10n000000000000', 'b10o000000000000',
                   'b10p000000000000', 'b10q000000000000', 'b10r000000000000', 'b10s000000000000',
                   'b10t000000000000']
    name_dict = {'b101000000000000': 'ind1', 'b102000000000000': 'ind2', 'b103000000000000': 'ind3',
                 'b104000000000000': 'ind4', 'b105000000000000': 'ind5', 'b106000000000000': 'ind6',
                 'b107000000000000': 'ind7', 'b108000000000000': 'ind8', 'b109000000000000': 'ind9',
                 'b10a000000000000': 'ind10', 'b10b000000000000': 'ind11', 'b10c000000000000': 'ind12',
                 'b10d000000000000': 'ind13', 'b10e000000000000': 'ind14', 'b10f000000000000': 'ind15',
                 'b10g000000000000': 'ind16', 'b10h000000000000': 'ind17', 'b10i000000000000': 'ind18',
                 'b10j000000000000': 'ind19', 'b10k000000000000': 'ind20', 'b10l000000000000': 'ind21',
                 'b10m000000000000': 'ind29', 'b10n000000000000': 'ind22', 'b10o000000000000': 'ind23',
                 'b10p000000000000': 'ind24', 'b10q000000000000': 'ind25', 'b10r000000000000': 'ind26',
                 'b10s000000000000': 'ind27', 'b10t000000000000': 'ind28'}
    if table_name=='financial_report':
        facpath = 'A:/weiyc/data/Industry/financial_report/financial_report.h5'
    elif table_name=='chp3_1':
        facpath = 'D:/indus_test/yb_ht/h5/chp3_1.h5'
    adj_sdate = (pd.to_datetime(sdate,format='%Y%m%d')-datetime.timedelta(days=31*3 if adj==None else 31*15)).strftime('%Y%m%d') #把起点前移以保证有充分数据做填充和调整
    raw_df = IO.read_data([adj_sdate, str(edate)], columns=[fac_name], universe=ticker_list, alt=facpath)[fac_name].unstack().rename(columns=name_dict)
    if adj=='qyoy': #同比
        adj_raw_df = raw_df/raw_df.shift(4)-1
    elif adj=='qoq': #环比
        adj_raw_df = raw_df/raw_df.shift(1)-1
    elif adj=='qydiff': #每年相同季度做一阶差分
        adj_raw_df = raw_df-raw_df.shift(4)
    elif adj=='qhdiff': #相邻季度做一阶差分
        adj_raw_df = raw_df-raw_df.shift(1)
    output = quaterly_to_daily(adj_sdate,edate,raw_df if adj==None else adj_raw_df) # 把季频财务数据按公告日期（0331 0630 0930 1231）向下填充映射到每个交易日
    return output

def get_dly_ind_data(sdate, edate, fac_name, adj=None,table_name='chp3to5_adj'):
    facpath = 'D:/indus_test/yb_ht/h5/'+table_name+'.h5'
    adj_sdate = (pd.to_datetime(sdate, format='%Y%m%d') - datetime.timedelta(days=0 if adj == None else 31 * 15)).strftime('%Y%m%d')  # 把起点前移以保证有充分数据做调整
    raw_df = IO.read_data([adj_sdate, str(edate)], columns=[fac_name], alt=facpath)[fac_name].unstack()
    return raw_df


def cal_quaterly_auto_corr(sdate,edate,fac_name,figpath, facpath='A:/weiyc/data/Industry/financial_report/financial_report.h5'):
    # 计算季频API数据逐期corr
    ticker_list = ['b101000000000000', 'b102000000000000', 'b103000000000000', 'b104000000000000',
                   'b105000000000000', 'b106000000000000', 'b107000000000000', 'b108000000000000',
                   'b109000000000000', 'b10a000000000000', 'b10b000000000000', 'b10c000000000000',
                   'b10d000000000000', 'b10e000000000000', 'b10f000000000000', 'b10g000000000000',
                   'b10h000000000000', 'b10i000000000000', 'b10j000000000000', 'b10k000000000000',
                   'b10l000000000000', 'b10m000000000000', 'b10n000000000000', 'b10o000000000000',
                   'b10p000000000000', 'b10q000000000000', 'b10r000000000000', 'b10s000000000000',
                   'b10t000000000000']
    name_dict = {'b101000000000000': 'ind1', 'b102000000000000': 'ind2', 'b103000000000000': 'ind3',
                 'b104000000000000': 'ind4', 'b105000000000000': 'ind5', 'b106000000000000': 'ind6',
                 'b107000000000000': 'ind7', 'b108000000000000': 'ind8', 'b109000000000000': 'ind9',
                 'b10a000000000000': 'ind10', 'b10b000000000000': 'ind11', 'b10c000000000000': 'ind12',
                 'b10d000000000000': 'ind13', 'b10e000000000000': 'ind14', 'b10f000000000000': 'ind15',
                 'b10g000000000000': 'ind16', 'b10h000000000000': 'ind17', 'b10i000000000000': 'ind18',
                 'b10j000000000000': 'ind19', 'b10k000000000000': 'ind20', 'b10l000000000000': 'ind21',
                 'b10m000000000000': 'ind29', 'b10n000000000000': 'ind22', 'b10o000000000000': 'ind23',
                 'b10p000000000000': 'ind24', 'b10q000000000000': 'ind25', 'b10r000000000000': 'ind26',
                 'b10s000000000000': 'ind27', 'b10t000000000000': 'ind28'}
    adj_sdate = (pd.to_datetime(sdate,format='%Y%m%d')-datetime.timedelta(days=93)).strftime('%Y%m%d') #把起点前移三个月，以提取季度数据填充开始部分的交易日
    raw_df = IO.read_data([adj_sdate, str(edate)], columns=[fac_name], universe=ticker_list, alt=facpath)[fac_name].unstack().rename(columns=name_dict)
    tmp1 = pd.DataFrame(raw_df.corrwith(raw_df.shift(1),axis=1),columns=['Spearman Rank '+'A Quarter'])
    tmp2 = pd.DataFrame(raw_df.rank(axis=1).corrwith(raw_df.rank(axis=1).shift(1),axis=1),columns=['Pearson Linear '+'A Quarter'])
    fac_auto_corr = pd.concat([tmp1,tmp2],axis=1)
    fac_auto_corr.plot()
    plt.title('Factor Auto Correlation',fontsize='large')
    plt.xlabel('Date',fontsize='medium')
    plt.ylabel('Correlation',fontsize='medium')
    plt.savefig(figpath + fac_name +'.png') #存储图片
    plt.close()

def get_zx_cls_data(sdate, edate,holding_period=21, col_name='S_DQ_CLOSE',dpath='Z:/warehouse/prod/DATABASE/WIND/AIndexIndustriesEODCITICS/AIndexIndustriesEODCITICS.h5'):
    # 提取中信一级行业指数的收盘价序列
    sdate = str(sdate)
    edate = min(pd.to_datetime(str(edate), format='%Y%m%d') + datetime.timedelta(days=2*holding_period),datetime.datetime.now()).strftime('%Y%m%d')  # 在当前日期允许的情况下，确保至少往后多取一个持仓周期的行情数据
    ticker_list = ['CI005001.WI', 'CI005002.WI', 'CI005003.WI', 'CI005004.WI', 'CI005005.WI', 'CI005006.WI',
                   'CI005007.WI', 'CI005008.WI', 'CI005009.WI', 'CI005010.WI', 'CI005011.WI', 'CI005012.WI',
                   'CI005013.WI', 'CI005014.WI', 'CI005015.WI', 'CI005016.WI', 'CI005017.WI', 'CI005018.WI',
                   'CI005019.WI', 'CI005020.WI', 'CI005021.WI', 'CI005022.WI', 'CI005023.WI', 'CI005024.WI',
                   'CI005025.WI', 'CI005026.WI', 'CI005027.WI', 'CI005028.WI', 'CI005029.WI']
    name_dict = {'CI005001.WI': 'ind1', 'CI005002.WI': 'ind2', 'CI005003.WI': 'ind3', 'CI005004.WI': 'ind4',
                 'CI005005.WI': 'ind5', 'CI005006.WI': 'ind6', 'CI005007.WI': 'ind7', 'CI005008.WI': 'ind8',
                 'CI005009.WI': 'ind9', 'CI005010.WI': 'ind10', 'CI005011.WI': 'ind11', 'CI005012.WI': 'ind12',
                 'CI005013.WI': 'ind13', 'CI005014.WI': 'ind14', 'CI005015.WI': 'ind15', 'CI005016.WI': 'ind16',
                 'CI005017.WI': 'ind17', 'CI005018.WI': 'ind18', 'CI005019.WI': 'ind19', 'CI005020.WI': 'ind20',
                 'CI005021.WI': 'ind21', 'CI005022.WI': 'ind29', 'CI005023.WI': 'ind22', 'CI005024.WI': 'ind23',
                 'CI005025.WI': 'ind24', 'CI005026.WI': 'ind25', 'CI005027.WI': 'ind26', 'CI005028.WI': 'ind27',
                 'CI005029.WI': 'ind28'}
    cls_df = IO.read_data([sdate, edate], columns=col_name, universe=ticker_list, alt=dpath)[col_name].unstack().rename(columns=name_dict)
    return cls_df

def get_zx_avg_data(sdate,edate,holding_period,dpath='d:/015627/Desktop/industry/avg_pct_chg_CITIC_I.h5'):
    sdate = str(sdate)
    edate = min(pd.to_datetime(str(edate), format='%Y%m%d') + datetime.timedelta(days=2*holding_period),datetime.datetime.now()).strftime('%Y%m%d')# 在当前日期允许的情况下，确保至少往后多取一个持仓周期的行情数据
    pct_chg_df = IO.read_data([sdate, edate], columns=['pct_chg'], alt=dpath)['pct_chg'].unstack()
    cls_df = (1+pct_chg_df/100).cumprod()
    return cls_df

def get_zx_barra(sdate,edate,fac_name,facpath='d:/015627/Desktop/industry/barra_CITIC_I.h5'):
    output = IO.read_data([sdate, edate], columns=[fac_name], alt=facpath)[fac_name].unstack()
    return output

def cumstd(df): #累计标准差
    data = df.copy()
    output = data.apply(lambda x: data.loc[:x.name].std(),axis=1,raw=False)
    return output

def cummean(df): #累计均值
    data = df.copy()
    output = data.apply(lambda x:data.loc[:x.name].mean(),axis=1,raw=False)
    return output

def cumrank(df): #累计计算时序rank
    data = df.copy()
    output = data.apply(lambda x:data.loc[:x.name].rank().iloc[-1],axis=1,raw=False)
    return output

def cumcount(df): #累计时序长度
    data = df.copy()
    output = data.apply(lambda x:data.loc[:x.name].count(),axis=1,raw=False)
    return output

def cal_adj_fac(raw_fac_df,holding_period,adj,annual_num):
    if adj=='zscore':
        adj_fac = (raw_fac_df-cummean(raw_fac_df))/cumstd(raw_fac_df)
    elif adj=='pctrank':
        adj_fac = (cumrank(raw_fac_df)-1)/(cumcount(raw_fac_df)-1)
    elif adj=='yoy':
        adj_fac = raw_fac_df/raw_fac_df.shift(annual_num)-1
    elif adj=='hoh':
        adj_fac = raw_fac_df/raw_fac_df.shift(holding_period)-1
    elif adj=='ydiff':
        adj_fac = raw_fac_df-raw_fac_df.shift(annual_num)
    elif adj=='hdiff':
        adj_fac = raw_fac_df-raw_fac_df.shift(holding_period)
    else: # 若调整方法为qyoy,qoq,qydiff,qhdiff, 则此处不做调整, 因为提取数据时已调整
        adj_fac = raw_fac_df
    return adj_fac

def data_process(sdt,edt,cls_df,raw_fac_df,holding_period,ret_shift,adj,annual_num):
    # 数据预处理
    adj_sdt = max(sdt,raw_fac_df.dropna(how='all',axis=0).index[0]) #回测起点
    adj_edt = min(edt,raw_fac_df.dropna(how='all',axis=0).index[-1]) #回测终点
    trading_days = get_trading_date_range(adj_sdt.strftime('%Y%m%d'),adj_edt.strftime('%Y%m%d'))
    if ret_shift==False:
        tmp_r_df = cls_df.shift(-1*holding_period)/cls_df-1 #holding_period内涨跌幅，向上shift(holding_period)对齐
        hpr_df = tmp_r_df.reindex(trading_days)
        daily_r_df = (cls_df.shift(-1)/cls_df-1).reindex(trading_days) #日度涨跌，向上shift(1)对齐
    elif ret_shift==True:
        tmp_r_df = cls_df.shift(-1*holding_period)/cls_df-1 #holding_period内涨跌幅，向上shift(holding_period+1)对齐
        hpr_df = tmp_r_df.shift(-1).reindex(trading_days)
        daily_r_df = (cls_df.shift(-1)/cls_df-1).shift(-1).reindex(trading_days) #日度涨跌，向上shift(2)对齐
    if adj==None:
        fac_df = raw_fac_df.reindex(trading_days)
    else:
        adj_raw_df = cal_adj_fac(raw_fac_df,holding_period,adj,annual_num)
        fac_df = adj_raw_df.reindex(trading_days)

    sdte,edte = trading_days[0],trading_days[-1]
    return fac_df,hpr_df,daily_r_df,sdte,edte

def cal_ic(fac_df,hpr_df,method):
    # 计算因子ic
    if method=='spearman':
        ics = fac_df.rank(axis=1).T.corrwith(hpr_df.rank(axis=1).T)
    elif method=='pearson':
        ics = fac_df.T.corrwith(hpr_df.T)
    output = pd.DataFrame(ics,columns=['ic'])
    return output

def get_group_label(data,group_num):
    # 生成分组标签
    output = data.copy()
    output.loc[:] = np.nan
    for i in range(group_num):
        if i==group_num-1:
            output[(data >= data.quantile(1/group_num*i))&(data <= data.quantile(1/group_num*(i+1)))] = 'group'+str(i+1)
        else:
            output[(data >= data.quantile(1/group_num*i))&(data < data.quantile(1/group_num*(i+1)))] = 'group'+str(i+1)
    return output

def group_test(fac_df,daily_r_df,group_num,holding_period,ret_shift):
    # 分组测试，返回分组标签和分组逐期收益
    tmp = fac_df.rank(axis=1)
    test_dtes = fac_df.index[range(0,len(fac_df),holding_period)] # 抽取调仓时点
    # 计算分组标签，保证持有期内标签不变
    group_df = tmp.loc[test_dtes].apply(get_group_label,args=(group_num,),axis=1,raw=False).reindex(fac_df.index).fillna(method='ffill')
    r_list = []
    for i in range(group_num): #计算每组的日度收益
        r_list.append(pd.DataFrame(daily_r_df[group_df=='group'+str(i+1)].mean(axis=1),columns=['group'+str(i+1)]))
    group_r = pd.concat(r_list,axis=1).shift(1) #把收益对齐到真实日期
    group_r.iloc[0]=0
    if ret_shift==False:
        group_df = group_df.shift(1) #把分组对齐到真实日期
    else:
        group_df = group_df.shift(2)  # 把分组对齐到真实日期
    return group_df,group_r

def cal_yly_r(group_r,annual_num):
    # 计算分年度收益
    yrs_list = group_r.index.year.unique().tolist()
    tmp_output = []
    for yr in yrs_list:
        tmp = group_r[group_r.index.year==yr]
        tr = tmp.mean()*annual_num
        tvol = tmp.std()*np.sqrt(annual_num)
        tSR = tr/tvol
        tmpA = pd.concat([pd.DataFrame(['Return'],index=['indicator'],columns=[yr]),pd.DataFrame(tr,columns=[yr])]).T
        tmpB = pd.concat([pd.DataFrame(['Volatility'],index=['indicator'],columns=[yr]),pd.DataFrame(tvol,columns=[yr])]).T
        tmpC = pd.concat([pd.DataFrame(['Sharpe Ratio'],index=['indicator'],columns=[yr]),pd.DataFrame(tSR,columns=[yr])]).T
        tmp_output.append(pd.concat([tmpA,tmpB,tmpC]))
    output = pd.concat(tmp_output)
    output.index.name = 'year'
    return output

def cal_indicators(ic_df,group_r,group_num,fac_auto_corr,annual_num):
    # 计算测试结果评价指标
    ic_mean = ic_df.mean()[0]
    ic_std = ic_df.std()[0]
    icir = ic_mean/ic_std
    rank_ac_med = fac_auto_corr.iloc[:,1].median()
    top_r = group_r['group'+str(group_num)].mean()*annual_num if ic_mean>0 else group_r['group1'].mean()*annual_num #头部组合年化收益
    top_vol = group_r['group'+str(group_num)].std()*np.sqrt(annual_num) if ic_mean>0 else group_r['group1'].std()*np.sqrt(annual_num) #头部组合年化波动率
    top_sr = top_r/top_vol #头部组合年化夏普比率
    hedge_r = group_r['hedge'].mean()*annual_num #多空对冲年化收益
    hedge_vol = group_r['hedge'].std()*np.sqrt(annual_num) #多空对冲年化波动
    hedge_ir = hedge_r/hedge_vol #多空对冲信息比率
    output = pd.DataFrame([ic_mean,ic_std,icir,rank_ac_med,hedge_r,hedge_vol,hedge_ir,top_r,top_vol,top_sr],index=['ic mean','ic std','icir','rank_autocorr_med','hedge return','hedge vol','IR','return(annual)','vol(annual)','sharpe ratio'],columns=['params'])
    return output

def cal_auto_corr(fac_df,holding_period):
    tmp1 = pd.DataFrame(fac_df.corrwith(fac_df.shift(holding_period),axis=1),columns=['Pearson Linear ' +str(holding_period)+' Days'])
    tmp2 = pd.DataFrame(fac_df.rank(axis=1).corrwith(fac_df.rank(axis=1).shift(holding_period),axis=1),columns=['Spearman Rank '+str(holding_period)+ ' Days'])
    fac_auto_corr = pd.concat([tmp1,tmp2],axis=1)
    return fac_auto_corr

def get_fac_name(fac_name,adj,mappath='d:/indus_test/fac_def.xlsx'): # 得到因子的中文名，如果对因子做了调整给其加上相应后缀
    map = pd.read_excel(mappath,index_col=0,encoding='GB2312')
    if adj==None:
        fac_def = map.loc[fac_name]['def']
        name = fac_name
    else:
        fac_def = map.loc[fac_name]['def']+'_'+adj
        name = adj+'_'+fac_name
    return name,fac_def

def save_results(fac_name,fac_df,ic_df,ic_method,group_df,group_r,group_nav,yly_group_results,fac_auto_corr,outpath,params,indicators,holding_period):
    # 存储测试结果
    # 1.生成excel
    file_path = outpath+fac_name+'/'
    check_dir(file_path)
    writer = pd.ExcelWriter(file_path+fac_name+'_'+params.loc['start date','params'][:6]+'_to_'+params.loc['end date','params'][:6]+'.xlsx', engine='xlsxwriter')
    mdf = pd.concat([params,indicators])
    mdf.to_excel(writer, sheet_name='params&indicators')
    adj_date_format(ic_df).to_excel(writer, sheet_name=ic_method+' ic')
    yly_group_results.to_excel(writer, sheet_name='yearly group results')
    adj_date_format(group_r).to_excel(writer, sheet_name='group r')
    adj_date_format(group_nav).to_excel(writer, sheet_name='group nav')
    adj_date_format(group_df).to_excel(writer, sheet_name='group labels')
    adj_date_format(fac_auto_corr).to_excel(writer,sheet_name='factor_auto_correlation')
    writer.save()
    # 2.生成图片
    fig = plt.figure(figsize=[9,30],dpi=200)
    # 图一：ic时间序列柱状图
    ax1 = fig.add_subplot(5,1,1)
    ax1.bar(ic_df.index.tolist(), np.array(ic_df['ic']),color='dodgerblue')
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xlabel('Date',fontsize='medium')
    plt.ylabel('IC',fontsize='medium')
    plt.title('Time Series of IC',fontsize='large')
    plt.xticks(ic_df.index[range(0,len(ic_df),6*holding_period)], rotation=45,fontsize='medium')
    plt.subplots_adjust(top=0.95,hspace=0.3)
    # 图二：分组累计收益曲线
    ax2 = fig.add_subplot(5,1,2)
    ax2.plot(group_nav-1)
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xticks(group_nav.index[range(0,len(group_nav),6*holding_period)], rotation=45,fontsize='medium')
    plt.legend(group_nav.columns,ncol=2,fontsize='small')
    plt.title('Segment Return',fontsize='large')
    plt.xlabel('Date',fontsize='medium')
    plt.ylabel('Cumulative Return',fontsize='medium')
    plt.subplots_adjust(hspace=0.3)
    # 图三：分年度收益率柱状图
    ax3 = fig.add_subplot(5,1,3)
    yly_return = yly_group_results[yly_group_results['indicator']=='Return'].drop(columns=['indicator'])
    x = np.arange(len(yly_return))
    bar_width = 0.15
    tick_label = pd.Series(yly_return.index).apply(lambda x:str(x)).tolist()
    for i in range(yly_return.shape[1]):
        plt.bar(x+i*bar_width, list(yly_return.iloc[:,i]), bar_width, align="center",alpha=0.5)
    plt.legend(yly_return.columns.tolist(),ncol=2,fontsize='small')
    plt.xticks(x + int(params.loc['group num'][0]/2)*bar_width , tick_label,fontsize='medium')
    plt.xlabel('Year',fontsize='medium')
    plt.ylabel('Return(annual)',fontsize='medium')
    plt.title('Annual Return by Year',fontsize='large')
    plt.subplots_adjust(hspace=0.3)
    # plt.subplots_adjust(bottom=0.05,hspace=0.3)
    # 图四:因子时间序列图
    ax4 = fig.add_subplot(5,1,4)
    fac_df.iloc[range(0,len(fac_df),holding_period)].plot(ax=ax4,legend=False)
    ax4.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xticks(fac_df.index[range(0,len(fac_df),6*holding_period)], rotation=45,fontsize='medium')
    # plt.legend(fac_df.columns,ncol=5,fontsize='small')
    plt.title('Time Series of Factor Value',fontsize='large')
    plt.xlabel('Date',fontsize='medium')
    plt.ylabel('Factor Value',fontsize='medium')
    plt.subplots_adjust(hspace=0.3)
    # 图五:因子自相关性时序图
    ax5 = fig.add_subplot(5,1,5)
    fac_auto_corr.iloc[range(0,len(fac_auto_corr),holding_period)].plot(ax=ax5)
    ax5.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xticks(fac_auto_corr.index[range(0,len(fac_auto_corr),6*holding_period)], rotation=45,fontsize='medium')
    # plt.legend(fac_df.columns,ncol=5,fontsize='small')
    plt.title('Factor Auto Correlation (median of rank corr: '+str(round(fac_auto_corr.iloc[:,1].median()*100,2))+'%)',fontsize='large')
    plt.xlabel('Date',fontsize='medium')
    plt.ylabel('Correlation',fontsize='medium')
    plt.subplots_adjust(bottom=0.05,hspace=0.3)
    plt.savefig(file_path + fac_name+'_'+params.loc['start date','params'][:6]+'_to_'+params.loc['end date','params'][:6] +'.png') #存储图片
    plt.close()
    print('Test results for '+fac_name+' have been saved in '+outpath)

def workflow(outpath,fac_name,cls_df,raw_fac_df,sdt,edt,adj,group_num=5,holding_period=21,ret_shift=True,ic_method='spearman',interest_type='simple',annual_num=252):
    fac_df,hpr_df,daily_r_df,sdte,edte = data_process(sdt,edt,cls_df,raw_fac_df,holding_period,ret_shift,adj,annual_num) #数据预处理
    ic_df = cal_ic(fac_df,hpr_df,ic_method) #计算ic序列
    group_df, group_r = group_test(fac_df,daily_r_df,group_num,holding_period,ret_shift) #计算分组收益
    group_r['hedge'] = np.sign(ic_df.mean()[0])*(group_r['group'+str(group_num)]-group_r['group1']) #计算多空收益
    group_nav = group_r.cumsum()+1 #计算分组单利净值
    yly_group_results = cal_yly_r(group_r,annual_num) #计算分年度分组收益情况
    fac_auto_corr = cal_auto_corr(fac_df,holding_period) #计算因子值自相关性
    adj_fac_name,fac_def = get_fac_name(fac_name,adj) # 提取因子的定义，如果因子值有调整对因子名也做调整
    params = pd.DataFrame([adj_fac_name,fac_def,sdte.strftime('%Y%m%d'),edte.strftime('%Y%m%d'),holding_period,ic_method,group_num,interest_type],columns=['params'],index=['fac_name','def','start date','end date','holding period','ic method','group num','interest type']) #测试使用的参数
    indicators = cal_indicators(ic_df,group_r,group_num,fac_auto_corr,annual_num) #计算测试结果相关指标
    save_results(adj_fac_name,fac_df, ic_df, ic_method, group_df, group_r, group_nav, yly_group_results, fac_auto_corr, outpath, params,indicators,holding_period) #存储测试结果

if __name__ == "__main__":
    a = time.time()
    # 参数定义
    # outpath = 'd:/indus_test/correct2/cfc/'
    outpath = 'd:/indus_test/yb_ht/results_adj/'
    fac_name = 'C13'
    group_num = 5
    holding_period = 10
    sdate, edate = 20140101,20191025
    ret_shift = True
    #  adj取值说明：
    # 'None' 不做调整, 'zscore' 时序标准化, 'pctrank' 时序分位, 'yoy' 同比, 'hoh' 环比, 'ydiff' 一阶差分类同比, 'hdiff' 一阶差分类环比
    # 'qyoy' 季度数据同比, 'qoq' 季度数据环比, 'qydiff' 季度数据一阶差分类同比 , 'qhdiff'季度数据一阶差分类环比
    adj = None
    sdt, edt = pd.to_datetime(str(sdate),format='%Y%m%d'),pd.to_datetime(str(edate),format='%Y%m%d')
    # 数据提取
    # raw_fac_df,fac_name = get_data_from_con_forecast(sdate,edate,fac_name,adj) # 提取表 con_forecast_zx 中的数据
    raw_fac_df,_ = get_data_from_con_forecast(sdate,edate,fac_name,adj,'con_forecast_c2_zx') # 提取表 con_forecast_c2_zx 中的数据
    # raw_fac_df = get_data_from_basic_info(sdate, edate, fac_name,adj) # 提取API日频数据
    # raw_fac_df = get_data_from_financial_report(sdate, edate, fac_name, adj) # 提取API季频数据
    # raw_fac_df = get_zx_barra(sdate,edate,fac_name) # 提取barra风格数据

    # raw_fac_df = get_dly_ind_data(sdate,edate,fac_name,adj) #提取chp3~chp5中的日度数据
    # raw_fac_df = get_dly_ind_data(sdate, edate, fac_name, adj,table_name='compds')  # 提取研报复合因子
    cls_df = get_zx_cls_data(sdate,edate,holding_period) # 提取中信一级行业指数收盘价
    # cls_df = get_zx_avg_data(sdate,edate,holding_period) # 提取中信一级行业指数收盘价,个股涨跌平权
    # 因子测试
    workflow(outpath, fac_name, cls_df, raw_fac_df ,sdt ,edt, adj, group_num, holding_period,ret_shift)
    b = time.time()
    print('finished in '+str((b-a)/60)+' min')

