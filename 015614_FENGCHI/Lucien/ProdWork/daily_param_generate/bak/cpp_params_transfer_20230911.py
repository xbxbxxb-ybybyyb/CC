import os, json
import numpy as np
import pandas as pd
import zipfile
import shutil

path = '/data/user/013551/forJYY-Strong'  # java 参数地址
output_folder = '/data/user/013551/forJYY-Strong/cpp'  # cpp 参数地址

sz_cnt = sh_cnt = 0
cnt = 0

stocks_sz = []
stocks_sh = []

print("preparing")
for dirr in os.listdir(path):
    if "new" in dirr:
        path1 = os.path.join(path, dirr)
        for dirrr in os.listdir(path1):
            if "zuhe" in dirrr:
                path2 = os.path.join(path1, dirrr)
                for file in os.listdir(path2):
                    if "first" in file or "second" in file or 'third' in file or "fourth" in file:
                        if "SZ" in file: 
                            tmpdf = pd.read_excel(os.path.join(path2, file))
                            stocks_sz += list(tmpdf['证券代码'])
                            print(os.path.join(path2, file)+' removed!')
                            os.remove(os.path.join(path2, file))
                        else:
                            tmpdf = pd.read_excel(os.path.join(path2, file))
                            stocks_sh += list(pd.read_excel(os.path.join(path2, file))['证券代码'])
                            print(os.path.join(path2, file)+' removed!')
                            os.remove(os.path.join(path2, file))

stocks_sz = sorted(stocks_sz)
stocks_sh = sorted(stocks_sh)

for file in os.listdir(output_folder):
    if '-' in file:
        prefix = file.split("-")[0]
    elif '_' in file:
        prefix = file.split("_")[0]
    else:
        prefix = file.split("-")[0]
    if str.isdigit(prefix):
        if os.path.isdir(os.path.join(output_folder, file)):
            shutil.rmtree(os.path.join(output_folder, file))
            print(file)
        else:
            os.remove(os.path.join(output_folder, file))
            print(file)

print("extracting")

for dir in os.listdir(path):
    if "-SH-new" in dir:
        date = dir.split('-')[0]
        if not os.path.exists(os.path.join(output_folder, date)):
            os.makedirs(os.path.join(output_folder, date))
        file_zip = zipfile.ZipFile(os.path.join(path, dir, date + "-prod-O45-SH-new.zip"), 'r')
        for file in file_zip.namelist():
            file_zip.extract(file, os.path.join(output_folder, date, 'temp'))
        file_zip.close()

        output_folder_front = os.path.join(output_folder, date + "-front")
        if not os.path.exists(output_folder_front):
            os.makedirs(output_folder_front)
    if "-SZ-new" in dir:
        date = dir.split('-')[0]
        if not os.path.exists(os.path.join(output_folder, date)):
            os.makedirs(os.path.join(output_folder, date))
        file_zip = zipfile.ZipFile(os.path.join(path, dir, date + "-prod-O45-SZ-new.zip"), 'r')
        for file in file_zip.namelist():
            file_zip.extract(file, os.path.join(output_folder, date, 'temp'))
        file_zip.close()

        output_folder_front = os.path.join(output_folder, date + "-front")
        if not os.path.exists(output_folder_front):
            os.makedirs(output_folder_front)
print(date)
print("copying")
print('SH len: ', len(stocks_sh), 'SZ len: ', len(stocks_sz))

sellforbuy_list1 = pd.read_excel(r'/data/group/800463/xiely/sp/stocklist_small/成交流水_%s_small.xlsx'%'20230905')
sellforbuy_list1 = sellforbuy_list1[~sellforbuy_list1['序号'].str.startswith('总行')]['证券代码'].values.tolist()
sellforbuy_list2 = pd.read_excel(r'/data/group/800463/xiely/sp/stocklist_small/成交流水_%s_small.xlsx'%'20230912')
sellforbuy_list2 = sellforbuy_list2[~sellforbuy_list2['序号'].str.startswith('总行')]['证券代码'].values.tolist()
sellforbuy_list = sellforbuy_list1 + sellforbuy_list2

