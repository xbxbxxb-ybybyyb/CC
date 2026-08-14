import pandas as pd
import datetime
from xquant.xqutils.helper import link

def gen_sp_param_qianyi():
    today = datetime.date.today().strftime('%Y%m%d')
    common_path = r'/data/group/800463/param/param/'
    o45_param = pd.read_excel(common_path + r'param-%s-prod-O45.xlsx'%today, sheet_name=None)
    #深圳O45卖出票必须在深圳中心启动，也就是一定要在other_selected_stocks里
    o45_InitialBasicParam = o45_param['InitialBasicParam']
    sz_InitialBasicParam = o45_InitialBasicParam[o45_InitialBasicParam['股票代码'].str.endswith('.SZ')]
    sh_InitialBasicParam = o45_InitialBasicParam[o45_InitialBasicParam['股票代码'].str.endswith('.SH')]
    sz_sell_stocks = sz_InitialBasicParam[sz_InitialBasicParam['期初可用仓位'] != 0]['股票代码'].values.tolist()
    sh_sell_stocks = sh_InitialBasicParam[sh_InitialBasicParam['期初可用仓位'] != 0]['股票代码'].values.tolist()
    print(len(o45_InitialBasicParam), len(sz_InitialBasicParam), len(sh_InitialBasicParam), len(sz_sell_stocks), len(sh_sell_stocks))
    lm = link.LinkMessage()
    lm.sendMessage('%d %d %d %d %d' % (len(o45_InitialBasicParam), len(sz_InitialBasicParam), len(sh_InitialBasicParam), len(sz_sell_stocks), len(sh_sell_stocks)))

    o45_saturn = o45_param['saturn配置参数']
    o45_ceres = o45_param['ceres配置参数']
    o45_saturn_stocks = sorted(list(set(o45_saturn['股票代码'].values.tolist())))
    sh_o45_saturn_stocks = [x for x in o45_saturn_stocks if '.SH' in x]
    sz_o45_saturn_stocks = [x for x in o45_saturn_stocks if '.SZ' in x]
    o45_ceres_stocks = sorted(list(set(o45_ceres['股票代码'].values.tolist())))
    sh_o45_ceres_stocks = [x for x in o45_ceres_stocks if '.SH' in x]
    sz_o45_ceres_stocks = [x for x in o45_ceres_stocks if '.SZ' in x]
    print(len(sh_o45_saturn_stocks), len(sz_o45_saturn_stocks), len(sh_o45_ceres_stocks), len(sz_o45_ceres_stocks))
    print(set(o45_saturn_stocks+sh_o45_ceres_stocks)-set(o45_InitialBasicParam['股票代码']))
    lm = link.LinkMessage()
    lm.sendMessage('双姐，今天saturn上海%d只，深圳%d只；ceres上海%d只，深圳%d只' % (len(sh_o45_saturn_stocks), len(sz_o45_saturn_stocks), len(sh_o45_ceres_stocks), len(sz_o45_ceres_stocks)))

    sz_InitialBasicParam_new = sz_InitialBasicParam
    o45_param['InitialBasicParam'] = sz_InitialBasicParam_new
    writer = pd.ExcelWriter('/data/group/800463/xiely/daily/excels/param-%s-prod-O45-SZ-new.xlsx'%today)
    for k,v in o45_param.items():
        v.to_excel(writer,sheet_name=k, index=None)
    writer.close()

    sh_InitialBasicParam_new = sh_InitialBasicParam
    o45_param['InitialBasicParam'] = sh_InitialBasicParam_new
    writer = pd.ExcelWriter('/data/group/800463/xiely/daily/excels/param-%s-prod-O45-SH-new.xlsx'%today)
    for k,v in o45_param.items():
        v.to_excel(writer,sheet_name=k, index=None)
    writer.close()
    
gen_sp_param_qianyi()