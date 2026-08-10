from multifactor.data.utils import *
import multifactor.utility.dt as udt
from xquant.xqutils.helper import link
import pandas as pd
import os

# ！！！ 修改实盘因子配置文件时需要改如下路径
ic_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_fix.json'
if_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IF_v3.0.3.json'
    
def link_send_message(message):
    
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)
    
def factor_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

        
def final_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_GEN_MODEL_FACTORS.success'
    return os.path.exists(path1)

def check_factor(edate):
    print('check factor flag')
    while True:
        if factor_flag_check(edate):
            break
        time.sleep(60)
    print('factor flag check finished!')
    factor_rootpath = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/'
    wrong_factor_list = []
    for xdir in os.listdir(factor_rootpath):
        if str.lower(xdir)[:2] in ['ic','if','du','tr']:
            fac_path = os.path.join(factor_rootpath, xdir, 'minute_norm')
            for h5 in os.listdir(fac_path):
                try:
                    fac = pd.read_hdf(os.path.join(fac_path, h5)).loc[str(edate)]
                    if len(fac) != 237 or len(fac.dropna()) < 100:
                        print('wrong factor: ', fac_path, h5)
                        wrong_factor_list.append(os.path.join(fac_path, h5))
                except:
                    wrong_factor_list.append(os.path.join(fac_path, h5))
    if len(wrong_factor_list) > 0:
        link_send_message('factor big wrong!!!!!')
        link_send_message(str(wrong_factor_list))
    else:
        link_send_message('factor is OK')
        
def check_model_and_trade_files(edate):
    print('check final flag')
    while True:
        if final_flag_check(edate):
            break
        time.sleep(60)
    print('final flag check finished!')
    
    xxy_path = '/data/user/011477/Trade_Docs/%s/Mobius_%s/' % (edate, edate)
    model_list = []
    for x in os.listdir(xxy_path):
        if x.endswith('%s.xlsx'%edate):
            df = pd.read_excel(os.path.join(xxy_path,x), sheet_name='信号模型配置列表')
            model_list += df['对应模型目录'].tolist()

    model_list = list(set(model_list))

    wrong_model_list = []
    for path in model_list:
        rawpath = os.path.join(path.replace('/model_trade/','/model_update/'), 'model_value', 'model_raw', str(edate))
        print()
        for x in os.listdir(rawpath):
            pklpath = os.path.join(rawpath, x)
            try:
                pkl = pd.read_pickle(pklpath).loc[str(edate)]
                if pkl.shape != (237,3) or len(pkl.dropna()) < 236:
                    wrong_model_list.append(pklpath)
            except:
                wrong_model_list.append(pklpath)
        normpath = os.path.join(path.replace('/model_trade/','/model_update/'), 'model_value', 'model_norm', str(edate))
        for x in os.listdir(normpath):
            pklpath = os.path.join(normpath, x)
            try:
                pkl = pd.read_pickle(pklpath).loc[str(edate)]
                if len(pkl) != 237 or len(pkl.dropna()) < 236:
                    wrong_model_list.append(pklpath)
                    print('model wrong:', pklpath)
            except:
                wrong_model_list.append(pklpath)
    if len(wrong_model_list) > 0:
        link_send_message('model value big wrong!!!!!')
        link_send_message(str(wrong_model_list))
    else:
        link_send_message('model value is OK')            

    trade_files_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/'

    next_tday = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')

    wrong_reason = []

    # 检查ICIF的因子文件
    for kind in ['ic','if']:
        _json = ic_factor_json if kind == 'ic' else if_factor_json
        _suffix = '_all' if kind  == 'ic' else '_all_if'
        datajson = pd.read_json(_json)
        json_factors = datajson.FactorName.tolist()
        if len(json_factors) != len(set(json_factors)):
            wrong_reason.append('%s json wrong' % kind)
        rawfactor_path = os.path.join(trade_files_path, str(next_tday) + _suffix, 'historyFactor')
        if len(os.listdir(rawfactor_path)) != 62:
            wrong_reason.append('%s trade files raw num wrong' % kind)
        for x in os.listdir(rawfactor_path):
            history_factors = []
            with open(os.path.join(rawfactor_path, x),'r') as f:
                line = f.readline()
                while line:
                    line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                    history_factors.append(line['FactorName'])
                    if len(line['Values']) != 237:
                        wrong_reason.append('%s factor raw lenth wrong' % (str(os.path.join(rawfactor_path, x)) + line['FactorName']))
                    line = f.readline()
            if len(set(json_factors) - set(history_factors)) != 0:
                wrong_reason.append('%s trade files raw factor wrong' % kind)

        normfactor_path = os.path.join(trade_files_path, str(next_tday) + _suffix, 'historyNormFactor')
        if len(os.listdir(normfactor_path)) != 1:
            wrong_reason.append('%s trade files norm factor num wrong' % kind)
        norm_factors = []
        with open(os.path.join(normfactor_path, str(edate)),'r') as f:
            line = f.readline()
            while line:
                line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                norm_factors.append(line['FactorName'])
                if len(line['Values']) != 237:
                    wrong_reason.append('%s factor norm lenth wrong' % (str(os.path.join(rawfactor_path, x)) + line['FactorName']))
                line = f.readline()
        if len(set(json_factors) - set(norm_factors)) != 0:
            wrong_reason.append('%s trade files norm factor wrong' % kind)      

    # 检查模型文件
    for model_path in model_list:
        model_name = model_path.split('/')[-2]
        model_file_path = os.path.join(trade_files_path, str(next_tday) + '_' + model_name, 'historySignal')
        if len(os.listdir(model_file_path)) != 30:
            wrong_reason.append(' num wrong' % model_file_path)
        for x in os.listdir(model_file_path):
            with open(os.path.join(model_file_path, x),'r') as f:
                line = f.readline()
                while line:
                    line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                    if len(line['Values']) != 237:
                        wrong_reason.append('%s model value lenth wrong' % os.path.join(model_file_path, x))
                    line = f.readline()

    if len(wrong_reason) > 0:
        link_send_message('trade files error!!!!!')
        link_send_message(str(wrong_reason))
        print(wrong_reason)
    else:
        link_send_message('trade files fine')

_,tdate,_ = check_update_date()
#tdate = 20220803
check_factor(tdate)
check_model_and_trade_files(tdate)