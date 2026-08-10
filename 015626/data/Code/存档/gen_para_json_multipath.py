# 因子
import sys
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')
from multifactor.data.utils import *
import multifactor.utility.dt as udt

import datetime
import json
import os
import sys
from xquant.investment.strategyfile import *

is_prod = True # False表示为仿真参数

# 获取当前日期
tday = str(check_update_date()[0])
current_date = udt.get_trading_day_offset(tday, 1)[0].strftime('%Y%m%d')
#current_date = '20250704'

print('current_date: ', current_date)
# 计算路径列表
compute_paths = ['0', '50', '55']
# compute_paths = ['0']

if is_prod:
    # 父目录路径（根据交易日期生成）
    parent_dir = f"/data/user/015626/data/share/para/Mobius_json_para/{current_date}"
    # 模型参数保存路径
    dest_model_path = '/data/user/015626/data/share/para/Mobius_json_para/'   # 需要修改 
else:
    # 父目录路径（根据交易日期生成）
    parent_dir = f"/data/user/015626/data/share/para/Mobius_json_para_sim/{current_date}"
    # 模型参数保存路径
    dest_model_path = '/data/user/015626/data/share/para/Mobius_json_para_sim/'   # 需要修改 

# 模型参数生成所需模板文件，非常重要，需要修改
template_path = '/data/user/015626/data/share/para/Mobius_json_para/gen_mobius_params/template/model/'  # 需要修改


excel_dict = {"IM": f"/data/user/015626/data/share/para/Mobius_para/Mobius_{current_date}/MobiusStrategy_IM_{current_date}#503103.xlsx",
              "IF": f"/data/user/015626/data/share/para/Mobius_para/Mobius_{current_date}/MobiusStrategy_IF_{current_date}#503102.xlsx",
              "IC": f"/data/user/015626/data/share/para/Mobius_para/Mobius_{current_date}/MobiusStrategy_IC_{current_date}#503101.xlsx"}
            
factor_definition_root_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition_v7.0.1/'
if is_prod:
    factor_def_zone = {
     'factor_definition_set_part1.json':503101,
     'factor_definition_set_part2.json':503102,
     'factor_definition_set_part3.json':503103,
     'factor_definition_set_part4.json':503104}
else:
    factor_def_zone = {
     'factor_definition_set_part1.json':303312,
     'factor_definition_set_part2.json':303313,
     'factor_definition_set_part3.json':303314,
     'factor_definition_set_part4.json':303315}

# 遍历计算路径列表，生成每个路径对应的文件
for compute_path in compute_paths:
    for factor_def, zone in factor_def_zone.items():
        # 构建完整路径（包含 offset 文件夹）
        offset_folder = f"offset_{compute_path}"
        full_path = os.path.join(parent_dir, offset_folder,'factor')
    
        # 确保目标目录存在，如果不存在则创建
        os.makedirs(full_path, exist_ok=True)
    
        # 生成 config.json 文件
        config = {
            "交易日期": current_date,
            "历史数据目录": "/data/user/666466/06_prod_data/02_FactorData",
            "日频数据目录": "/data/user/666466/06_prod_data/00_MarketData",
            "因子配置文件": os.path.join(factor_definition_root_path, factor_def),
            "是否记录因子值": "True",
            "静态信息查询失败时是否使用本地文件": "True",
            "开始处理分钟聚合数据时间": "09:30:00",
            "计算路径": compute_path
        }
    
        # 生成 config.json 文件路径
        config_filename = f"{current_date}_factor_{factor_def.split('_')[-1].replace('.json', '')}_offset_{compute_path}#{zone}.json"
        config_file_path = os.path.join(full_path, config_filename)
    
        with open(config_file_path, 'w') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        if is_prod:
            upload_strategy_file(strategy_id = "MobiusFactorStrategy", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = config_file_path, is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)            
        else:
            sim_upload_strategy_file(strategy_id = "MobiusFactorStrategy", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = config_file_path, is_delete=False,  is_ready=1)  
                            
                            
# ******************************** 截面指标  *********************************************
if is_prod:
    jiemian_zone = [503106, 503107, 503112]
else:
    jiemian_zone = [303317, 303318, 303319]

jiemian_path = os.path.join(parent_dir, 'MobiusCrossSectionCalculator')
os.makedirs(jiemian_path, exist_ok=True)
for zone in jiemian_zone:
    config = {
        "path":""
    }
    config_filename = f"front_MobiusCrossSectionCalculator#{zone}.json"
    config_file_path = os.path.join(jiemian_path, config_filename)

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    if is_prod:
        upload_strategy_file(strategy_id = "MobiusCrossSectionCalculator", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = config_file_path, is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)
    else:
        sim_upload_strategy_file(strategy_id = "MobiusCrossSectionCalculator", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = config_file_path, is_delete=False,  is_ready=1)
              
            