sellforbuy_list = [str(int(x)) for x in sellforbuy_list]
sellforbuy_list = ['0'*(6-len(x))+x for x in sellforbuy_list]
sellforbuy_list = [x+'.SH' if x[0]=='6' else x+'.SZ' for x in sellforbuy_list]
print('len(sellforbuy_list): ', len(sellforbuy_list))

still_position_df = pd.read_excel(r'/data/group/800463/position/O45_组合证券_%s_origin.xlsx'%date)
still_position_stocklist = still_position_df[still_position_df['T日指令可用数量']>0]['证券代码'].values.tolist()
still_position_stocklist = [str(int(x)) for x in still_position_stocklist]
still_position_stocklist = ['0'*(6-len(x))+x for x in still_position_stocklist]
still_position_stocklist = [x+'.SH' if x[0]=='6' else x+'.SZ' for x in still_position_stocklist]
print(len(set(sellforbuy_list).intersection(set(still_position_stocklist))))
sellforbuy_list = [x for x in sellforbuy_list if x in still_position_stocklist]
print('len(sellforbuy_list): ', len(sellforbuy_list))

sellforbuy_list_cpp = []

sh_zuhe_name = 'EventCPPSH%s'%date
cpp_sh_zuhe = pd.DataFrame(index=stocks_sh)
cpp_sh_zuhe['买入交易账户'] = '2000000100'
cpp_sh_zuhe['卖出交易账户'] = '2000000100'
cpp_sh_zuhe['买入证券数量'] = '10000000'
cpp_sh_zuhe['卖出证券数量'] = '0'
cpp_sh_zuhe.index.rename('证券代码',inplace=True)
if not os.path.exists(os.path.join(output_folder_front, "zuhe-prod")):
    os.mkdir(os.path.join(output_folder_front, "zuhe-prod"))
cpp_sh_zuhe.loc[cpp_sh_zuhe.index.isin(sellforbuy_list), '卖出证券数量'] = '100'
cpp_sh_zuhe.to_excel(os.path.join(output_folder_front, "zuhe-prod")+'/%s.xlsx'%sh_zuhe_name)

sz_zuhe_name = 'EventCPPSZ%s'%date
cpp_sz_zuhe = pd.DataFrame(index=stocks_sz)
cpp_sz_zuhe['买入交易账户'] = '20000002'
cpp_sz_zuhe['卖出交易账户'] = '20000002'
cpp_sz_zuhe['买入证券数量'] = '10000000'
cpp_sz_zuhe['卖出证券数量'] = '0'
cpp_sz_zuhe.index.rename('证券代码',inplace=True)
if not os.path.exists(os.path.join(output_folder_front, "zuhe-prod")):
    os.mkdir(os.path.join(output_folder_front, "zuhe-prod"))
cpp_sz_zuhe.loc[cpp_sz_zuhe.index.isin(sellforbuy_list), '卖出证券数量'] = '100'
cpp_sz_zuhe.to_excel(os.path.join(output_folder_front, "zuhe-prod")+'/%s.xlsx'%sz_zuhe_name)


shutil.copytree(os.path.join(output_folder, "backup", "eventdriven_fast-front"),
                os.path.join(output_folder_front, "eventdriven_fast-front"))

shutil.copytree(os.path.join(output_folder, "backup", "eventdriven_udp-front"),
                os.path.join(output_folder_front, "eventdriven_udp-front"))

print("reading")

small_test_list_sh = stocks_sh[:6]
small_test_list_sz = stocks_sz[:6]

ycbd_5_stocklist = pd.read_excel(r'/data/group/800463/stock_list/ycbd_list/ycbd_list_%s.xlsx'%date)
ycbd_5_stocklist = ycbd_5_stocklist['stk_code'].values.tolist()

