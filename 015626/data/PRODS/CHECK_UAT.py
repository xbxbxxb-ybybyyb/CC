from multifactor.data.utils import *
import multifactor.utility.dt as udt
from xquant.xqutils.helper import link
import pandas as pd
import os

# ！！！ 修改实盘因子配置文件时需要改如下路径
ic_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_V4.0.4.json'
if_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IF_V4.0.1.json'
im_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IM_V5.0.1.json'


flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'


def link_send_message(message):
    
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)
    
def factor_flag_check(date):
    
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_norm2_generation.success'
    path5 = flag_rootpath + str(date) + '/' + 'MODEL.success'
    path6 = flag_rootpath + str(date) + '/' + '%s_model.success'%str(date)
    print(path5, os.path.exists(path5))
    print(path6, os.path.exists(path6))
    return (os.path.exists(path5) and os.path.exists(path6))
        
def final_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_GEN_MODEL_FACTORS.success'
    path2 = '/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_IM_%s#503103.xlsx'%(date, date)
    print(path1, os.path.exists(path1))
    print(path2, os.path.exists(path2))
    return os.path.exists(path1) and os.path.exists(path2)

def check_sorted(test_list):
    flag = 0
    i = 1
    while i < len(test_list):
        if(test_list[i] < test_list[i - 1]):
            flag = 1
        i += 1
    if (not flag):
        return True
    else:
        return False


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
        if str.lower(xdir)[:2] in ['ic','if','du','tr','im']:
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
        print('factors fine')
        link_send_message('factor is OK')
        
def check_model_and_trade_files(edate):
    print('check final flag')
    while True:
        if final_flag_check(edate):
            break
        time.sleep(60)
    print('final flag check finished!')
    next_tday = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')
    xxy_path = '/data/user/016700/Data/para/Mobius_%s/'% (next_tday)
    print(xxy_path)
    model_list = []
    for x in os.listdir(xxy_path):

        
        if (str(next_tday) in x) and ('sim' not in x):
        #if (str(edate) in x):
            df = pd.read_excel(os.path.join(xxy_path,x), sheet_name='信号模型配置列表')
            model_list += df['对应模型目录'].tolist()

    model_list = list(set(model_list))
    print(model_list)
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
                
        normpath2 = os.path.join(path.replace('/model_trade/','/model_update/'), 'model_value', 'model_norm2', str(edate))
        for x in os.listdir(normpath2):
            pklpath = os.path.join(normpath2, x)
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
        print('model value fine')
        link_send_message('model value is OK')            

    trade_files_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/'

    

    wrong_reason = []

    # 检查因子文件
    for kind in ['ic','if','im']:
        if kind == 'ic':
            _json = ic_factor_json
            _suffix = '_all'
        elif kind == 'if':
            _json = if_factor_json
            _suffix = '_all_if'
        elif kind == 'im':
            _json = if_factor_json
            _suffix = '_all_im'
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
                    wrong_reason.append('%s factor norm lenth wrong' % (str(os.path.join(normfactor_path, str(edate))) + line['FactorName']))
                line = f.readline()
        if len(set(json_factors) - set(norm_factors)) != 0:
            wrong_reason.append('%s trade files norm factor wrong' % kind)      

    # 检查模型文件
    for model_path in model_list:
        model_name = model_path.split('/')[-2]
        model_file_path = os.path.join(trade_files_path, str(next_tday) + '_' + model_name, 'historySignal')
        if len(os.listdir(model_file_path)) != 31:
            wrong_reason.append(' num wrong %s' % model_file_path)
        for x in os.listdir(model_file_path):
            with open(os.path.join(model_file_path, x),'r') as f:
                line = f.readline()
                while line:
                    line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                    if len(line['Values']) != 237:
                        wrong_reason.append('%s model value lenth wrong' % os.path.join(model_file_path, x))
                    line = f.readline()
    th = []
    tmh = []
    ic_len_h = []
    if_len_h = []
    im_len_h = []

    print(len(model_list))
    for model_path in model_list:
        model_name = model_path.split('/')[-2]
        model_file_path2 = os.path.join(trade_files_path, str(next_tday) + '_' + model_name, 'signalNorm2Value')
        if len(os.listdir(model_file_path2)) < 1:
            wrong_reason.append(' num wrong %s' % model_file_path2)
        x = str(edate)
        with open(os.path.join(model_file_path2, x),'r') as f:
            line = f.readline()
            while line:
                line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                tmh.append(line['SignalName'])
                th.append(line['Values'])               
                if check_sorted(line['Values']):
                    pass
                else:
                    wrong_reason.append(' norm2 not sorted %s' % model_file_path2)                
                line = f.readline()
        temp_length_list = set([len(item) for item in th])
        if len(temp_length_list) != 1:
            wrong_reason.append(' signal length wrong %s' % model_file_path2)
        else:    
            if '_ic_' in model_path:
                ic_len_h.append(list(temp_length_list)[0])
            elif '_if_' in model_path:
                if_len_h.append(list(temp_length_list)[0])
            elif '_im_' in model_path:
                im_len_h.append(list(temp_length_list)[0])
        
            
        
        #if '_crn' in model_path:
        #    if len(tmh) != 6:
        #        wrong_reason.append(' model num wrong %s' % model_file_path2)
        #else:
        #    if len(tmh) != 15:
        #        wrong_reason.append(' model num wrong %s' % model_file_path2)
        th = []
        tmh = []
    

        
    if len(set(ic_len_h)) != 1:
        print(ic_len_h)
        wrong_reason.append(' ic norm2 length discrepancy %s' % model_file_path2)        

    if len(set(if_len_h)) != 1:
        wrong_reason.append(' if norm2 length discrepancy %s' % model_file_path2)
        print(set(if_len_h))
        
    if len(set(im_len_h)) != 1:
        wrong_reason.append(' im norm2 length discrepancy %s' % model_file_path2)
    
    if len(wrong_reason) > 0:
        link_send_message('trade files error!!!!!')
        link_send_message(str(wrong_reason))
        print(wrong_reason)
    else:
        print('trade files fine')
        link_send_message('trade files fine')

def minute_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    flag_path = flag_rootpath + str(date) + '/'
    path = flag_rootpath + str(date) + '/' + 'trade_files_factors.success'
    path2 = flag_rootpath + str(date) + '/' + 'trade_files.success'
    path3 = flag_path + str(date) + '_norm2_generation.success'
    path4 = flag_rootpath + str(date) + '/' + 'trade_files_factors2.success'
    print(path)
    print(path2)
    print(path3)
    return os.path.exists(path) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

_,tdate,_ = check_update_date()

while True:
    if minute_flag_check(tdate):
        break
    time.sleep(60)
print('flag check finished!')
#tdate = 20220803
#check_factor(tdate)
check_model_and_trade_files(tdate)