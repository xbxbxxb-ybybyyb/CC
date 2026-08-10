import sys
import datetime as dt
import pandas as pd
import os
from log import Log
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils import *
from WindPy import w
w.start()

logger = Log('wind_api_weiych')
root_path = 'A:\\weiyc\\data\\Industry\\CSV\\basic_info'
table_h5_file = 'A:\\weiyc\\data\\Industry\\basic_info\\basic_info.h5'

def retriever(date_list):
    for date in date_list:
        print('*'*10, date ,'*'*10)
        df = w.wsee("b101000000000000,b102000000000000,b103000000000000,b104000000000000,b105000000000000,b106000000000000,b107000000000000,b108000000000000,b109000000000000,b10a000000000000,b10b000000000000,b10c000000000000,b10d000000000000,b10e000000000000,b10f000000000000,b10g000000000000,b10h000000000000,b10i000000000000,b10j000000000000,b10k000000000000,b10l000000000000,b10m000000000000,b10n000000000000,b10o000000000000,b10p000000000000,b10q000000000000,b10r000000000000,b10s000000000000,b10t000000000000",
                    "sec_turn_ffmc_wavg,sec_close_ffswavg_chn,sec_ncashinflow_d_sum_chn,sec_nclosinginflow_d_sum_chn,sec_cinflowrate_d_overall_chn,sec_pettm_media_chn,sec_csrc_statlistcompnum_chn,sec_csrc_stat_mv_chn",
                    "tradeDate=" + str(date) + ";DynamicTime=0;excludeRule=1;P0="+str(date)+";P1=0;equityType=0")
        df = pd.DataFrame(data = df.Data, index=df.Fields, columns=df.Codes).T

        df.index.name = 'Ticker'
        df = df.reset_index()
        df['dt'] = date
        df = df.set_index(['dt','Ticker'])

        df.to_csv(os.path.join(root_path, str(date) + '.csv'))

def csv2h5(sdate, edate, operation = 'append'):

    csv_list = [os.path.join(root_path, i) for i in os.listdir(root_path)]

    update_list = [i for i in csv_list if
                   int(i[-12:-4]) >= sdate and int(i[-12:-4]) <= edate and int(i[-12:-4]) >= 20000101]
    update_list.sort()
    if operation == 'create':
        logger.info('csv2h5: create -  %s' % (table_h5_file))
        os.remove(table_h5_file) if os.path.exists(table_h5_file) else None
    with pd.HDFStore(table_h5_file) as h5_store:
        logger.info('csv2h5: check date list')
        for fname in update_list:
            if not '.csv' in fname:
                continue
            logger.info(fname)
            dat = pd.read_csv(fname, encoding='utf_8_sig')
            dat = data_reformat(dat)
            if len(dat) <= 0:
                logger.warning('csv2h5: sparse table %s - data too little ' % (fname))
                continue
            else:
                h5_store.append('basic_info', dat, data_columns=True)
                logger.info('csv2h5: %s done' % (fname))

def data_reformat(dat):
    #dat = dat.sort_values([dat_fig['dt']])
    dat['dt'] = dat['dt'].apply(lambda x: dt.datetime.strptime(str(x),'%Y%m%d'))
    dat['Ticker'] = dat['Ticker'].astype('str')
    dat = dat.set_index(['dt', 'Ticker'])
    return dat

sdate, edate, cdate_list = check_update_date(20180124, 20180125)
retriever(cdate_list)
csv2h5(20100101, 20191104, 'create')