for dir in os.listdir(os.path.join(output_folder, date, 'temp')):
    for f in os.listdir(os.path.join(output_folder, date, 'temp', dir)):
        with open(os.path.join(output_folder, date, 'temp', dir, f), "r", encoding="utf-8") as file:
            info = json.load(file)
        symbol = info["股票代码"]
        if symbol not in stocks_sh+stocks_sz:
            continue
        info["允许买入开始时间"] = str(int(str(info["允许买入开始时间"].replace(":", "")))) + "000"
        info["允许卖出开始时间"] = str(int(str(info["允许卖出开始时间"].replace(":", "")))) + "000"
        info["允许买入结束时间"] = str(int(str(info["允许买入结束时间"].replace(":", "")))) + "000"
        info["允许卖出结束时间"] = str(int(str(info["允许卖出结束时间"].replace(":", "")))) + "000"
        info["取消订阅非必要行情时间"] = str(int(str(info["取消订阅非必要行情时间"].replace(":", "")))) + "000"
        info["强制撤单时间点"] = str(int(str(info["强制撤单时间点"].replace(":", "")))) + "000"  # "93000000"

        for cell in info["股票数据"]:
            cell['昨收价'] = str(cell['昨收价'])
            cell['昨日最高价'] = str(cell['昨日最高价'])
            if '昨日流通股份' not in cell or np.isnan(cell['昨日流通股份']):
                cell['昨日流通股份'] = "0"
            else:
                cell['昨日流通股份'] = str(cell['昨日流通股份'])

        info["参数目录"] = "/home/appadmin/ATS-Quant-prod/resources/JGStrategy/JupiterStrategy"
        info["JupiterNew模型目录"] = "/home/appadmin/ATS-Quant-prod/resources/JGStrategy/JupiterNewStrategy"
        info["是否验证模式"] = "0"
        if symbol in sellforbuy_list:
            info["Event开关"] = "1"
            sellforbuy_list_cpp.append(symbol)
        else:
            info["Event开关"] = "0"
        info["时间点1"] = "91501000"
        info["股数1"] = "100"
        info['时间点2'] = "93100000"
        
