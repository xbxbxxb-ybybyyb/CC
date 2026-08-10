from IO import IO, IO_enums
from utility import dt, alputils, utility
import numpy as np
import pandas as pd
import os
from alpha1 import taskpath

tp = taskpath.TaskPath()
def TSRANK(A,n):
    x,y = A.shape
    ret = []
    for i in range(0,x):
        if i<n-1:
            ret.append([np.nan for i in range(y)])
        else:
            a = A[i-n+1:i+1].rank(pct=True).iloc[-1]
            ret.append(a.values.tolist())
    rn = pd.DataFrame(ret)
    rn = rn.replace([np.inf,-np.inf],[np.nan,np.nan])
    rn.index = A.index
    rn.columns = A.columns
    return rn

def REGSI(Y,X):
    h,l = Y.shape
    resi = np.zeros([h,l])
    
    for i in range(0,h):
        y = Y.iloc[i,:]
        x = X.iloc[i,:]
        mat = np.vstack([x,np.ones(len(x)),y]).T
        mat1 = mat[~np.isnan(mat.sum(axis=1)),:]
        import sklearn.linear_model as lm
        glm = lm.LinearRegression()
        glm_r = glm.fit(mat1[:,0:2],mat1[:,-1])
        coef = glm_r.coef_.T
        res = mat[:,-1] - np.dot(mat[:,0:2],coef)
        resi[i,:] =  res
    
    rn = pd.DataFrame(resi)
    rn = rn.replace([np.inf,-np.inf],[np.nan,np.nan])
    rn.columns = Y.columns
    rn.index = Y.index
    return rn

def CORR(a,b,n):
    x,y = a.shape
    ret = []
    for i in range(0,x):
        #print(i)
        if i<n-1:
            ret.append([np.nan for i in range(y)])
        else:
            cov = (a[i-n+1:i+1]*b[i-n+1:i+1]).mean()-a[i-n+1:i+1].mean()*b[i-n+1:i+1].mean()
            std_a = (a[i-n+1:i+1]**2).mean()-a[i-n+1:i+1].mean()**2
            std_b = (b[i-n+1:i+1]**2).mean()-b[i-n+1:i+1].mean()**2
            cor = cov/np.sqrt(std_a*std_b )
            ret.append(cor.values.tolist())
    rn = pd.DataFrame(ret)
    rn = rn.replace([np.inf,-np.inf],[np.nan,np.nan])
    rn.columns = a.columns
    rn.index = a.index
    return rn

def trans(df):
	df1 = df.copy()
	d = df1.quantile(0.96)
	id1 = df1 > d
	id2 = df1 <= d
	df1[id1] = 1
	df1[id2] = 0
	return df1

