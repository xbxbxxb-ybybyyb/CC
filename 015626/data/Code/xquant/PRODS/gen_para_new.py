import sys
sys.path.insert(4,'/data/user/016700/')
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import datetime
import os
import json

import numpy as np
import pandas as pd
from pandas import ExcelFile
from loguru import logger
from time import strptime, strftime
import copy

# 放置因子配置文件的根路径，配置文件联系系统团队提供，这些文件不需要每天变化
# 需要修改
factor_definition_root_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition_v7.0.1/'

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
            df = pd.read_excel(xls, sheet_name, dtype = {'买入证券账户': str, '卖出证券账户': str})
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


# 通过3个品种的excel参数文件，生成新的参数文件(4个因子策略，3个模型策略，3个交易策略）
# file_path_dict 入参，字典类型，三个品种的excel文件
# dest_factor_path_list 入参，生成4个因子策略的参数文件列表
# dest_model_path_dict 入参，生成3个模型参数文件，key为 IC IM IF
# dest_trade_path_dict 入参，生成3个交易策略参数文件，key为 IC IM IF
def read_excel(excel_file_path_dict: dict, factor_param_path_list: list, model_param_path_dict: dict,
               trade_param_path_dict: dict):
    path = ''
    reader = 0
    for k, v in excel_file_path_dict.items():
        logger.info("read source excel: ", v)
        xls = pd.ExcelFile(v)
        reader = StrategyExcelReader(xls, v)
        gen_model_param(reader.param_data, model_param_path_dict[k])
        gen_trade_param(reader.param_data, trade_param_path_dict[k])
        if len(path) == 0:
            path = reader.param_data['历史因子文件目录']
        else:
            path = path + "," + reader.param_data['历史因子文件目录']

    i = 1
    for dest_file in factor_param_path_list:
        factor_definition_file = os.path.join(factor_definition_root_path,
                                              "factor_definition_set_part" + str(i) + ".json")
        gen_factor_param(reader.param_data, dest_file, factor_definition_file, path)
        i = i + 1

    return


def safe_delete_form_dict(data_dict: dict, key: str):
    if data_dict.__contains__(key):
        data_dict.pop(key)
    else:
        logger.info("key {} not exist", key)


def gen_factor_param(param_dict: dict, dest_file_name: str, factor_definition_file: str, history_path: str):
    tmp = copy.deepcopy(param_dict)
    json_dict = dict()
    json_dict['计算路径'] = '0'
    for k, v in tmp.items():
        json_dict[k] = v

    json_dict['历史因子文件目录'] = history_path
    json_dict['因子配置文件'] = factor_definition_file

    safe_delete_form_dict(json_dict, "开仓列表")
    safe_delete_form_dict(json_dict, "是否校验历史数据")
    safe_delete_form_dict(json_dict, "FAK下单参数")
    safe_delete_form_dict(json_dict, "信号到仓位配置参数")
    safe_delete_form_dict(json_dict, "信号模型配置列表")
    safe_delete_form_dict(json_dict, "期初持仓列表")
    safe_delete_form_dict(json_dict, '多组模型是否并行预测')

    safe_delete_form_dict(json_dict, "开仓比例")
    safe_delete_form_dict(json_dict, "买入交易账户")
    safe_delete_form_dict(json_dict, "卖出交易账户")
    safe_delete_form_dict(json_dict, "买入证券账户")
    safe_delete_form_dict(json_dict, "卖出证券账户")
    safe_delete_form_dict(json_dict, "合约乘数")
    safe_delete_form_dict(json_dict, "下单价格滑点")
    safe_delete_form_dict(json_dict, "第二阶段下单价格滑点")
    safe_delete_form_dict(json_dict, "下单间隔")
    safe_delete_form_dict(json_dict, "订单存续时间(秒)")
    safe_delete_form_dict(json_dict, "交易开始时间")
    safe_delete_form_dict(json_dict, "开仓截止时间")
    safe_delete_form_dict(json_dict, "平仓开始时间")
    safe_delete_form_dict(json_dict, "平仓结束时间")
    safe_delete_form_dict(json_dict, "废单次数上限")
    safe_delete_form_dict(json_dict, "过去1分钟最大下单次数")
    safe_delete_form_dict(json_dict, "过去1分钟最大撤单次数")
    safe_delete_form_dict(json_dict, "当日成交总量")
    safe_delete_form_dict(json_dict, "当日撤单次数上限")
    safe_delete_form_dict(json_dict, "最大委托次数")
    safe_delete_form_dict(json_dict, "最大撤废次数")
    safe_delete_form_dict(json_dict, "买入交易账户平今仓查询公司")
    safe_delete_form_dict(json_dict, "卖出交易账户平今仓查询公司")
    safe_delete_form_dict(json_dict, "资产单元编号")
    safe_delete_form_dict(json_dict, "基金编号")
    safe_delete_form_dict(json_dict, "保证金查询阈值1(千万元)")
    safe_delete_form_dict(json_dict, "保证金查询阈值2(千万元)")
    safe_delete_form_dict(json_dict, "每分钟成交量上限")
    safe_delete_form_dict(json_dict, "委托参考tick数量")
    safe_delete_form_dict(json_dict, "单笔委托上限")
    safe_delete_form_dict(json_dict, "最大委托价格档位")
    safe_delete_form_dict(json_dict, "第二阶段最大委托价格档位")
    safe_delete_form_dict(json_dict, "下单第一阶段存续时间(S)")
    safe_delete_form_dict(json_dict, "第一阶段下单算法")
    safe_delete_form_dict(json_dict, "第二阶段下单算法")
    safe_delete_form_dict(json_dict, "Alg4撤单间隔时间(ms)")

    with open(dest_file_name, 'wt', encoding='utf-8') as fw:
        # Compatible with Chinese
        json.dump(json_dict, fw, ensure_ascii=False, cls=PdEncoder, indent=4)
    pass