# ************************************ 模型 ******************************************************
import json
import os
from xquant.factordata import FactorData
from datetime import date
from loguru import logger

def send_link_message(msg):
    print(msg)
    # lm = notice.LinkMessage()
    # lm.sendMessage(msg)


def gen_params_json(tday, zone, dest_path, template_file, variety_str, trade_day, root_data_path, offset_str='00', rank_type='norm2'):
    if not os.path.exists(dest_path):
        os.makedirs(dest_path, exist_ok=True)

    if offset_str == '0':
        model_config = {"IC": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7unifac/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7unifac_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            },{
                "信号编号": 3,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7unifac_crn_trend/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            },
            {
                "信号编号": 4,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7_crn_ew/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            },
                              ]
        , "IF": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7c/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            },{
                "信号编号": 3,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7_crn_trend/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            },
            {
                "信号编号": 4,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7_crn_ew/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            }]
        , "IM": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1unifac_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1unifac/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            },{
                "信号编号": 3,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1unifac_crn_trend/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            },
            {
                "信号编号": 4,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1_crn_ew/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            }]
        }
    else:
        model_config = {"IC": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7unifac/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_ic_ic_v7unifac_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IC"
            }]
        , "IF": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7c/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_if_if_v7_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IF"
            }]
        , "IM": [{
                "信号编号": 1,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1unifac_crn/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            },
            {
                "信号编号": 2,
                "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20250328_im_im_v1unifac/",
                "历史信号文件目录": "",
                "波动率时间窗口": 0,
                "Rank周期1": 4800,
                "Rank周期2": 2400,
                "LSTM模型输入因子步长": 10,
                "Rank计算方法": "norm2",
                "合约类型": "IM"
            }]
        }
        
    configs = model_config.get(variety_str)
    if configs is None:
        return
    for config in configs:
        model_path = config['对应模型目录'].strip()
        if model_path.endswith('/'):
            model_path = model_path[:-1]
        arrays = model_path.split("/")
        model_name = arrays[-1]
        config["历史信号文件目录"] = os.path.join(root_data_path, trade_day, 'offset_' + offset_str, '03_signal', model_name, 'history_files/signalNorm2Value')
        config['Rank计算方法'] = rank_type

    params_file = f'{tday}_{variety_str}_model_offset_{offset_str}_#{zone}.json'
    with open(template_file, mode='r') as f:
        json_obj = json.load(f)
        json_obj['交易日期'] = trade_day
        json_obj['历史数据根目录'] = root_data_path
        json_obj['计算路径'] = '0' if offset_str.startswith('00') else offset_str
        json_obj['信号模型配置列表'].clear()
        json_obj['信号模型配置列表'] = configs
        with open(os.path.join(dest_path, params_file), "w") as fw:
            fw.write(json.dumps(json_obj, indent=4, ensure_ascii=False))
        if is_prod:
            upload_strategy_file(strategy_id = "MobiusModelStrategy", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = os.path.join(dest_path, params_file), is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)
        else:
            sim_upload_strategy_file(strategy_id = "MobiusModelStrategy", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = os.path.join(dest_path, params_file), is_delete=False,  is_ready=1)


def param_entry(trading_day, offset, model_variety_zone_dict, template_path, dest_model_path):
    root_data_path = '/data/user/666466/06_prod_data/02_FactorData'

    logger.info("begin to generate param")
    for variety, zone in model_variety_zone_dict.items():
        logger.info("offset={}, variety={}", offset, variety)
        dest = os.path.join(dest_model_path, trading_day, 'offset_' + offset, 'model', variety)
        logger.info("param will write to {}", dest)
        gen_params_json(trading_day, zone, dest, os.path.join(template_path, 'params.json'), variety, trading_day, root_data_path, offset)
        
if is_prod:
    model_variety_zone_dict = {'IC':'503108', 'IF':'503109', 'IM':'503110'}
else:
    model_variety_zone_dict = {'IC':303320, 'IF':303321, 'IM':303322}

for compute_path in compute_paths:
    param_entry(current_date, compute_path, model_variety_zone_dict, template_path, dest_model_path)
    
    
# ******************************************* 交易 ************************************************
from pandas import ExcelFile
from loguru import logger
from time import strptime, strftime
import copy

class PdEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return str(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y%m%d")
        if isinstance(obj, pd.Timestamp):
            return obj.strftime("%Y-%m-%d")
        return super(PdEncoder, self).default(obj)

class StrategyExcelReader(object):
    def __init__(self, xls, excel_name):
        logger.info(f"sheet names:{xls.sheet_names}")
        self._xls = xls
        self._excel_name = excel_name
        self._param_data = dict()
        self.deal_sheets(xls=self._xls, sheet_names=self._xls.sheet_names)
        self._trade_time = strptime(self._trade_date, "%Y%m%d")
        logger.info(f"symbol: {self._symbol}, trade date: {self._trade_date}")
        # logger.info(f"param data:\n {self._param_data}")
        logger.info(f"StrategyExcelReader init done, excel name: {self._excel_name}")
        self._adapt_windows()

    def dump(self, save_param_path, save_request_path):
        self._dump_test_case(save_param_path, save_request_path)

    def _dump_test_case(self, dump_params_path: str, dump_request_path: str):
        with open(dump_params_path, 'wt', encoding='utf-8') as fw:
            # Compatible with Chinese
            json.dump(self._param_data, fw, ensure_ascii=False, cls=PdEncoder)

        with open(dump_request_path, 'w', encoding='utf-8') as fw:
            json.dump(self._request_data, fw, cls=PdEncoder)

    def _adapt_windows(self):
        if '订单存续时间(秒)' not in self._param_data:
            self._param_data['订单存续时间(秒)'] = 10

        format_date = strftime("%Y-%m-%d", self._trade_time)

        logger.info("trading date in request file: {}".format(format_date))

    def _load_config_file_templates(self, local_params_path):
        with open(local_params_path, encoding='utf-8') as file:
            self._param_data = json.load(file)

    @property
    def param_data(self):
        return self._param_data

    @property
    def symbol(self):
        return self._symbol

    @property
    def trade_date(self):
        return self._trade_date

    def _extract_list_dict(self, df, sheet_name):
        data = []
        for idx in df.index:
            data_row = {}
            for col in df.columns:
                value = df.loc[idx, col]
                if isinstance(value, pd.Timestamp):
                    value = value.strftime("%Y-%m-%d")
                if isinstance(value, str):
                    value = value.strip()
                data_row[col] = value
            data.append(data_row)
        self._param_data[sheet_name] = data

    def _extract_hs300_stock_info(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_zz500_stock_info(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_recent_30_trading_days_info(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_zz1000_stock_info(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_initial_basic_param(self, df):
        for col in df.columns:
            value = str(df.loc[0, col]).strip()
            self._param_data[str(col)] = value
            if col == '开仓列表':
                strs = value.split(',')
                self._symbol = strs[0]
            elif col == '交易日期':
                self._trade_date = value

    def _extract_signal_position(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_init_position(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_signal_config(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def _extract_fak_param(self, df, sheet_name):
        self._extract_list_dict(df, sheet_name)

    def deal_sheets(self, xls: ExcelFile, sheet_names: list):
        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name, dtype = {'买入证券账户':str, '卖出证券账户':str})
            if sheet_name == 'InitialBasicParam':
                self._extract_initial_basic_param(df)
            elif sheet_name == '信号到仓位配置参数':
                self._extract_signal_position(df, sheet_name)
            elif sheet_name == '沪深300成分股收盘价信息':
                self._extract_hs300_stock_info(df, sheet_name)
            elif sheet_name == '中证500成分股收盘价信息':
                self._extract_zz500_stock_info(df, sheet_name)
            elif sheet_name == '中证1000成分股收盘价信息':
                self._extract_zz1000_stock_info(df, sheet_name)
            elif sheet_name == '最近30个交易日主力近月合约信息':
                self._extract_recent_30_trading_days_info(df, sheet_name)
            elif sheet_name == '期初持仓列表':
                self._extract_init_position(df, sheet_name)
            elif sheet_name == '信号模型配置列表':
                self._extract_signal_config(df, sheet_name)
            elif sheet_name == "FAK下单参数":
                self._extract_fak_param(df, sheet_name)
                
def safe_delete_form_dict(data_dict: dict, key: str):
    if data_dict.__contains__(key):
        data_dict.pop(key)
    else:
        logger.info("key {} not exist", key)
        
def read_excel(excel_file_path_dict: dict):
    path = ''
    reader = 0
    for k, v in excel_file_path_dict.items():
        logger.info("read source excel: ", v)
        xls = pd.ExcelFile(v)
        reader = StrategyExcelReader(xls, v)
        gen_trade_param(reader.param_data, trade_param_path_dict[k])


def gen_trade_param(param_dict: dict):
    json_dict = copy.deepcopy(param_dict)
    if not json_dict.__contains__("Alg4撤单间隔时间(ms)"):
        json_dict["Alg4撤单间隔时间(ms)"] = "100"

    safe_delete_form_dict(json_dict, '沪深300成分股收盘价信息')
    safe_delete_form_dict(json_dict, '中证500成分股收盘价信息')
    safe_delete_form_dict(json_dict, '中证1000成分股收盘价信息')
    safe_delete_form_dict(json_dict, "最近30个交易日主力近月合约信息")

    safe_delete_form_dict(json_dict, '行情分钟数据目录')
    safe_delete_form_dict(json_dict, '历史因子文件目录')
    safe_delete_form_dict(json_dict, '因子配置文件')
    safe_delete_form_dict(json_dict, '是否记录因子值')

    safe_delete_form_dict(json_dict, '静态信息查询失败时是否使用本地文件')
    safe_delete_form_dict(json_dict, '是否校验历史数据')
    safe_delete_form_dict(json_dict, '多组模型是否并行预测')
    safe_delete_form_dict(json_dict, '中证1800停牌列表')
    safe_delete_form_dict(json_dict, '开始处理分钟聚合数据时间')

    if json_dict.__contains__("信号到仓位配置参数"):
        param_array = json_dict['信号到仓位配置参数']
        for param in param_array:
            param['时间路径'] = 0
    if json_dict.__contains__("信号模型配置列表"):
        param_array = json_dict['信号模型配置列表']
        for param in param_array:
            param['时间路径'] = 0
            safe_delete_form_dict(param, '波动率时间窗口')
            safe_delete_form_dict(param, '对应模型目录')
            safe_delete_form_dict(param, '历史信号文件目录')
            safe_delete_form_dict(param, 'Rank周期1')
            safe_delete_form_dict(param, 'Rank周期2')
            safe_delete_form_dict(param, 'LSTM模型输入因子步长')
            safe_delete_form_dict(param, 'Rank计算方法')

    return json_dict
    
if is_prod:
    zone = 503111
else:
    zone = 303316

_cash = 0
_cash_55 = 10
multipath_cash_dict = {
    'IC':{'50':{1:_cash,2:_cash},
          '55':{1:_cash_55,2:_cash_55}},
    'IF':{'50':{1:_cash,2:_cash},
          '55':{1:_cash_55,2:_cash_55}},
    'IM':{'50':{1:_cash,2:_cash},
          '55':{1:_cash_55,2:_cash_55}}
}

for future_kind in ['IC', 'IF', 'IM']:
    cash_dict = multipath_cash_dict[future_kind]
    
    xls = pd.ExcelFile(excel_dict[future_kind])
    reader = StrategyExcelReader(xls, excel_dict[future_kind])
    data = gen_trade_param(reader.param_data)
    
    list1 = []
    list2 = []
    for path in compute_paths:
        for _ in data['信号到仓位配置参数']:
            x = _.copy()
            x['时间路径'] = path
            if path in cash_dict.keys():
                if x['所属信号编号'] in list(cash_dict[path].keys()):
                    list1.append(x)
            else:
                list1.append(x)
        for _ in data['信号模型配置列表']:
            y = _.copy()
            y['时间路径'] = path
            if path in cash_dict.keys():
                if y['信号编号'] in list(cash_dict[path].keys()):
                    y['初始资金（千万元）'] = cash_dict[path][y['信号编号']]
                    list2.append(y)
            else:
                list2.append(y)
    
    data['信号到仓位配置参数'] = list1
    data['信号模型配置列表'] = list2
    trade_path = os.path.join(parent_dir, 'MobiusStrategy')
    os.makedirs(trade_path, exist_ok=True)
    
    config_filename = f"{current_date}_{future_kind}_trade#{zone}.json"
    config_file_path = os.path.join(trade_path, config_filename)
    
    with open(config_file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, cls=PdEncoder)

    if is_prod:
        upload_strategy_file(strategy_id = "MobiusStrategy", strategy_date = str(current_date), file_type = 1, 
                            upload_file_path = config_file_path, is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)
    else:
        sim_upload_strategy_file(strategy_id = "MobiusStrategy", strategy_date = str(current_date), file_type = 1, 
                        upload_file_path = config_file_path, is_delete=False,  is_ready=1)