from loguru import logger

from xfactor import FactorUtil
from xfactor.runner.BasicDataManager import load_data_for_same_check


def get_use_data(py_code):
    def remove_space(code):
        while (len(code)>0 and code[0]==' '):
            code = code[1:]
        return code
    data_dic = {'/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5': 'MD',
                '/data/group/800463/data/generalStrong/minute5/': 'minute5',
                '/data/group/800463/data/generalStrong/ordersheet5_new/': 'ordersheet5_new',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5': 'AShareMoneyFlow',
                '/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5': 'RISK',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5': 'AShareEODDerivativeIndicator',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5':'AIndexEODPrices',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AIndexValuation/AIndexValuation.h5':'AIndexValuation',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5': 'AShareDescription',
                '/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5':'UNIV',
                '/data/group/800463/data/generalStrong/concept_h5_except_300/':'concept',
                '/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5': 'AShareEODDerivativeIndicator',
                '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareST/AShareST.h5': 'AShareST',
                '/data/group/800463/data/generalStrong/concept/': 'concept',
                # '/data/group/800080/warehouseJG/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5': 'INDEXWEIGHT_CHINA_STOCK_DAILY_CSI',
                '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSECU/DWD_EXP_FORECASTSECU.h5': 'SUNTIME',
                '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSCHEDULE/DWD_EXP_FORECASTSCHEDULE.h5': 'SUNTIME',
                '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSECUDERIVED/DWD_EXP_FORECASTSECUDERIVED.h5': 'SUNTIME',
                's.hsi': 'hsi'
    }
    data_use_list = []
    for i in range(len(py_code)):
        code = py_code[i]
        code = remove_space(code)
        if (len(code)==0) or (code[0] == '#'):
            continue

        if any(x in code for x in ['/data/group/', '/data/user/', '/dfs/group/', '/dfs/user/', 's.hsi']):
            use_data = code
            for key, value in data_dic.items():
                if key in code:
                    use_data = value
                    break
            data_use_list.append(use_data)
    return data_use_list

def get_h5_info_for_value_same_check(kls, start_date, end_date):
    t_1_factor_data = {}
    for data_dict in kls.t_1_factor_data:
        break_flag = True
        counter = 0
        start_date_new = ""
        while break_flag:
            if counter > 5:
                raise RuntimeError("tradingday接口调用失败超过5次！")

            try:
                start_date_new = FactorUtil.factor_data.tradingday(start_date, -int(data_dict["lag"]+1))[0]
                break_flag = False
            except Exception as e:
                logger.warning("tradingday接口调用失败！重试...")
                counter += 1
        t_1_factor_data[data_dict["name"]] = {
            "name": data_dict["name"],
            "lag": data_dict["lag"],
            "path": data_dict["path"],
            "column": data_dict["column"],
            "start_date": start_date_new,
            "end_date": end_date
        }

    return t_1_factor_data

def prepare_database_for_value_same_check(kls, stratgegy, start_date, end_date):
    t_1_factor_data = get_h5_info_for_value_same_check(kls, start_date, end_date)
    log_interval_task = {
        "strategy": stratgegy,
        "factor_class_list": [kls],
        "calc_start_date": start_date,
        "calc_end_date": end_date,
        "factor_type": FactorUtil.FactorType.T_1_FACTOR,
        "task_data_info": {
            "t_day_data_info": [],
            "xdb_data_info": {},
            "t_1_factor_data_info": t_1_factor_data,
            "other_t_day_data_info": {}
        }
    }
    db = load_data_for_same_check(log_interval_task)
    db["skip"] = False
    return db

def check_factor_sub_type(kls):
    if kls.strategy_name != "saturn/sell":
        return None
    if not kls.t_day_data:
        return "s"
    for item in kls.t_day_data:
        if "1m" in item:
            return "s1"
    return "s0"