class DailyPvAlp:
    def __init__(self, stDate, edDate, universe = 'alpha_universe',indexName = None):
        self.stDate = stDate
        self.edDate = edDate
        self.universe = universe
        self.savepath = os.path.join(tp.featurepath,'pv_alpuniv')
        if not os.path.exists(self.savepath):
            os.makedirs(self.savepath)
        
        self.indexName = indexName
        if indexName is None:
            self.index = IO.read_data([stDate,edDate], ftype=IO_enums.FType.UNIV, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.OPTM)
        else:
            self.index = IO.read_data([stDate,edDate],alt = indexName)
            
        self.index = self.index[[self.universe]]
        self.risk = IO.read_data([stDate,edDate],columns = ['Size','Industry'],\
                         ftype=IO_enums.FType.RISK, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.STYLEFACTOR)
    
    def h5write(self, alpha_pd):
        alpName = alpha_pd.columns[0]
        resultName = os.path.join(self.savepath, alpName + '.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        if alpha_pd.shape[0] < 100:
            raise('Something wrong with data!')
        IO.pd_hdf5_writer(alpha_pd, resultName, alpName, append = append)
    
    
    def genalp(self):
        self.genalp1()
        self.genalp3()
        self.genalp4()
        self.genalp5()
        self.genalp6()
        self.genalp7()
        self.genalp8()
        self.genalp9()
        self.genalp10()
        self.genalp11()
        self.genalp12()
        self.genalp13()
        self.genalp14()
        self.genalp15()
        self.genalp16()
        self.genalp17()
        self.genalp18()
        self.genalp19()
        self.genalp20()
        self.genalp21()
        self.genalp22()
        self.genalp23()
        self.genalp24()
        self.genalp25()
        self.genalp26()
        self.genalp27()
        self.genalp28()
        self.genalp29()
        self.genalp30()
        self.genalp31()
        self.genptn()
        self.gentcn()
        self.gencore()
        self.genz1()
        self.gendwf()
        self.genM()
        self.genM_high()
        
    # depend on zsj
    def genalpz(self):
        self.genalpzf5b()
    
    def genalp1(self, alpName = 'alp1_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['pct_chg','turn','volume'],\
                       ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        index = self.index
        data = h5_data.join(index)
        data = data[data[self.universe] == 1]
    
        RET = data['pct_chg'].unstack()/100.0
        TURN = data['turn'].unstack()/100.0
        VOLUME = data['volume'].unstack()/100
        
        RET[VOLUME == 0] = np.nan
        TURN[VOLUME == 0] = np.nan
        
        alp1_zf = abs(RET) - TURN
        
        alp1_zf[alp1_zf > 0.015] = np.nan
        alp1_zf[alp1_zf < -0.2] = np.nan
        
        alp1_zf = alp1_zf.replace(np.inf, np.nan)
        alp1_zf = alp1_zf.replace(-np.inf, np.nan)
        alp1_zf = alputils.standardize(alp1_zf)
        
        malp1_zf = pd.DataFrame(alp1_zf.stack(),columns = [alpName])
        
        # riskNeutral
        mrisk = self.risk
        malp1_zf = alputils.riskNeutral(malp1_zf,mrisk)    
        malp1_zf = malp1_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp1_zf)
    
    def genalp3(self,alpName = 'alp3_alpuniv'):
        W = 20
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['amt'], ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace(0,np.nan)
        AMT = np.log(h5_data['amt'].unstack())
        AMT = AMT.replace(np.inf,np.nan)
        AMT = AMT.replace(-np.inf,np.nan)
        
        alp3_zf = AMT.rolling(window = W).std()
        alp3_zf = alp3_zf[str(self.stDate):str(self.edDate)]
        alp3_zf = -alp3_zf
        
        alp3_zf[AMT == 0] = np.nan
        
        malp3_zf = pd.DataFrame(alp3_zf.stack(),columns = [alpName])
        malp3_zf = malp3_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]        
        
        data = malp3_zf.join(self.index)
        data = data[data[self.universe] == 1]
        data = data.replace(0,np.nan)
        
        alp3_zf = data[alpName].unstack()
        alp3_zf = alputils.standardize(alp3_zf)
        
        # save data        
        malp3_zf = pd.DataFrame(alp3_zf.stack())
        malp3_zf.columns = [alpName]
        
        malp3_zf = alputils.riskNeutral(malp3_zf,self.risk)
        malp3_zf = malp3_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp3_zf = malp3_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp3_zf)
            
    def genalp4(self, alpName = 'alp4_alpuniv'):    
        W = 21
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn'],ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        TURN = h5_data['turn'].unstack()
        TURN = TURN.replace(np.inf,np.nan)
        TURN = TURN.replace(np.inf,np.nan)
        
        TURN_s = TURN.rolling(window = W).std()
        TURN_m = TURN.rolling(window = W).mean()
        
        TURN_m = TURN_m.replace(0,np.nan)
        
        alp4_zf = TURN_s/TURN_m
        
        alp4_zf = alp4_zf[str(self.stDate):str(self.edDate)]
        alp4_zf = -alp4_zf
        
        malp4_zf = pd.DataFrame(alp4_zf.stack(), columns = [alpName])
        malp4_zf = malp4_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp4_zf.join(self.index)
        data = data[data[self.universe] == 1]
        
        alp4_zf = data[alpName].unstack()
        alp4_zf = alputils.standardize(alp4_zf)
        
        malp4_zf = pd.DataFrame(alp4_zf.stack(),columns = [alpName])
        
        malp4_zf = alputils.riskNeutral(malp4_zf,self.risk)
        malp4_zf = malp4_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp4_zf = malp4_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp4_zf)

    def genalp5(self,alpName = 'alp5_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['turn','total_shares','close'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
                             
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        
        data = data.replace(np.inf,np.nan)
        data = data.replace(-np.inf,np.nan)
        
        TURN = data['turn'].unstack()
        TURN[TURN==0] = np.nan
        TMCAP = np.log(data['total_shares']*data['close']).unstack()
        
        alp5_zf = REGSI(TURN,TMCAP)
        alp5_zf = -alp5_zf
        
        alp5_zf = alputils.standardize(alp5_zf)
        
        malp5_zf = pd.DataFrame(alp5_zf.stack(),columns = [alpName])
        malp5_zf = alputils.riskNeutral(malp5_zf,self.risk)
        malp5_zf = malp5_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp5_zf)

    def genalp6(self,alpName = 'alp6_alpuniv'):    
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn'], ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        TURN = h5_data['turn'].unstack()/100.0
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        TURN = TURN.sort_index()
        alp6_zf = TURN.shift(W)
        alp6_zf[alp6_zf < 0.0155] = np.nan
        alp6_zf = alp6_zf[str(self.stDate):str(self.edDate)]
        alp6_zf = -alp6_zf
        # filter index
        malp6_zf = pd.DataFrame(alp6_zf.stack(),columns = [alpName])
        malp6_zf = malp6_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp6_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp6_zf = data[alpName].unstack()
        #standardize
        alp6_zf = alputils.standardize(alp6_zf)
        malp6_zf = pd.DataFrame(alp6_zf.stack(),columns = [alpName])
        # riskNeutral
        malp6_zf = alputils.riskNeutral(malp6_zf,self.risk)
        malp6_zf = malp6_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp6_zf = malp6_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp6_zf)
    
    def genalp7(self,alpName = 'alp7_alpuniv'):    
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]    
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn','pct_chg'],ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        TURN = h5_data['turn'].unstack()/100.0
        RET = h5_data['pct_chg'].unstack()/100.0
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        RET = RET.replace([np.inf,-np.inf],np.nan)
        TURN = TURN.sort_index()
        RET = RET.sort_index()
        
        alp_zf = TURN + RET.shift(W)
        alp_zf[alp_zf < 0] = np.nan
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp8(self,alpName = 'alp8_alpuniv'):    
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]        
        h5_data = IO.read_data([sdate,self.edDate],columns = ['turn','total_shares','free_float_shares','close'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data['totalmktcap'] = h5_data['close']*h5_data['total_shares']
        h5_data['freefloatcap'] = h5_data['close']*h5_data['free_float_shares']
        
        TURN = h5_data['turn'].unstack()/100.0
        TCAP = h5_data['totalmktcap'].unstack()
        FFCAP = h5_data['freefloatcap'].unstack()
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        TCAP = TCAP.replace([0,np.inf,-np.inf],np.nan)
        FFCAP = FFCAP.replace([0,np.inf,-np.inf],np.nan)
        
        TURN = TURN.sort_index()
        TCAP = np.log(TCAP).sort_index()
        #FFCAP = np.log(FFCAP).sort_index()
        #TDF = TCAP/FFCAP
        
        alp_zf = TCAP - TCAP.shift(W) + TURN
        
        alp_zf[alp_zf < 0.01] = np.nan
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')    
        self.h5write(malp_zf)

    def genalp9(self,alpName = 'alp9_alpuniv'):
        W = 5
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn'], ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        TURN = h5_data['turn'].unstack()/100.0
        TURN = TURN.sort_index()
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        
        alp_zf = np.abs(TURN - TURN.shift(5))
        
        alp_zf[alp_zf < 0.001] = np.nan
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]                     
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp10(self,alpName = 'alp10_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn'], ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        TURN = h5_data['turn'].unstack()/100.0
        TURN = TURN.sort_index()
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        
        alp_zf = np.abs(TURN - TURN.shift(W))
        
        alp_zf[alp_zf < 0.0005] = np.nan
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp11(self,alpName = 'alp11_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['turn','pct_chg','close','total_shares','free_float_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        h5_data['totalmktcap'] = h5_data['close']*h5_data['total_shares']
        h5_data['ffmktcap'] = h5_data['close']*h5_data['free_float_shares']
        
        TURN = h5_data['turn'].unstack()/100.0
        RET = h5_data['pct_chg'].unstack()/100.0
        TMCAP = h5_data['totalmktcap'].unstack()
        FFMCAP = h5_data['ffmktcap'].unstack()
        
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        RET = RET.replace([np.inf,-np.inf],np.nan)
        TMCAP = TMCAP.replace([np.inf,-np.inf],np.nan)
        FFMCAP = FFMCAP.replace([np.inf,-np.inf],np.nan)
        TDF = np.log(TMCAP)/np.log(FFMCAP)
        
        alp_zf = (RET+TURN)*TDF
        
        alp_zf[alp_zf < 0.01] = np.nan
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
                             
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp12(self,alpName = 'alp12_alpuniv'):    
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['turn','close','total_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data['totalmktcap'] = h5_data['close']*h5_data['total_shares']
        
        TURN = h5_data['turn'].unstack()/100.0
        TURN = TURN.sort_index()
        TURN = TURN.replace([0,np.inf,-np.inf],np.nan)
        
        TMCAP = h5_data['totalmktcap'].unstack()
        TMCAP = TMCAP.sort_index()
        TMCAP = TMCAP.replace([0,np.inf,-np.inf],np.nan)
        
        alp_zf = np.log(TMCAP)+TURN
        alp_zf[alp_zf<5] = np.nan
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
                             
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp13(self,alpName = 'alp13_alpuniv'):    
        W = 121
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        
        h5_data = IO.read_data([sdate,self.edDate],columns = ['turn','high','low'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        
        TURN = h5_data['turn'].unstack()/100.0
        HIGH = h5_data['high'].unstack()
        LOW = h5_data['low'].unstack()
        HML = HIGH - LOW
        
        alp_zf = HML.rolling(window = W).min() + TURN
        alp_zf[alp_zf < 0.013] = np.nan
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp14(self,alpName = 'alp14_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate],columns = ['turn','amt'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        
        TURN = h5_data['turn'].unstack()/100.0
        AMT = h5_data['amt'].unstack()
        AMT = np.sqrt(AMT)
        
        alp_zf = TSRANK(AMT,W) + TURN
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]                     
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp15(self,alpName = 'alp15_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate],columns = ['vwap','amt'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        
        VWAP = h5_data['vwap'].unstack()
        AMT = h5_data['amt'].unstack()
        AMT = np.sqrt(AMT)
        
        alp_zf = (AMT+VWAP).rolling(window = W).std()
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)
    
    def genalp16(self,alpName = 'alp16_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate],columns = ['pct_chg','turn','close','total_shares','free_float_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        data['totalmktcap'] = data['close']*data['total_shares']
        data['ffmktcap'] = data['close']*data['free_float_shares']
        data['tdf'] = np.log(data['totalmktcap'])/np.log(data['ffmktcap'])
        data = data.replace([0,np.inf,-np.inf],np.nan)
        RET = data['pct_chg'].unstack()
        TURN = data['turn'].unstack()
        TDF = data['tdf'].unstack()
        
        alp_zf = np.abs(REGSI(RET,REGSI(TURN,TDF)))
        alp_zf = -alp_zf
        
        malp = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        # filter index
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis =0, how = 'all')
        self.h5write(malp_zf)

    def genalp17(self,alpName = 'alp17_alpuniv'):
        W = 20
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]        
        h5_data = IO.read_data([sdate,self.edDate],columns = ['close','turn','adjfactor'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        h5_data['adjclose'] = h5_data['close']*h5_data['adjfactor']
        
        CLOSE = h5_data['adjclose'].unstack()
        TURN = h5_data['turn'].unstack()
        
        alp_zf = CORR(CLOSE,TURN,W)
        alp_zf[alp_zf < 0] = np.nan
        
        alp_zf = alp_zf[str(self.stDate):str(self.edDate)]
        alp_zf = -alp_zf
        
        # filter index
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
                    
        data = malp_zf.join(self.index)
        data = data[data[self.universe] == 1]
        alp_zf = data[alpName].unstack()
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp18(self,alpName = 'alp18_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['amt','pct_chg','turn'], \
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data = data.replace([0,np.inf,-np.inf],np.nan)
        
        RET = data['pct_chg'].unstack()
        TURN = data['turn'].unstack()
        AMT = data['amt'].unstack()
        AMT = np.sqrt(AMT)
        
        alp_zf = REGSI(AMT,RET) - TURN
        alp_zf[alp_zf < 120] = np.nan
        alp_zf = -alp_zf
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp19(self,alpName = 'alp19_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate],columns = ['amt','vwap','close','total_shares','free_float_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
                             
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data['totalmktcap'] = data['close']*data['total_shares']
        data['ffmktcap'] = data['close']*data['free_float_shares']
        data['tdf'] = np.log(data['totalmktcap'])/np.log(data['ffmktcap'])
        data = data.replace([0,np.inf,-np.inf],np.nan)
        
        AMT = data['amt'].unstack()
        VWAP = data['vwap'].unstack()
        TDF = data['tdf'].unstack()
        AMT = np.sqrt(AMT)
        alp_zf = np.abs(REGSI(AMT,VWAP + TDF))
        alp_zf[alp_zf < 150] = np.nan
        alp_zf = -alp_zf
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp20(self,alpName = 'alp20_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['amt','close','total_shares','free_float_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data['totalmktcap'] = data['close']*data['total_shares']
        data['ffmktcap'] = data['close']*data['free_float_shares']
        data['tdf'] = np.log(data['totalmktcap'])/np.log(data['ffmktcap'])
        data = data.replace([0,np.inf,-np.inf],np.nan)
        
        AMT = data['amt'].unstack()
        CLOSE = data['close'].unstack()
        TDF = data['tdf'].unstack()
        AMT = np.sqrt(AMT)
        
        alp_zf = np.abs(CLOSE+np.abs(REGSI(AMT,TDF)))
        alp_zf = -alp_zf
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp21(self,alpName = 'alp21_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate],columns = ['amt','close','total_shares','free_float_shares'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        h5_data = h5_data.replace([0,np.inf,-np.inf],np.nan)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data['totalmktcap'] = data['close']*data['total_shares']
        data['ffmktcap'] = data['close']*data['free_float_shares']
        data['tdf'] = np.log(data['totalmktcap'])/np.log(data['ffmktcap'])
        data = data.replace([0,np.inf,-np.inf],np.nan)
        
        AMT = data['amt'].unstack()
        CLOSE = data['close'].unstack()
        TDF = data['tdf'].unstack()
        AMT = np.sqrt(AMT)
        
        
        alp_zf = np.abs(REGSI(AMT+CLOSE, TDF))
        alp_zf[alp_zf < 120] = np.nan
        alp_zf = -alp_zf
        
        #standardize
        alp_zf = alputils.standardize(alp_zf)
        malp_zf = pd.DataFrame(alp_zf.stack(),columns = [alpName])
        
        # riskNeutral
        malp_zf = alputils.riskNeutral(malp_zf,self.risk)
        malp_zf = malp_zf.dropna(axis = 0, how = 'all')
        self.h5write(malp_zf)

    def genalp22(self, alpName = 'alp22_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['vwap','close','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data = data.replace(np.inf,np.nan)
        data = data.replace(np.inf,np.nan)
        
        VWAP = data['vwap'].unstack()
        CLOSE = data['close'].unstack()
        TURN = data['turn'].unstack()
        
        alp = np.abs(TURN - VWAP/CLOSE)
        alp = -alp
        
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        alp = alputils.standardize(alp)
        
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        
        # riskNeutral
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)

    def genalp23(self, alpName = 'alp23_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['vwap','close','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data = data.replace(np.inf,np.nan)
        data = data.replace(np.inf,np.nan)
        
        VWAP = data['vwap'].unstack()
        CLOSE = data['close'].unstack()
        TURN = data['turn'].unstack()
        #TURN[AMT == 0] = np.nan
        
        alp = np.abs(TURN + VWAP/CLOSE)
        alp = -alp
        
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        alp = alputils.standardize(alp)
        
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        
        # riskNeutral
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)

    def genalp24(self, alpName = 'alp24_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['close','high','low','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        data = data.replace(np.inf,np.nan)
        data = data.replace(np.inf,np.nan)
        data['hml'] = data['high']-data['low']
        CLOSE = data['close'].unstack()
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        alp = CLOSE/np.abs(HML)/TURN
        alp = -alp
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        alp = alputils.standardize(alp)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        # riskNeutral
        malp = alputils.riskNeutral(malp,self.risk)    
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)

    def genalp25(self, alpName = 'alp25_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        data = IO.read_data([sdate,self.edDate], columns = ['vwap','high','low','turn'],\
                             ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = data.replace([np.inf,-np.inf],np.nan)
        data['hml'] = data['high']-data['low']
        
        VWAP = data['vwap'].unstack()
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        alp = np.abs(CORR(VWAP,HML,W)*TURN)
        alp = -alp
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        # standardize on universe
        data = malp.join(self.index)
        data = data[data[self.universe] ==1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp,ismdf = True)
        
        # risk neutral
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def genalp26(self, alpName = 'alp26_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        
        data = IO.read_data([sdate,self.edDate], columns = ['close','total_shares','high','low','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = data.replace([np.inf,-np.inf],np.nan)
        data['hml'] = data['high']-data['low']
        data['tcap'] = data['close']*data['total_shares']
        
        TCAP = np.log(data['tcap'].unstack())
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        alp = np.abs(CORR(TCAP,HML,W)*TURN)
        alp = -alp
        
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp, ismdf = True)
        
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def genalp27(self, alpName = 'alp27_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]  
        
        data = IO.read_data([sdate,self.edDate], columns = ['close','high','low','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = data.replace([np.inf, -np.inf], np.nan)
        data['hml'] = data['high']-data['low']
        
        CLOSE = data['close'].unstack()
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        
        alp = np.abs(CORR(CLOSE,HML,W)*TURN)
        alp = -alp
        
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        malp = pd.DataFrame(alp.stack(), columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp.join(self.index)
        data = data[data[self.universe]==1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp,ismdf = True)
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def genalp28(self, alpName = 'alp28_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        data = IO.read_data([sdate,self.edDate], columns = ['volume','high','low','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        data = data.replace([np.inf,-np.inf],np.nan)
        data['hml'] = data['high']-data['low']
        
        VOLUME = np.sqrt(data['volume'].unstack())
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        TURN[VOLUME == 0] = np.nan
        
        alp = np.abs(CORR(VOLUME,HML,10)*TURN)
        alp = -alp
        
        alp = alp.replace(np.inf, np.nan)
        alp = alp.replace(-np.inf, np.nan)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp, ismdf = True)
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def genalp29(self, alpName = 'alp29_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['amt','high','low','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        data = h5_data.replace([np.inf,-np.inf],np.nan)
        data['hml'] = data['high'] - data['low']
        AMT = np.sqrt(data['amt'].unstack())
        HML = np.abs(data['hml'].unstack())
        TURN = data['turn'].unstack()
        TURN[AMT == 0] = np.nan
        
        alp = np.abs(CORR(AMT,HML,W)*TURN)
        alp = -alp
        
        alp = alp.replace([np.inf,-np.inf], np.nan)
        # join index
        malp = pd.DataFrame(alp.stack(), columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        malp = data[[alpName]]
        # standarize
        malp = alputils.standardize(malp,ismdf = True)
        
        # risk Neutral
        #import pdb;pdb.set_trace()
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def genalp30(self, alpName = 'alp30_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['amt','close','total_shares','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.replace([np.inf,-np.inf],np.nan)
        data['tcap'] = data['close']*data['total_shares']
        
        AMT = np.sqrt(data['amt'].unstack())
        TCAP = np.log(data['tcap'].unstack())
        TURN = data['turn'].unstack()
        TURN[AMT == 0] = np.nan
        
        alp = np.abs(CORR(AMT,TCAP,W)*TURN)
        alp = -alp
        alp = alp.replace([np.inf,-np.inf],np.nan)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        
        # join index and standardize
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp,ismdf = True)
        
        # risk neutral
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)

    def genalp31(self, alpName = 'alp31_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]    
        h5_data = IO.read_data([sdate,self.edDate], columns = ['volume','close','total_shares','turn'],\
                           ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.replace([np.inf,-np.inf],np.nan)
        data['tcap'] = data['close']*data['total_shares']
        
        VOLUME = np.sqrt(data['volume'].unstack())
        TCAP = np.log(data['tcap'].unstack())
        TURN = data['turn'].unstack()
        TURN[VOLUME == 0] = np.nan
        
        alp = np.abs(CORR(VOLUME,TCAP,W)*TURN)
        alp = -alp
        alp = alp.replace([np.inf,-np.inf],np.nan)
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        #join index and standardize and riskneutral
        data = malp.join(self.index)
        data = data[data[self.universe] == 1]
        malp = data[[alpName]]
        malp = alputils.standardize(malp,ismdf = True)
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)

    def genptn(self,alpName = 'ptn_alpuniv'):    
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['pct_chg','turn'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        
        RET = data['pct_chg'].unstack()/100.0
        RET = np.abs(RET)
        RET[np.abs(RET) > 0.09] = np.nan
        TURN = data['turn'].unstack()/100.0 + 1e-9
        
        ptn_zf = np.power(RET,1.5)/TURN
        ptn_zf[ptn_zf > 1] = np.nan
        
        ptn_zf = ptn_zf.replace(np.inf, np.nan)
        ptn_zf = ptn_zf.replace(-np.inf, np.nan)
        
        ptn_zf = alputils.standardize(ptn_zf)
        
        # save data
        mptn_zf = pd.DataFrame(ptn_zf.stack())
        mptn_zf.columns = [alpName]
        
        mptn_zf = alputils.riskNeutral(mptn_zf,self.risk)
        mptn_zf = mptn_zf.dropna(axis = 0, how = 'all')
        self.h5write(mptn_zf)

    def gentcn(self,alpName = 'tcn_alpuniv'):
        W = 20
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['turn'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        df = h5_data['turn'].unstack()
        df = df.replace(np.inf, np.nan)
        df = df.replace(-np.inf, np.nan)
        
        tcn_zf = df.rolling(window = W).std()
        tcn_zf[tcn_zf < 0.04] = np.nan
        tcn_zf = tcn_zf.replace(np.inf, np.nan)
        tcn_zf = tcn_zf.replace(-np.inf, np.nan)
        
        # intersect with universe
        mtcn = pd.DataFrame(tcn_zf.stack(),columns = [alpName])
        mtcn = mtcn[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        mtcn = mtcn.join(self.index)
        mtcn = mtcn[mtcn[self.universe] == 1]
        
        tcn_zf = mtcn[alpName].unstack()
        tcn_zf = alputils.standardize(tcn_zf)
        
        # save data
        mtcn_zf = pd.DataFrame((-tcn_zf).stack(),columns = [alpName])
        
        # risk neutral
        mtcn_zf = alputils.riskNeutral(mtcn_zf,self.risk)
        mtcn_zf = mtcn_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        mtcn_zf = mtcn_zf.dropna(axis = 0, how = 'all')
        self.h5write(mtcn_zf)
    
    def gencore(self,alpName = 'core_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['pct_chg'],
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        if self.indexName is not None:
            index = IO.read_data([sdate, self.edDate], columns = [self.universe],alt = self.indexName)
        else:
            index = IO.read_data([sdate,self.edDate], columns = [self.universe],ftype=IO_enums.FType.UNIV, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.OPTM)
        
        datauniv = h5_data.join(index)
        datauniv = datauniv[datauniv[self.universe] == 1]
        data = h5_data
        
        # get index return
        dfuniv = datauniv['pct_chg'].unstack()
        dfM = dfuniv.mean(axis = 1)
        dfM = dfM.replace(np.inf, np.nan)
        dfM = dfM.replace(-np.inf, np.nan)
        
        df = data['pct_chg'].unstack()
        dfM_expand = pd.DataFrame(np.tile(dfM.values, [len(df.columns),1]).T,columns = df.columns, index = df.index)
        
        core_zf = df.rolling(window = W).corr(other = dfM_expand)
        core_zf = core_zf[str(self.stDate):str(self.edDate)]
        
        # get univ data
        mcorezf = pd.DataFrame(core_zf.stack(),columns = ['core'])
        mcorezf = mcorezf.join(index)
        mcorezf = mcorezf[mcorezf[self.universe]==1]
        core_zf = mcorezf['core'].unstack()
        # standardize
        core_zf = core_zf.replace(np.inf, np.nan)
        core_zf = core_zf.replace(-np.inf, np.nan)
        
        core_zf = alputils.standardize(core_zf)
        
        # save data        
        mcore_zf = pd.DataFrame(core_zf.stack())
        mcore_zf.columns = [alpName]
        
        mcore_zf = alputils.riskNeutral(mcore_zf,self.risk)
        mcore_zf = mcore_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        mcore_zf = mcore_zf.dropna(axis = 0, how = 'all')
        self.h5write(mcore_zf)

    def genz1(self,alpName = 'z1_alpuniv'):
        W = 10
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        h5_data = IO.read_data([sdate,self.edDate], columns = ['high','low','close','adjfactor'],\
                               ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        
        HIGH = h5_data['high'].unstack()
        LOW = h5_data['low'].unstack()
        CLOSE = h5_data['close'].unstack()
        ADJFACTOR = h5_data['adjfactor'].unstack()
        
        HIGH = HIGH * ADJFACTOR
        LOW = LOW * ADJFACTOR
        CLOSE = CLOSE * ADJFACTOR
        
        alp1 = 2*CLOSE/(HIGH+LOW)
        alp1 = alp1.replace(np.inf, np.nan)
        alp1 = alp1.replace(-np.inf, np.nan)
        
        HH5 = HIGH.rolling(window = 5).max()
        LL5 = LOW.rolling(window = 5).min()
        
        HH10 = HIGH.rolling(window = 10).max()
        LL10 = LOW.rolling(window = 10).min()
        
        alp2 = 2*CLOSE/(HH5+LL5)
        alp2 = alp2.replace(np.inf, np.nan)
        alp2 = alp2.replace(-np.inf, np.nan)
        
        alp3 = 2*CLOSE/(HH10 + LL10)
        alp3 = alp3.replace(np.inf, np.nan)
        alp3 = alp3.replace(np.inf, np.nan)
        
        # EW and winsorize
        alp1 = alp1.ewm(halflife = 3).mean()
        alp2 = alp2.ewm(halflife = 3).mean()
        alp3 = alp3.ewm(halflife = 3).mean()
        
        malp1 = pd.DataFrame(alp1.stack(), columns = ['alp1'])
        malp2 = pd.DataFrame(alp2.stack(), columns = ['alp2'])
        malp3 = pd.DataFrame(alp3.stack(), columns = ['alp3'])
        
        data = pd.concat([malp1,malp2,malp3,self.index],axis = 1)
        data = data[data[self.universe] == 1]
        
        alp1 = data['alp1'].unstack()
        alp2 = data['alp2'].unstack()
        alp3 = data['alp3'].unstack()
        
        # winsorize and standardize
        ###TODO: beta neutral
        alp1 = alputils.standardize(alp1)
        alp2 = alputils.standardize(alp2)
        alp3 = alputils.standardize(alp3)
        
        alp = alp1*0.3 + alp2*0.3 + alp3*0.4
        
        alp[alp < -0.85] = np.nan
        alp = -alp
        malp = pd.DataFrame(alp.stack(),columns = [alpName])
        malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]        
    
        malp = alputils.riskNeutral(malp,self.risk)
        malp = malp.dropna(axis = 0, how = 'all')
        self.h5write(malp)
    
    def update_use_previousdata(self, alpfullname):
        pre_stDate = dt.get_trading_day_offset(self.stDate,-1)[0]
        pre_edDate = dt.get_trading_day_offset(self.edDate,-1)[0]
        alp_pd = IO.read_data([pre_stDate, pre_edDate], alt = alpfullname)
        tmpcol = alp_pd.columns[0]
        print('no data be read! use past data to update ' + tmpcol)
        alp_pd = alp_pd[tmpcol].unstack()
        tmpdays = dt.get_trading_date_range(self.stDate,self.edDate)
        alp_pd.index = pd.Index(tmpdays,name='dt')
        alp_pd = pd.DataFrame(alp_pd.stack(),columns = [tmpcol])
        return alp_pd

    def genalpzf5b(self,alpName = 'alpzf5b_alpuniv'):
        try:
            a = IO.read_data([self.stDate,self.edDate],alt = r'W:\zhisj\factor\pv\reversal\residual_reversal\ff3_r2_nis.h5')
            b = IO.read_data([self.stDate,self.edDate],alt = r'W:\zhisj\factor\pv\reversal\residual_reversal\ff3_ivol_nis.h5')
        except:
            a = self.update_use_previousdata(r'W:\zhisj\factor\pv\reversal\residual_reversal\ff3_r2_nis.h5')
            b = self.update_use_previousdata(r'W:\zhisj\factor\pv\reversal\residual_reversal\ff3_ivol_nis.h5')

        a = a*0.9
        b = b*0.1
        data = pd.concat([a,b],axis = 1)
        alp = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        alp = alp.dropna(axis = 0,how = 'all')
        self.h5write(alp)
    
    def gendwf(self,alpName='dwf_alpuniv'):
        sdate = dt.get_trading_day_offset(self.stDate,-120)[0]
        data = IO.read_data([sdate,self.edDate],columns = ['pct_chg'],ftype=IO_enums.FType.MD, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.WIND)
        data = data.dropna(how = 'all')
        index = self.index
        risk = self.risk
        
        datanew = data[['pct_chg']].groupby('dt').apply(trans)
        datanew.columns = [alpName]
        
        data_df=datanew[alpName].unstack()
        data_df=data_df.ewm(halflife=10).mean()
        data_dfnew = np.sqrt(data_df)
        mdata = pd.DataFrame(data_dfnew.stack(),columns = [alpName])
        mdata = mdata[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        mdataindex=mdata.join(index)
        mdataindex=mdataindex[mdataindex[self.universe]==1]
        mdata=mdata[[alpName]]
        datasd = -utility.norm_winsor(mdata,ismdf=True)
        datan = alputils.riskNeutral(datasd,risk)
        datan.columns =[alpName]
        self.h5write(datan)
    
    def genM(self, alpName = 'M_alpuniv'):
        stDate = self.stDate
        edDate = self.edDate
        backwindow = 20
        sdate = dt.get_trading_day_offset(stDate,-backwindow)[0]
        tradecount = IO.read_data([sdate,edDate],columns = ['TRADES_COUNT'],alt=r'Z:\warehouse\prod\DATABASE\WIND\AShareMoneyFlow\AShareMoneyFlow.h5')
        amtret = IO.read_data([sdate,edDate],columns=['amt','pct_chg'],dsource=IO_enums.DSource.WIND)
        amtdf = amtret['amt'].unstack()
        retdf = amtret['pct_chg'].unstack()/100
        tradecountdf = tradecount['TRADES_COUNT'].unstack()
        tradecountdf = tradecountdf.reindex(index = amtdf.index, columns = amtdf.columns)
        W = amtdf/tradecountdf
        lenoftd = len(W.index)
        mlist = []
        for t in range((backwindow+1),(lenoftd+1)):
            tmpw = W.iloc[(t-backwindow):t,:]
            tmpret = retdf.iloc[(t-backwindow):t,:]
            tmpw = tmpw.rank(axis=0)
            tmphigh = tmpret.copy()
            tmplow = tmpret.copy()
            tmphigh[~(tmpw > backwindow/2)] = 0
            tmplow[~(tmpw < backwindow/2)] = 0
            mhigh=((1+tmphigh).cumprod()-1).iloc[-1:,:]
            mlow=((1+tmplow).cumprod()-1).iloc[-1:,:]
            m = mhigh-mlow
            m = pd.DataFrame(m.stack(), columns = [alpName])
            mlist.append(m)
        M = pd.concat(mlist, axis = 0)
        M = M.loc[IO.str_date_parser(stDate):IO.str_date_parser(edDate)]
        univ = self.index
        risk = self.risk
        M = M.join(univ)
        M = M[M['alpha_universe']==1]
        M = M[[alpName]]
        M = -utility.norm_winsor(M, ismdf = True)
        M = alputils.riskNeutral(M,risk)
        self.h5write(M)
    
    def genM_high(self, alpName = 'M_high_alpuniv'):
        stDate = self.stDate
        edDate = self.edDate
        backwindow = 20
        sdate = dt.get_trading_day_offset(stDate,-backwindow)[0]
        tradecount = IO.read_data([sdate,edDate],columns = ['TRADES_COUNT'],alt=r'Z:\warehouse\prod\DATABASE\WIND\AShareMoneyFlow\AShareMoneyFlow.h5')
        amtret = IO.read_data([sdate,edDate],columns=['amt','pct_chg'],dsource=IO_enums.DSource.WIND)
        amtdf = amtret['amt'].unstack()
        retdf = amtret['pct_chg'].unstack()/100
        tradecountdf = tradecount['TRADES_COUNT'].unstack()
        tradecountdf = tradecountdf.reindex(index = amtdf.index, columns = amtdf.columns)
        W = amtdf/tradecountdf
        lenoftd = len(W.index)
        mlist = []
        for t in range((backwindow+1),(lenoftd+1)):
            tmpw = W.iloc[(t-backwindow):t,:]
            tmpret = retdf.iloc[(t-backwindow):t,:]
            tmpw = tmpw.rank(axis=0)
            tmphigh = tmpret.copy()
            tmplow = tmpret.copy()
            tmphigh[~(tmpw > backwindow/2)] = 0
            tmplow[~(tmpw < backwindow/2)] = 0
            m=((1+tmphigh).cumprod()-1).iloc[-1:,:]
            m = pd.DataFrame(m.stack(), columns = [alpName])
            mlist.append(m)
        M = pd.concat(mlist, axis = 0)
        M = M.loc[IO.str_date_parser(stDate):IO.str_date_parser(edDate)]
        univ = self.index
        risk = self.risk
        M = M.join(univ)
        M = M[M['alpha_universe']==1]
        M = M[[alpName]]
        M = -utility.norm_winsor(M, ismdf = True)
        M = alputils.riskNeutral(M,risk)
        self.h5write(M)