#        if symbol in small_test_list_sh+small_test_list_sz:
#            info["小单测试"] = "1"
#            print(symbol," 小单测试!")
        
        info["Jupiter策略启动组合"] = "0"
        save_path_europa = os.path.join(output_folder, info["交易日期"] + "_europa")
        if not os.path.exists(save_path_europa):
            os.mkdir(save_path_europa)
        json.dump(info, open(os.path.join(save_path_europa, symbol + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        info["Event开关"] = "0"
        info["Jupiter策略启动组合"] = "1"
        if symbol in ycbd_5_stocklist:
            print('jupiter 0 symbol: ', symbol)
            info["单票持仓总规模上限"] = "0"
        save_path_jupiter = os.path.join(output_folder, info["交易日期"] + "_jupiter")
        if not os.path.exists(save_path_jupiter):
            os.mkdir(save_path_jupiter)
        json.dump(info, open(os.path.join(save_path_jupiter, symbol + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        cnt += 1

print("generating")
print(len(sellforbuy_list), len(sellforbuy_list_cpp), set(sellforbuy_list)-set(sellforbuy_list_cpp))
print(set(sellforbuy_list_cpp)-set(sellforbuy_list))
print(len([x for x in sellforbuy_list_cpp if '.SH' in x]), len([x for x in sellforbuy_list_cpp if '.SZ' in x]))


def gen_params(date, output_folder, output_folder_front, config, stock_paths, is_sz):
    udp_name = config['udp']
    fast_name = config['fast']
    output_name = config['zuhe_name'] + config['zone']

    symbol_list = stock_paths
    if config['split'] == 'left':
        symbol_list = stock_paths[:len(stock_paths) // 2]
    elif config['split'] == 'right':
        symbol_list = stock_paths[len(stock_paths) // 2:]

    save_path = os.path.join(output_folder, date + '-prd')
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    backend_params = {
        "TargetSymbolsList": [],
        "UDPTransactionBandNames": "",
        "FastTransactionBandNames": "",
        "TickBandNames": "tick_udp",
        "QueryConstantTime": "91000000",
        "Channel": ""
    }

    if config['isEuropa']:
        symbol_list = ["/home/appadmin/cppParam/EventDriven/" + date + "_europa/" + file for file in
                       symbol_list]
    else:
        symbol_list = ["/home/appadmin/cppParam/EventDriven/" + date + "_jupiter/" + file for file in
                       symbol_list]
                    
    backend_params["TargetSymbolsList"] = symbol_list
    backend_params["UDPTransactionBandNames"] = udp_name
    backend_params["FastTransactionBandNames"] = fast_name
    backend_params["Channel"] = fast_name.split("_")[-1]
    backend_params['EventSwitch'] = config['EventSwitch']
    backend_params['单批次数量'] = config['单批次数量']
    backend_params['分批间隔秒数'] = config['分批间隔秒数']
    backend_params["sell撤单时间"] = "143000000"

    if udp_name.startswith('sh_'):
        backend_params[
            "UDPTransactionBandList"] = "sh_market_data_udp_1,sh_market_data_udp_2,sh_market_data_udp_3,sh_market_data_udp_4,sh_market_data_udp_5,sh_market_data_udp_6"
        backend_params[
            "FastTransactionBandList"] = "sh_market_data_fast_1,sh_market_data_fast_2,sh_market_data_fast_3,sh_market_data_fast_4,sh_market_data_fast_5,sh_market_data_fast_6"
    else:
        backend_params[
            "UDPTransactionBandList"] = "sz_market_data_udp_2011,sz_market_data_udp_2012,sz_market_data_udp_2013,sz_market_data_udp_2014"
        backend_params[
            "FastTransactionBandList"] = "sz_market_data_fast_2011,sz_market_data_fast_2012,sz_market_data_fast_2013,sz_market_data_fast_2014"

    json.dump(backend_params, open(os.path.join(save_path, "backend_" + output_name), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    params = {"参数地址": os.path.join("/home/appadmin/cppParam/EventDriven", date + '-prd', "backend_" + output_name)}
    dirr = date + "-cpp-" + ("SZ" if is_sz else "SH") + "-front"
    output_folder_front = os.path.join(output_folder_front, dirr)
    if not os.path.exists(output_folder_front):
        os.mkdir(output_folder_front)
    json.dump(params, open(os.path.join(output_folder_front, output_name), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


SINGLE_BATCH_SIZE = '500'
BATCH_GAP_SECONDS = '30'
sz_config = [
    {"udp": "sz_market_data_udp_2011", 'fast': "sz_market_data_fast_2011", "zone": "#303202.json", "zuhe_name": "SZ$%s$CH2011_0"%sz_zuhe_name,
     "split": "all", "EventSwitch": "1", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sz_market_data_udp_2011", 'fast': "sz_market_data_fast_2011", "zone": "#303208.json", "zuhe_name": "SZ$%s$CH2011_1"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    
    {"udp": "sz_market_data_udp_2012", 'fast': "sz_market_data_fast_2012", "zone": "#303203.json", "zuhe_name": "SZ$%s$CH2012_0"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sz_market_data_udp_2012", 'fast': "sz_market_data_fast_2012", "zone": "#303209.json", "zuhe_name": "SZ$%s$CH2012_1"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    
    {"udp": "sz_market_data_udp_2013", 'fast': "sz_market_data_fast_2013", "zone": "#303204.json", "zuhe_name": "SZ$%s$CH2013_0"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sz_market_data_udp_2013", 'fast': "sz_market_data_fast_2013", "zone": "#303207.json", "zuhe_name": "SZ$%s$CH2013_1"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    
    {"udp": "sz_market_data_udp_2014", 'fast': "sz_market_data_fast_2014", "zone": "#303205.json", "zuhe_name": "SZ$%s$CH2014_0"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sz_market_data_udp_2014", 'fast': "sz_market_data_fast_2014", "zone": "#303206.json", "zuhe_name": "SZ$%s$CH2014_1"%sz_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False}
    
]

stock_paths = []
for file in sorted(os.listdir(os.path.join(output_folder, date + "_europa"))):
    if file[:-5] in stocks_sz:
        stock_paths.append(file[:-5] + '.json')

for config in sz_config:
    gen_params(date, output_folder, output_folder_front, config, stock_paths, True)

sh_config = [
    {"udp": "sh_market_data_udp_1", 'fast': "sh_market_data_fast_1", "zone": "#303101.json", "zuhe_name": "SH$%s$CH1_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "1", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},  
    {"udp": "sh_market_data_udp_2", 'fast': "sh_market_data_fast_2", "zone": "#303103.json", "zuhe_name": "SH$%s$CH2_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sh_market_data_udp_3", 'fast': "sh_market_data_fast_3", "zone": "#303104.json", "zuhe_name": "SH$%s$CH3_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sh_market_data_udp_4", 'fast': "sh_market_data_fast_4", "zone": "#303105.json", "zuhe_name": "SH$%s$CH4_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sh_market_data_udp_5", 'fast': "sh_market_data_fast_5", "zone": "#303106.json", "zuhe_name": "SH$%s$CH5_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},
    {"udp": "sh_market_data_udp_6", 'fast': "sh_market_data_fast_6", "zone": "#303102.json", "zuhe_name": "SH$%s$CH6_0"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": True},

    {"udp": "sh_market_data_udp_1", 'fast': "sh_market_data_fast_1", "zone": "#303111.json", "zuhe_name": "SH$%s$CH1_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    {"udp": "sh_market_data_udp_2", 'fast': "sh_market_data_fast_2", "zone": "#303107.json", "zuhe_name": "SH$%s$CH2_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    {"udp": "sh_market_data_udp_3", 'fast': "sh_market_data_fast_3", "zone": "#303108.json", "zuhe_name": "SH$%s$CH3_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    {"udp": "sh_market_data_udp_4", 'fast': "sh_market_data_fast_4", "zone": "#303109.json", "zuhe_name": "SH$%s$CH4_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    {"udp": "sh_market_data_udp_5", 'fast': "sh_market_data_fast_5", "zone": "#303110.json", "zuhe_name": "SH$%s$CH5_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False},
    {"udp": "sh_market_data_udp_6", 'fast': "sh_market_data_fast_6", "zone": "#303112.json", "zuhe_name": "SH$%s$CH6_1"%sh_zuhe_name,
     "split": "all", "EventSwitch": "0", "单批次数量": SINGLE_BATCH_SIZE, "分批间隔秒数": BATCH_GAP_SECONDS, "isEuropa": False}
]


stock_paths = []
for file in sorted(os.listdir(os.path.join(output_folder, date + "_europa"))):
    if file[:-5] in stocks_sh:
        stock_paths.append(file[:-5] + '.json')    
        
for config in sh_config:
    gen_params(date, output_folder, output_folder_front, config, stock_paths, False)

print("archiving")


def zipDir(dirpaths, outFullName):
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for par in dirpaths:
        dirpath, tailfix = par
        for path, dirnames, filenames in os.walk(dirpath):
            fpath = path.replace(dirpath, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, tailfix, filename))
    zip.close()


zipDir([(os.path.join(output_folder_front, "eventdriven_fast-front"), "")],
       os.path.join(output_folder, date + "-eventdriven_fast-front.zip"))
zipDir([(os.path.join(output_folder_front, "eventdriven_udp-front"), "")],
       os.path.join(output_folder, date + "-eventdriven_udp-front.zip"))
zipDir([(os.path.join(output_folder_front, "zuhe-prod"), "")],
       os.path.join(output_folder, date + "-eventdriven_zuhe.zip"))

archive_targets = [(os.path.join(output_folder_front, date + "-cpp-SH-front"), date + "-cpp-SH-front"),
                   (os.path.join(output_folder_front, date + "-cpp-SZ-front"), date + "-cpp-SZ-front")]
params_path = os.path.join(output_folder, date + "-eventdriven-front.zip")
zipDir(archive_targets, params_path)

shutil.make_archive(os.path.join(output_folder, date + "-eventdriven-front-all"), 'zip',
                    output_folder_front)

print("cleaning")

shutil.rmtree(os.path.join(output_folder, date, 'temp'))
shutil.rmtree(output_folder_front)

print("finished:", cnt, "in total")
