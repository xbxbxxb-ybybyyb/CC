from multifactor.IO import IO, IO_enums
from multifactor.utility import dt, alputils, utility
from multifactor.backtest import FactorTest
import pandas as pd
import numpy as np
import os, gc
import taskpath

tp = taskpath.TaskPath()

class FddAlp:
    def __init__(self,stDate,edDate,universe = 'alpha_universe', indexName = None):
        self.stDate = stDate
        self.edDate = edDate
        self.universe = universe
        self.indexName = indexName
        if universe == 'alpha_universe':
            self.fdddatapath = os.path.join(tp.featurepath,'fdddata_alpuniv')
            self.fddchgpath = os.path.join(tp.featurepath,'fddchg_alpuniv')
            self.fdddailypath = os.path.join(tp.featurepath,'fdddaily_alpuniv')
            self.fddqtrlypath = os.path.join(tp.featurepath,'fddqtrly_alpuniv')
        else:
            self.fdddatapath = os.path.join(tp.featurepath,'fdddata_'+ universe)
            self.fddchgpath = os.path.join(tp.featurepath,'fddchg_'+universe)
            self.fdddailypath = os.path.join(tp.featurepath,'fdddaily_'+universe)
            self.fddqtrlypath = os.path.join(tp.featurepath,'fddqtrly_'+universe)
        
        if not os.path.exists(self.fdddatapath):
            os.makedirs(self.fdddatapath)
        
        if not os.path.exists(self.fddchgpath):
            os.makedirs(self.fddchgpath)
        
        if not os.path.exists(self.fdddailypath):
            os.makedirs(self.fdddailypath)
        
        if not os.path.exists(self.fddqtrlypath):
            os.makedirs(self.fddqtrlypath)
        
        
        if indexName is None:
            self.index = IO.read_data([stDate,edDate], columns = [universe], alt = '/data/group/800080/warehouse/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
        else:
            self.index = IO.read_data([stDate,edDate], columns = [universe], alt = indexName)
        self.risk = IO.read_data([stDate,edDate],columns = ['Size','Industry'],\
                         ftype=IO_enums.FType.RISK, dfreq=IO_enums.DFreq.DAILY, dsource=IO_enums.DSource.STYLEFACTOR)

    def genalp(self):
        if self.universe == 'alpha_universe':
            self.genfalp()
            self.genfalpdaily()
        self.gengrossmargin()
        self.genoperatecashflow()
        self.genoperateincome()
        self.genroa()
        self.genroaroe()
        self.genroe()
        self.genroema()
        self.genroecom()
        self.genb2p()
        self.gene2p()
        self.genpechgnew()
        self.genfdddata()
        self.genfddchg()
        self.gengrowth()
        self.genquality()
        self.genprofit()
        self.gengrowthchg()
        self.genqualitychg()
        self.genprofitchg()
        return self

    def genfalp(self,alpName = 'falp_100', usefdays = False):
        stDate = self.stDate
        edDate = self.edDate
        savepath = self.fddqtrlypath
        
        stDate = dt.get_trading_day_offset(stDate,-2)[0]
        edDate = IO.str_date_parser(edDate)
        if usefdays:
            fdays = dt.get_financial_date_range(stDate,edDate)
        else:
            # then we update our data
            import datetime as dt1
            if stDate.year != edDate.year:
                fdays = []
            elif stDate.month < 5 and edDate.month >= 5:
                fdays = [IO.str_date_parser(dt1.date(edDate.year-1,12,31)),IO.str_date_parser(dt1.date(edDate.year,3,31))]
            elif stDate.month < 9 and edDate.month >= 9:
                fdays = [IO.str_date_parser(dt1.date(edDate.year,6,30))]
            elif stDate.month < 11 and edDate.month >= 11:
                fdays = [IO.str_date_parser(dt1.date(edDate.year,9,30))]
            else:
                fdays = []
        mdata = []
        for fd in fdays:
            print(fd)
            prefd = dt.get_financial_date(fd,31)
            curdate = dt.get_trading_day_offset(fd,2)[0]
            fdrange = dt.get_financial_date_range(prefd,curdate)
            pretdforpepb = dt.get_trading_day_offset(fd,0)[0]
            # fdata
            #data = IO.read_data(fdrange, columns = ['roe_basic','grossprofitmargin','qfa_ocftoor','qfa_yoygr','qfa_yoyprofit','qfa_roe'],\
            #                alt = 'W:/zhangf/data/fdd/CHINA_STOCK/DAILY/WIND/FDD_CHINA_STOCK_DAILY_WIND.h5')
            data = IO.read_data(fdrange,columns=['roe_basic','grossprofitmargin','qfa_ocftoor','qfa_yoygr','qfa_yoyprofit','qfa_roe'],
                                ftype=IO_enums.FType.FDD,dfreq=IO_enums.DFreq.QUARTERLY)
            # pepb
            pepb = IO.read_data(pretdforpepb, columns = ['pe_ttm','pb_lf'],\
                            ftype = IO_enums.FType.FDD, dfreq = IO_enums.DFreq.DAILY, dsource = IO_enums.DSource.WIND )
            
            # alpha universe
            univ = IO.read_data(pretdforpepb,ftype = IO_enums.FType.UNIV, dfreq = IO_enums.DFreq.DAILY, dsource = IO_enums.DSource.OPTM)
            univ = univ[univ['alpha_universe'] == True]
            
            # ipo data
            ipodata = pd.read_hdf('/data/group/800080/warehouse/prod/ETC/CHINA_STOCK/WIND/STOCK_LISTING_DELISTING_DATE.h5')
            # get secuCodes
            ipodata = ipodata[ipodata['ipo_date'] < pretdforpepb]
            secucode1 = list(ipodata.index)
            
            pepb1 = pepb[(pepb.pe_ttm < 50) & (pepb.pe_ttm > 0) & (pepb.pb_lf > 0) & (pepb.pb_lf < 20)]
            secucode2 = list(pepb1.index.get_level_values(level = 1))
            
            data1 = data.loc[fd,['roe_basic','grossprofitmargin']]
            data11 = data1[(data1.roe_basic > 5) & (data1.grossprofitmargin > 5)]
            
            secucode3 = list(data11.index)
            secucode4 = list(univ.index.get_level_values(level = 1))
            
            secuCode = set(secucode1).intersection(set(secucode2)).intersection(set(secucode3)).intersection(set(secucode4))
            secuCode = list(secuCode)
            
            if len(secuCode) == 0:
                raise('something wrong')
            
            qfa_roe = data['qfa_roe'].unstack()
            qfa_yoygr = data['qfa_yoygr'].unstack()
            qfa_yoyprofit = data['qfa_yoyprofit'].unstack()
            qfa_ocftoor = data['qfa_ocftoor'].unstack()
            
            qfa_roe = qfa_roe[secuCode]
            qfa_yoygr = qfa_yoygr[secuCode]
            qfa_yoyprofit = qfa_yoyprofit[secuCode]
            qfa_ocftoor = qfa_ocftoor[secuCode]
            
            roevol = pd.DataFrame(qfa_roe.std(axis = 0),columns = ['roevol'])
            yoygrvol = pd.DataFrame(qfa_yoygr.std(axis = 0),columns = ['yoygrvol'])
            yoyprofitvol = pd.DataFrame(qfa_yoyprofit.std(axis = 0),columns = ['yoyprofitvol'])
            ocftoorvol = pd.DataFrame(qfa_ocftoor.std(axis = 0),columns = ['ocftoorvol'])
            
            roevol = roevol.rank(axis = 0, method = 'average', na_option = 'keep', pct = True)
            yoygrvol = yoygrvol.rank(axis = 0, method = 'average', na_option = 'keep', pct = True)
            yoyprofitvol = yoyprofitvol.rank(axis = 0, method = 'average', na_option = 'keep', pct = True)
            ocftoorvol = ocftoorvol.rank(axis = 0, method = 'average', na_option = 'keep', pct = True)
                
            datavol = pd.concat([roevol*0.2,yoygrvol,yoyprofitvol,ocftoorvol*0.5],axis = 1)
        
            datavol = datavol.sum(axis = 1)
            datavol = pd.DataFrame(datavol, columns = ['fvol'])
            datavol = datavol.sort_values('fvol')
            
            secucodevolsd = list(datavol[0:int(alpName.split('_')[-1])].index)
            
            tmpdata = data.loc[fd,['roe_basic']]
            tmpdata = tmpdata.reset_index()
            tmpdata = tmpdata.set_index(['Ticker'])
            malp = tmpdata.loc[secucodevolsd]
            
            malp.columns = ['falp']
            malp = malp.rank(pct = True)
            
            malp = malp.reset_index()
            malp['dt'] = fd
            malp = malp.set_index(['dt','Ticker'])
            
            mdata = mdata + [malp]
        if len(mdata) != 0:        
            mdata = pd.concat(mdata, axis = 0)
            fileName = os.path.join(savepath,alpName + '.h5')
            if os.path.exists(fileName):
                append = True
            else:
                append = None
            IO.pd_hdf5_writer(mdata, fileName, dataset = alpName, append = append)
    
    def genfalpdaily(self,alpName = 'falp'):
        stDate = self.stDate
        edDate = self.edDate
        savepath = self.fdddailypath
        
        tradingdays = dt.get_trading_date_range(stDate,edDate)
        fileName = os.path.join(savepath,alpName + '.h5')
        tmplist = []
        for td in tradingdays:
            if td.month < 5:
                fdate = pd.Timestamp(td.year-1,9,30)
            elif td.month < 9:
                fdate = pd.Timestamp(td.year,3,31)
            elif td.month < 11:
                fdate = pd.Timestamp(td.year,6,30)
            else:
                fdate = pd.Timestamp(td.year,9,30)
                
            data = IO.read_data(fdate,alt = os.path.join(self.fddqtrlypath,alpName+'.h5'))
            
            data = data.reset_index()
            data.dt = td
            data = data.set_index(['dt','Ticker'])
            tmplist.append(data)

        dataall = pd.concat(tmplist,axis=0)
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(dataall,fileName,dataset = alpName,append = append)
        return None    

    def gengrossmargin(self,alpName = 'grossmargin_ttm2_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['grossmargin_ttm2'],ftype=IO_enums.FType.FDD, dfreq = IO_enums.DFreq.QUARTERLY)
        
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        
        roa = data['grossmargin_ttm2']
        # unstack
        roa_df = roa.unstack()
        # standardize
        roa_sd = alputils.standardize(roa_df)
        #stack to multiindex
        mroa = pd.DataFrame(roa_sd.stack(), columns = [alpName])
        mroa = alputils.riskNeutral(mroa,self.risk)
        mroa = mroa.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroa, fileName, alpName, append = append)

    def genoperatecashflow(self,alpName = 'operatecashflow_ttm2_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['operatecashflow_ttm2'],ftype=IO_enums.FType.FDD)
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        roa = data['operatecashflow_ttm2']
        # unstack
        roa_df = roa.unstack()
        roa_df = utility.norm_winsor(roa_df)
        mroa = pd.DataFrame(roa_df.stack(),columns = [alpName])
        mroa = alputils.riskNeutral(mroa,self.risk)
        mroa = mroa.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroa, fileName, alpName, append = append)

    def genoperateincome(self,alpName = 'operateincome_alpuniv'):
        stDate = self.stDate
        edDate = self.edDate
        universe = self.universe
        savepath = self.fdddailypath
        h5_data = IO.read_data([stDate,edDate], columns = ['qfa_operateincome'],ftype=IO_enums.FType.FDD)
        index = self.index
        data = h5_data.join(index)
        data = data[data[universe] == 1]
        roa = data[['qfa_operateincome']]
        mroa = utility.norm_winsor(roa,ismdf=True)
        mroa.columns = [alpName]
        mrisk = self.risk
        mroa = alputils.riskNeutral(mroa,mrisk)
        mroa = mroa.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(savepath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroa, fileName, alpName, append = append)
        gc.collect

    def genroa(self,alpName = 'roa_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['qfa_roa'],ftype=IO_enums.FType.FDD )
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        roa = data['qfa_roa']
        # unstack
        roa_df = roa.unstack()
        roa_df = utility.norm_winsor(roa_df)
        mroa = pd.DataFrame(roa_df.stack(),columns = [alpName])
        mroa = alputils.riskNeutral(mroa,self.risk)
        mroa = mroa.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroa, fileName, alpName, append = append)

    def genroaroe(self,alpName = 'roaroe_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['qfa_roe','qfa_roa'],ftype=IO_enums.FType.FDD )
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        roe = data[['qfa_roe','qfa_roa']]
        roe = pd.DataFrame(roe.sum(axis  = 1), columns = [alpName])
        # unstack
        roe_df = roe.unstack()
        roe_df = utility.norm_winsor(roe_df)
        mroe = pd.DataFrame(roe_df.stack(),columns = [alpName])
        # standardize
        #roe_sd = alputils.standardize(roe_df)
        #stack to multiindex
        #mroe = pd.DataFrame(roe_sd.stack(), columns = [alpName])
        mroe = alputils.riskNeutral(mroe,self.risk)
        mroe = mroe.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroe, fileName, alpName, append = append)

    def genroe(self,alpName = 'roe_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['qfa_roe'],ftype=IO_enums.FType.FDD )
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        roe = data['qfa_roe']
        # unstack
        roe_df = roe.unstack()
        roe_df = utility.norm_winsor(roe_df)
        mroe = pd.DataFrame(roe_df.stack(),columns = [alpName])
        
        # standardize
        #roe_sd = alputils.standardize(roe_df)
        #stack to multiindex
        #mroe = pd.DataFrame(roe_sd.stack(), columns = [alpName])
        mroe = alputils.riskNeutral(mroe,self.risk)
        mroe = mroe.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroe, fileName, alpName, append = append)

    def genroema(self,alpName = 'roema_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['qfa_roe','qfa_roa'],ftype=IO_enums.FType.FDD )
        roe = h5_data['qfa_roe']
        roa = h5_data['qfa_roa']
        
        roeroa = pd.concat([roe,roa],axis = 1)
        alp = pd.DataFrame(roeroa['qfa_roe'] - roeroa['qfa_roa'], columns = [alpName])
        
        data = alp.join(self.index)
        data = data[data[self.universe] == 1]
        
        alp_df = data[alpName].unstack()
        alp_df = utility.norm_winsor(alp_df)
        mroe = pd.DataFrame(alp_df.stack(),columns = [alpName])
        # standardize
        #alp_sd = alputils.standardize(alp_df)
        
        #stack to multiindex
        #mroe = pd.DataFrame(alp_sd.stack(), columns = [alpName])
        mroe = alputils.riskNeutral(mroe,self.risk)
        mroe = mroe[alpName].unstack()
        mroe = FactorTest.Standard_Process(mroe)
        mroe = pd.DataFrame(mroe.stack(),columns = [alpName])
        mroe = mroe.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mroe, fileName, alpName, append = append)
        
    def genroecom(self,alpName = 'roecom_alpuniv'):
        mroe = IO.read_data([self.stDate,self.edDate],alt = os.path.join(self.fdddailypath,'roe_alpuniv.h5'))
        mroema = IO.read_data([self.stDate,self.edDate],alt = os.path.join(self.fdddailypath,'roema_alpuniv.h5'))
        
        roecom = pd.concat([mroe*0.5,mroema*0.5],axis = 1)
        roecom = pd.DataFrame(roecom.sum(axis = 1),columns = [alpName])    
        roecom = roecom.dropna(how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(roecom, fileName, alpName, append = append)

    def genb2p(self,alpName = 'B2P_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['pe_ttm','pb_lf'],ftype=IO_enums.FType.FDD )
        
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        B2P = 1/data['pb_lf']
        # unstack
        B2P_df = B2P.unstack()
        # standardize
        B2P_sd = alputils.standardize(B2P_df)
        #stack to multiindex
        mB2P = pd.DataFrame(B2P_sd.stack(), columns = [alpName])
        mB2P = alputils.riskNeutral(mB2P,self.risk)
        mB2P = mB2P.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mB2P, fileName, alpName, append = append)

    def gene2p(self,alpName = 'E2P_alpuniv'):
        h5_data = IO.read_data([self.stDate,self.edDate], columns = ['pe_ttm'],ftype=IO_enums.FType.FDD )
        data = h5_data.join(self.index)
        data = data[data[self.universe] == 1]
        E2P = 1/data['pe_ttm']
        # unstack
        E2P_df = E2P.unstack()
        # standardize
        E2P_sd = alputils.standardize(E2P_df)
        #stack to multiindex
        mE2P = pd.DataFrame(E2P_sd.stack(), columns = [alpName])
        mE2P = alputils.riskNeutral(mE2P,self.risk)
        mE2P = mE2P.dropna(axis = 0, how = 'all')
        # save data
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mE2P, fileName, alpName, append = append)

    def genpechgnew(self,alpName = 'pechgnew_alpuniv'):
        W = 60
        sdate = dt.get_trading_day_offset(self.stDate,-W)[0]
        data = IO.read_data([sdate,self.edDate],alt = os.path.join(self.fdddailypath,'E2P_alpuniv.h5'))
        alp = data['E2P_alpuniv'].unstack()
        alp = alp - alp.shift(W)
        alp = FactorTest.Standard_Process(alp)
        
        mpe_zf = pd.DataFrame(alp.stack(), columns = [alpName])
        mpe_zf = mpe_zf[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        mpe_zf = alputils.riskNeutral(mpe_zf,self.risk)
        mpe_zf = mpe_zf.dropna(axis = 0, how = 'all')
        
        fileName = os.path.join(self.fdddailypath, alpName + '.h5')
        if os.path.exists(fileName):    
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(mpe_zf, fileName, alpName, append = append)
    
    def genfdddata(self):
        alpNames1 = ['yoyroe','yoyprofit','yoyop','yoyocfps','yoyocf','yoynetprofit','yoyeps_basic','yoy_tr','qfa_yoysales','qfa_yoyprofit','qfa_yoyop','qfa_yoygr']
        alpNames2 = ['roic','roe_ttm2','roe_basic','roa2_ttm2','qfa_roe','qfa_roa','qfa_profittogr','qfa_operateincome','qfa_grossmargin','profit_ttm2','optogr']
        alpNames = alpNames1 + alpNames2
        for alp in alpNames:
            alpName = alp + '_alpuniv'
            h5_data = IO.read_data([self.stDate,self.edDate], columns = [alp],ftype=IO_enums.FType.FDD,h5root='W:/zhangf/data')
        
            roe_df = h5_data[alp].unstack()
            roe_df = roe_df.rank(axis = 1, na_option = 'keep', pct = True)
        
            # unstack
            roe = pd.DataFrame(roe_df.stack(),columns = [alpName])                         
        
            data = roe.join(self.index)
            data = data[data[self.universe] == 1]
        
            roe_df = data[alpName].unstack()
            # standardize
            roe_sd = FactorTest.Standard_Process(roe_df)
        
            #stack to multiindex
            mroe = pd.DataFrame(roe_sd.stack(), columns = [alpName])
            
            mroe = alputils.riskNeutral(mroe,self.risk)
            mroe = mroe.dropna(axis = 0, how = 'all')
            if not os.path.exists(self.fdddatapath):
                os.makedirs(self.fdddatapath)
        
            # save data
            fileName = os.path.join(self.fdddatapath, alpName + '.h5')
            if os.path.exists(fileName):
                append = True
            else:
                append = None
            IO.pd_hdf5_writer(mroe, fileName, alpName, append = append)
            gc.collect
    
    def genfddchg(self):
        fileNames = os.listdir(self.fdddatapath)
        sdate = dt.get_trading_day_offset(self.stDate,-60)[0]
        
        for alpName in fileNames:
            alp = alpName.split('.')[0]
            data = IO.read_data([sdate,self.edDate],alt = os.path.join(self.fdddatapath,alpName))
            data_df = data[alp].unstack()
            datanew = data_df - data_df.shift(60)
            
            datasd = FactorTest.Standard_Process(datanew)
            malp = pd.DataFrame(datasd.stack(),columns = [alp+'chg'])
            malp = malp[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
            malp = alputils.riskNeutral(malp,self.risk)
            malp = malp.dropna(how = 'all')
            if not os.path.exists(self.fddchgpath):
                os.makedirs(self.fddchgpath)
        
            # save data
            fileName = os.path.join(self.fddchgpath, alp+'chg' + '.h5')
            if os.path.exists(fileName):
                append = True
            else:
                append = None
            IO.pd_hdf5_writer(malp, fileName, alpName, append = append)
            gc.collect
            
    def gengrowth(self,alpName = 'growth_alpuniv'):   
        sdate = self.stDate
        edate = self.edDate
        yoyocfps = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoyocfps_alpuniv.h5'))
        #yoydebt = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoydebt_alpuniv.h5'))
        qfa_yoygr = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_yoygr_alpuniv.h5'))
        yoy_tr = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoy_tr_alpuniv.h5'))
        qfa_yoyprofit = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_yoyprofit_alpuniv.h5'))
        yoyroe = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoyroe_alpuniv.h5'))   
        yoyeps_basic = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoyeps_basic_alpuniv.h5'))
        qfa_yoyop = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_yoyop_alpuniv.h5'))
        yoynetprofit = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoynetprofit_alpuniv.h5'))
        qfa_yoysales = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_yoysales_alpuniv.h5'))
        yoyprofit = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoyprofit_alpuniv.h5'))
        yoyop = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'yoyop_alpuniv.h5'))
        
        data = pd.concat([yoyocfps*0.4,qfa_yoygr*0.1,yoy_tr*0.05,qfa_yoyprofit*0.1,yoyroe*0.1,yoyeps_basic*0.1,qfa_yoyop*0.4,yoynetprofit*0.05,qfa_yoysales*0.05,\
                          yoyprofit*0.1,yoyop*0.1],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)
        
    def genquality(self,alpName = 'quality_alpuniv'):
        sdate = self.stDate
        edate = self.edDate
        qfa_roa = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_roa_alpuniv.h5'))
        qfa_roe = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_roe_alpuniv.h5'))
        roa2_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'roa2_ttm2_alpuniv.h5'))
        roe_basic = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'roe_basic_alpuniv.h5'))
        roic = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'roic_alpuniv.h5'))
        roe_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'roe_ttm2_alpuniv.h5'))
        
        data = pd.concat([qfa_roa*0.05,qfa_roe*0.5,roa2_ttm2*0.5,roe_basic*0.05,roic*0.05,roe_ttm2*0.05],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)
    
    def genprofit(self,alpName = 'profit_alpuniv'):
        sdate = self.stDate
        edate = self.edDate
        qfa_profittogr = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_profittogr_alpuniv.h5'))
        profit_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'profit_ttm2_alpuniv.h5'))
        qfa_operateincome = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_operateincome_alpuniv.h5'))
        qfa_grossmargin = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'qfa_grossmargin_alpuniv.h5'))
        optogr = IO.read_data([sdate,edate],alt = os.path.join(self.fdddatapath,'optogr_alpuniv.h5'))
        
        data = pd.concat([qfa_profittogr*0.05,profit_ttm2*0.05,qfa_operateincome*0.4,qfa_grossmargin*0.3,optogr*0.3],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)
        
    def gengrowthchg(self,alpName = 'growthchg_alpuniv'):
        sdate = self.stDate
        edate = self.edDate
        #yoydebt = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoydebt_alpunivchg.h5'))
        yoy_tr = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoy_tr_alpunivchg.h5'))
        qfa_yoyprofit = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_yoyprofit_alpunivchg.h5'))
        yoyroe = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoyroe_alpunivchg.h5'))
        yoyeps_basic = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoyeps_basic_alpunivchg.h5'))
        qfa_yoyop = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_yoyop_alpunivchg.h5'))
        yoynetprofit = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoynetprofit_alpunivchg.h5'))
        qfa_yoysales = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_yoysales_alpunivchg.h5'))
        yoyop = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'yoyop_alpunivchg.h5'))
        
        data = pd.concat([yoy_tr*0.2,qfa_yoyprofit*0.01,yoyroe*0.1,yoyeps_basic*0.2,qfa_yoyop*0.05,yoynetprofit*0.05,qfa_yoysales*0.01,\
                          yoyop*0.2],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)
        
    def genqualitychg(self,alpName = 'qualitychg_alpuniv'):
        sdate = self.stDate
        edate = self.edDate
        qfa_roa = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_roa_alpunivchg.h5'))
        qfa_roe = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_roe_alpunivchg.h5'))
        roa2_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'roa2_ttm2_alpunivchg.h5'))
        roe_basic = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'roe_basic_alpunivchg.h5'))
        roic = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'roic_alpunivchg.h5'))
        roe_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'roe_ttm2_alpunivchg.h5'))
        
        data = pd.concat([qfa_roa*0.22,qfa_roe*0.02,roa2_ttm2*0.05,roe_basic*0.02,roic*0.1,roe_ttm2*0.6],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)
    
    def genprofitchg(self,alpName = 'profitchg_alpuniv'):
        sdate = self.stDate
        edate = self.edDate
        qfa_profittogr = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_profittogr_alpunivchg.h5'))
        profit_ttm2 = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'profit_ttm2_alpunivchg.h5'))
        qfa_operateincome = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_operateincome_alpunivchg.h5'))
        qfa_grossmargin = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'qfa_grossmargin_alpunivchg.h5'))
        optogr = IO.read_data([sdate,edate],alt = os.path.join(self.fddchgpath,'optogr_alpunivchg.h5'))
        
        data = pd.concat([qfa_profittogr*0.4,profit_ttm2*0.5,qfa_operateincome*0.02,qfa_grossmargin*0.1,optogr*0.1],axis = 1)
        data = pd.DataFrame(data.sum(axis = 1),columns = [alpName])
        
        fileName = os.path.join(self.fdddailypath,alpName + '.h5')
        if not os.path.exists(fileName):
            append = None
        else:
            append = True
        IO.pd_hdf5_writer(data,fileName,alpName,append = append)