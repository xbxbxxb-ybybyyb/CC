import pandas as pd
import numpy as np
from sklearn import linear_model
from IO import IO, IO_enums

def standardize(df, ismdf = False):
    # df is a dataframe with columns of stock names and rows are tradingDays
    if ismdf:
        col = df.columns[0]
        df = df[col].unstack()
    df = df.replace(np.inf,np.nan)
    df = df.replace(-np.inf,np.nan)
    m = df.mean(axis = 1)
    s = df.std(axis = 1, ddof = 0)
    df1 = df.subtract(m, axis = 0).divide(s, axis = 0)
    df1[df1 > 3] = 3
    df1[df1 < -3] = -3
    dfnew = df1.multiply(s, axis = 0).add(m, axis = 0)
    dfs = dfnew.subtract(dfnew.mean(axis = 1),axis = 0).divide(dfnew.std(axis = 1, ddof = 0),axis = 0)
    if ismdf:
        dfs = pd.DataFrame(dfs.stack(),columns = [col])
    return dfs

def riskNeutral(mdf, mrisk):
    # mdf is a multiIndex, and mrisk is also a multiIndex
    data = mdf.join(mrisk)
    tradingDays = data.index.get_level_values(level = 0).unique()
    alpname = mdf.columns
    risknames = mrisk.columns
    
    malplist = []
    for td in tradingDays:
        dailyData1 = data.loc[[td]]
        # get res
        dailyData = dailyData1[~dailyData1.isin([np.nan,np.inf,-np.inf]).any(1)]
        
        lm = linear_model.LinearRegression()
        y = dailyData[alpname].values
        
        risknamesrep = []
        risknamesrep[:] = risknames
        
        x = dailyData[risknamesrep].values
        if 'Industry' in risknames:
            risknamesrep.remove('Industry')
            ind = pd.get_dummies(dailyData['Industry'])
            ind.columns = ['ind'+str(int(i)) for i in ind.columns]
            if 'ind0' in ind.columns:
                ind = ind.drop('ind0',1)
            indsum = ind.sum()
            smallnumcols = indsum[indsum < 3].index
            ind = ind.drop(smallnumcols,1)
            
            x = pd.concat([dailyData[risknamesrep],ind],axis = 1).values
        
        lm.fit(x,y)
        res = y - np.dot(x,lm.coef_.T)
        npstd = np.nanstd(res)
        if npstd ==0:
            npstd = 1
        res = (res-np.nanmean(res))/npstd
        alp_df = pd.DataFrame(res,index = dailyData.index,columns = alpname)
        
        # set alp_df to multiIndex
        malplist = malplist + [alp_df]
    malp = pd.concat(malplist)
    return malp

def box_skew_algo(x):
    y = np.array(x)
    x = y[~np.isnan(y)]
    if len(np.unique(x)) < 10:
        return y
    x = np.sort(x)
    md = np.median(x)
    q3 = np.percentile(x,75)
    q1 = np.percentile(x,25)
    iqr = q3 - q1
    rx = np.flip(x, axis=0)
    x, rx = zip(*[(i, j) for i, j in zip(x, rx) if i!=j])
    x = np.split(np.array(x), 2)[1]
    rx = np.split(np.array(rx), 2)[1]
    if len(x) < 5:
        return y
    mc = np.median((x + rx - 2.0 * md) / (x - rx))
    a, b= (3.5, 4) if mc >= 0 else (4, 3.5)
    L = q1 - 1.5 * np.exp(-a * mc) * iqr
    U = q3 + 1.5 * np.exp( b * mc) * iqr
    y[np.array([item < L if not np.isnan(item) else False for item in y])] = L
    y[np.array([item > U if not np.isnan(item) else False for item in y])] = U
    y = (y-np.nanmean(y))/np.nanstd(y)
    return y

def boxskewstandardize(mpd, axis=1):
    pd_raw = mpd[mpd.columns].unstack()
    pd_raw = pd_raw.replace(np.inf,np.nan)
    pd_raw = pd_raw.replace(-np.inf,np.nan)
    if type(pd_raw) == pd.DataFrame:
        # Return copy instead of original
        pd_process = pd_raw.copy()
        pd_df = pd_process.apply(box_skew_algo, axis=axis)
        mpd_df = pd.DataFrame(pd_df.stack(),columns = mpd.columns)
        return mpd_df
    else:
        raise AssertionError

def settnan(malp,pct1,pct2):
    tradingdays = malp.index.get_level_values(level=0)
    alpnewlist = []
    for td in tradingdays:
        tmpalp = malp.loc[td]
        tmpalpnew = tmpalp.sort_values(malp.columns,ascending = False)
        num1 = round(tmpalpnew.shape[0]*pct1)
        num2 = round(tmpalpnew.shape[0]*pct2)
        tmpalpnew.iloc[num1:num2,:] = np.nan
        tmpalpnew = tmpalpnew.reset_index()
        tmpalpnew['dt'] = td
        malpnew = tmpalpnew.set_index(['dt','Ticker'])
        alpnewlist = alpnewlist + [malpnew]
    mdf = pd.concat(alpnewlist,axis = 0)
    return mdf

def industryfilter(mdf, industryNum):
    td = mdf.index.get_level_values(level = 0).unique()
    tradingdays = [i for i in td]
    industry = IO.read_data(tradingdays,columns = ['Industry'],ftype=IO_enums.FType.RISK, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.STYLEFACTOR)
    indname = industry.columns[0]
    data = mdf.join(industry)
    data = data[data[indname] == industryNum]
    data = data[mdf.columns]
    data = data.subtract(data.mean(axis = 0),axis = 1).divide(data.std(axis = 0),axis = 1)
    return data

