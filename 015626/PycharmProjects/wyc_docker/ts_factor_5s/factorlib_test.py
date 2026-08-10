from multiprocessing import Pool
from SIF_Factor_Test13 import SIF_Factor_Test
import datetime
import pandas as pd
import numpy as np
import os
import glob
from multifactor.IO import IO
import multifactor.utility.dt as udt

class FactorLibTest:

    def __init__(self, libname, ticker = 'IC.CFE',start_date = 20200101, end_date = 21000101, save_image = False, show_image=False, save_path = '/data/user/015626/data/share/factor/factor_test/1min/all_factor_test_20201208/'):
        self.libname = libname
        self.start_date = start_date
        self.end_date = end_date
        self.save_image = save_image
        self.show_image = show_image
        self.ticker = ticker
        self.libpath = '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/' + libname
        self.save_path = os.path.join(save_path, libname + '_' + str(start_date) + '_' + str(end_date))
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        origindata = IO.read_data([start_date, int(str(udt.get_trading_day_offset(end_date,1)[0])[:10].replace('-',''))], columns=['vwap'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
        origindata = origindata.xs(self.ticker, level=1)
        origindata['ret'] = origindata['vwap'].shift(-2) / origindata['vwap'].shift(-1) - 1
        self.origindata = origindata[['ret']]

    def test_factor(self, factorpath):
        factorname = factorpath.split('/')[-1][:-3]
        print(factorname)
        f = pd.read_hdf(factorpath).loc[str(self.start_date):str(self.end_date)]
        try:
            sif = SIF_Factor_Test(f.join(self.origindata, how='inner').sort_index(), factor_kind='1min', save_image=self.save_image,
                                  show_image=self.show_image, signal_lims=(-1, 1), savepath=self.save_path)
            stats = sif.draw_result()
            del (sif)
            return pd.DataFrame(stats, index=[f.columns.tolist()[0]])
        except:
            return pd.DataFrame({}, index=[f.columns.tolist()[0]])

    def run(self):
        pathlist = glob.glob(self.libpath + '/*.h5')

        with Pool(processes=24) as pool:
            rlist = pool.map(self.test_factor, pathlist)
        result = pd.concat(rlist, axis=0)
        return result

# edate = 20201225
#
# rdict = {}
# for i in [0,4,19,59,119,239]:
#     r = FactorLibTest('IF_prod', ticker='IF.CFE', start_date=int(str(udt.get_trading_day_offset(edate, -1 * i)[0])[:10].replace('-','')),end_date=edate).run()
#     r.to_csv('/data/user/015626/data/share/test0.csv')
#     rdict[str(i+1)+' tdays'] = [len(r), round(r['IC-1min'].fillna(value = 0).mean(),3), round(r['sharpe_Q3-Q0'].fillna(value = 0).mean(),3), len(r[r['ret_per_deal']>0]), len(r[r['ret_per_deal']<0]),len(r[r['ret_per_deal'].isna()])]
#
# result = pd.DataFrame(rdict, index=['count','IC','sharpe','profit count','loss count','no deal count'])
# print(result)