def gen_model_param(param_dict: dict, dest_file_name: str):
    tmp = copy.deepcopy(param_dict)
    json_dict = dict()
    json_dict['计算路径'] = "0"
    for k, v in tmp.items():
        json_dict[k] = v

    safe_delete_form_dict(json_dict, "因子配置文件")
    safe_delete_form_dict(json_dict, "是否记录因子值")
    safe_delete_form_dict(json_dict, "静态信息查询失败时是否使用本地文件")
    safe_delete_form_dict(json_dict, "开始处理分钟聚合数据时间")
    safe_delete_form_dict(json_dict, "中证1800停牌列表")

    variety = 'IC'
    if json_dict.__contains__("开仓列表"):
        variety = json_dict['开仓列表']
        variety = variety.strip()[:2]
        safe_delete_form_dict(json_dict, "开仓列表")

    safe_delete_form_dict(json_dict, "是否校验历史数据")
    safe_delete_form_dict(json_dict, "FAK下单参数")
    safe_delete_form_dict(json_dict, "信号到仓位配置参数")
    safe_delete_form_dict(json_dict, "期初持仓列表")

    if json_dict.__contains__("信号模型配置列表"):
        param_array = json_dict['信号模型配置列表']
        for param in param_array:
            param['合约类型'] = variety

    safe_delete_form_dict(json_dict, "开仓比例")
    safe_delete_form_dict(json_dict, "买入交易账户")
    safe_delete_form_dict(json_dict, "卖出交易账户")
    safe_delete_form_dict(json_dict, "买入证券账户")
    safe_delete_form_dict(json_dict, "卖出证券账户")
    safe_delete_form_dict(json_dict, "合约乘数")
    safe_delete_form_dict(json_dict, "下单价格滑点")
    safe_delete_form_dict(json_dict, "第二阶段下单价格滑点")
    safe_delete_form_dict(json_dict, "下单间隔")
    safe_delete_form_dict(json_dict, "订单存续时间(秒)")
    safe_delete_form_dict(json_dict, "交易开始时间")
    safe_delete_form_dict(json_dict, "开仓截止时间")
    safe_delete_form_dict(json_dict, "平仓开始时间")
    safe_delete_form_dict(json_dict, "平仓结束时间")
    safe_delete_form_dict(json_dict, "废单次数上限")
    safe_delete_form_dict(json_dict, "过去1分钟最大下单次数")
    safe_delete_form_dict(json_dict, "过去1分钟最大撤单次数")
    safe_delete_form_dict(json_dict, "当日成交总量")
    safe_delete_form_dict(json_dict, "当日撤单次数上限")
    safe_delete_form_dict(json_dict, "最大委托次数")
    safe_delete_form_dict(json_dict, "最大撤废次数")
    safe_delete_form_dict(json_dict, "买入交易账户平今仓查询公司")
    safe_delete_form_dict(json_dict, "卖出交易账户平今仓查询公司")
    safe_delete_form_dict(json_dict, "资产单元编号")
    safe_delete_form_dict(json_dict, "基金编号")
    safe_delete_form_dict(json_dict, "保证金查询阈值1(千万元)")
    safe_delete_form_dict(json_dict, "保证金查询阈值2(千万元)")
    safe_delete_form_dict(json_dict, "每分钟成交量上限")
    safe_delete_form_dict(json_dict, "委托参考tick数量")
    safe_delete_form_dict(json_dict, "单笔委托上限")
    safe_delete_form_dict(json_dict, "最大委托价格档位")
    safe_delete_form_dict(json_dict, "第二阶段最大委托价格档位")
    safe_delete_form_dict(json_dict, "下单第一阶段存续时间(S)")
    safe_delete_form_dict(json_dict, "第一阶段下单算法")
    safe_delete_form_dict(json_dict, "第二阶段下单算法")
    safe_delete_form_dict(json_dict, '行情分钟数据目录')

    safe_delete_form_dict(json_dict, "Alg4撤单间隔时间(ms)")
    safe_delete_form_dict(json_dict, '沪深300成分股收盘价信息')
    safe_delete_form_dict(json_dict, '中证500成分股收盘价信息')
    safe_delete_form_dict(json_dict, '中证1000成分股收盘价信息')
    safe_delete_form_dict(json_dict, '最近30个交易日主力近月合约信息')

    with open(dest_file_name, 'wt', encoding='utf-8') as fw:
        # Compatible with Chinese
        json.dump(json_dict, fw, ensure_ascii=False, cls=PdEncoder, indent=4)
    pass


