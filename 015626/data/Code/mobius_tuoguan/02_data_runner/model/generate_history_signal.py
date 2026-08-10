import os
from check_log import check_log_file
from loguru import logger
from datetime import date
from xquant.factordata import FactorData
from gen_signal_norm2 import rank_index
import notice
import sys
import json
from xquant.factordata import FactorData



def gen_request_json(dest_path, template_file, trade_day, root_data_path, offset):
    request_file = 'request.json'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path, exist_ok=True)
    if len(trade_day) != 8:
        print(trade_day + ' not valid')
        return None
    trade_day = trade_day[:4] + '-' + trade_day[4:6] + '-' + trade_day[-2:]
    with open(template_file, mode='r') as f:
        json_obj = json.load(f)
        json_obj['StartDate'] = trade_day
        json_obj['EndDate'] = trade_day
        json_obj['SpecHisotryMDServiceParam']['开始日期'] = trade_day
        json_obj['SpecHisotryMDServiceParam']['结束日期'] = trade_day
        json_obj['SpecHisotryMDServiceParam']['replayFile'] = root_data_path
        json_obj['SpecHisotryMDServiceParam']['计算路径'] = 0 if offset.startswith('00') else int(offset)
        with open(os.path.join(dest_path, request_file), "w") as fw:
            fw.write(json.dumps(json_obj, indent=4, ensure_ascii=False))


def gen_params_json(dest_path, template_file, variety_str, trade_day, root_data_path, offset_str='00', rank_type='norm2'):
    if not os.path.exists(dest_path):
        os.makedirs(dest_path, exist_ok=True)

    model_config = {"IM": [{
        "信号编号": 1,
        "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20241213_im_im_v1unifac",
        "历史信号文件目录": "/data/user/012129/mobius/04_FactorData/trade_files/20250228_20241213_ic_ic_v7unifac/signalNorm2Value/",
        "波动率时间窗口": 0,
        "Rank周期1": 4800,
        "Rank周期2": 2400,
        "LSTM模型输入因子步长": 10,
        "Rank计算方法": "norm2",
        "合约类型": "IM"
    },
        {
            "信号编号": 2,
            "对应模型目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/20241213_im_im_v1unifac_crn",
            "历史信号文件目录": "/data/user/012129/mobius/04_FactorData/trade_files/20250228_20241213_ic_ic_v7unifac_crn/signalNorm2Value/",
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

    params_file = 'params.json'
    with open(template_file, mode='r') as f:
        json_obj = json.load(f)
        json_obj['交易日期'] = trade_day
        json_obj['历史数据根目录'] = root_data_path
        json_obj['计算路径'] = '0' if offset_str.startswith('00') else offset_str
        json_obj['信号模型配置列表'].clear()
        json_obj['信号模型配置列表'] = configs
        with open(os.path.join(dest_path, params_file), "w") as fw:
            fw.write(json.dumps(json_obj, indent=4, ensure_ascii=False))


def param_entry(trading_day, offset, norm_type):
    request_file = 'request.json'
    params_file = 'params.json'
    root_data_path = '/dfs/user/666466/03_mobius/02_FactorData'
    template_path = '/dfs/user/666466/01_params/template/model'
    dest_model_path = '/dfs/user/666466/01_params'

    variety_list = ['IM']

    logger.info("begin to generate param")
    for variety in variety_list:
        logger.info("offset={}, variety={}", offset, variety)
        dest = os.path.join(dest_model_path, trading_day, 'offset_' + offset, 'model', variety)
        logger.info("param will write to {}", dest)
        gen_request_json(dest, os.path.join(template_path, request_file), trading_day, root_data_path, offset)
        gen_params_json(dest, os.path.join(template_path, params_file), variety, trading_day, root_data_path, offset, norm_type)
        if os.path.exists(os.path.join(dest, request_file)) and os.path.exists(os.path.join(dest, params_file)):
            logger.info("norm模型参数生成成功，variety={}, offset={}, date={}", variety, offset, trading_day)
        else:
            logger.error("norm模型参数生成失败，variety={}, offset={}, date={}", variety, offset, trading_day)


def run_model(today, offset):
    logger.info("generate model params")
    param_entry(today, offset, 'norm2')
    logger.info("start java app for model")
    variety_list = ['IM']
    norm2_pass = True
    for variety in variety_list:
        cmd_str = 'sh start_model.sh {} {} {}'.format(today, offset, variety)
        os.system(cmd_str)
        logger.info("check log")
        if 0 == check_log_file('/dfs/user/666466/11_log/{}/offset_{}/model/MobiusModel_{}_{}_{}.log'.format(today, offset, variety, today, offset)):
            rank_index([today], variety, offset) 
        else:
            norm2_pass = False

    if norm2_pass:
        param_entry(today, offset, 'norm')
        for variety in variety_list:
            cmd_str = 'sh start_model.sh {} {} {}'.format(today, offset, variety)
            os.system(cmd_str)
            logger.info("check [rank_type=norm] log")
            if 0 == check_log_file('/dfs/user/666466/11_log/{}/offset_{}/model/MobiusModel_{}_{}_{}.log'.format(today, offset, variety, today, offset)):
                logger.info('[rank=norm] check log pass, {}, {}, {}', today, offset, variety)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        exit()

    offset = '0'
    today = sys.argv[1]

    s = FactorData()
    date_list = s.tradingday('20250421', -3)

    for day in date_list:
        logger.info("model will run, today={}, offset={}", today, offset)
        run_model(day, offset)