def gen_trade_param(param_dict: dict, dest_json_file):
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

    with open(dest_json_file, 'wt', encoding='utf-8') as fw:
        # Compatible with Chinese
        json.dump(json_dict, fw, ensure_ascii=False, cls=PdEncoder, indent=4)
    pass

from common.tools import *
from xquant.investment.strategyfile import *

if __name__ == '__main__':

    ##############################################
    #####配置项开始#################################
    
    # 交易日
    trade_date = get_next_trading_day(str(check_update_date()[-2]))
    print(trade_date)
    
    # 生成参数文件后放置的路径，此路径下生成的文件用来创建策略，均为.json
    # 需要修改
    param_root_path = f"/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/test_samples/v7.0.1/para/Mobius_{trade_date}_json/"

    # 每日参数，excel 文件，每个品种一个
    # 即老版本用来创建策略的excel文件
    excel_dict = {"IM": f"/data/user/016700/Data/para/Mobius_{trade_date}/MobiusStrategy_IM_{trade_date}#503103.xlsx",
                  "IF": f"/data/user/016700/Data/para/Mobius_{trade_date}/MobiusStrategy_IF_{trade_date}#503102.xlsx",
                  "IC": f"/data/user/016700/Data/para/Mobius_{trade_date}/MobiusStrategy_IC_{trade_date}#503101.xlsx"}
    

    dest_path = os.path.join(param_root_path, trade_date)

    #####不调整策略服务器时，下面的内容不需要修改#################################

    # 需要修改井号后面的zone id
    # 一共需要4台服务器来计算所有因子（包括IC、IF、IM），{因为不同品种有共用的因子，所以把因子进行了合并去重，并不区分品种}
    dest_factor_path_list = [os.path.join(dest_path, trade_date + "_factor_part1" + "#503101.json"),
                             os.path.join(dest_path, trade_date + "_factor_part2" + "#503102.json"),
                             os.path.join(dest_path, trade_date + "_factor_part3" + "#503103.json"),
                             os.path.join(dest_path, trade_date + "_factor_part4" + "#503104.json")]

    # 需要修改井号后面的zone id
    # 一共需要3台服务器来推理模型，分别对应IC、IF、IM
    dest_model_path_dict = {"IC": os.path.join(dest_path, trade_date + "_IC_model" + "#503108.json"),
                            "IF": os.path.join(dest_path, trade_date + "_IF_model" + "#503109.json"),
                            "IM": os.path.join(dest_path, trade_date + "_IM_model" + "#503110.json")
                            }
    # 需要修改井号后面的zone id
    # 只需要一台服务器即可承载3个品种的交易策略。下述三个zone_id填同一个即可
    dest_trade_path_dict = {"IC": os.path.join(dest_path, trade_date + "_IC_trade" + "#503111.json"),
                            "IF": os.path.join(dest_path, trade_date + "_IF_trade" + "#503111.json"),
                            "IM": os.path.join(dest_path, trade_date + "_IM_trade" + "#503111.json")
                            }

    #####配置项结束#################################
    ##############################################

    try:
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
    except OSError as e:
        logger.info("Make dir {} error, {}", dest_path, e)

    read_excel(excel_dict, dest_factor_path_list, dest_model_path_dict, dest_trade_path_dict)

    target_date =  trade_date


    json_para_root = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/test_samples/v7.0.1/para/'
    json_path = os.path.join(json_para_root, f'Mobius_{target_date}_json', target_date)
    factor_zone_dict = {1:'503101', 2:'503102', 3:'503103', 4:'503104'}
    model_zone_dict = {'IC':'503108', 'IF':'503109', 'IM':'503110'}
    trade_zone_dict = {'IC':'503111', 'IF':'503111', 'IM':'503111'}
    for k,v in factor_zone_dict.items():
        upload_strategy_file(strategy_id = "MobiusFactorStrategy", strategy_date = str(target_date), file_type = 1, 
                                upload_file_path = os.path.join(json_path, f'{target_date}_factor_part{k}#{v}.json'), is_delete=False,  is_ready=1)
    for k,v in model_zone_dict.items():
        upload_strategy_file(strategy_id = "MobiusModelStrategy", strategy_date = str(target_date), file_type = 1, 
                                upload_file_path = os.path.join(json_path, f'{target_date}_{k}_model#{v}.json'), is_delete=False,  is_ready=1)
    for k,v in trade_zone_dict.items():
        upload_strategy_file(strategy_id = "MobiusStrategy", strategy_date = str(target_date), file_type = 1, 
                                upload_file_path = os.path.join(json_path, f'{target_date}_{k}_trade#{v}.json'), is_delete=False,  is_ready=1)
                                