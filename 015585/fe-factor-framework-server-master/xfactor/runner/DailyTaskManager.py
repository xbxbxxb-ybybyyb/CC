import copy
import xfactor.FactorUtil as FactorUtil
from settings import RunMode

from loguru import logger


class DailyTaskManager(object):

    def __init__(self, factor_name_list, start_date, end_date, strategy):
        self.factor_class_list = FactorUtil.get_factor_class_list(factor_name_list)
        self.factor_data = FactorUtil.factor_data
        self.calc_date = start_date

        self.strategy = strategy

    # 生成task
    # 因子间并行
    def generate_task(self, mode):

        # 获取所有因子涉及的数据种类
        factor_type_groups = FactorUtil.split_calc_factor_into_group(self.strategy, self.factor_class_list)
        task_data_info_all = self.collect_task_data_info(factor_type_groups)

        task_dict = {}

        # generate prepare tasks:
        xdb_prepare_tasks = []
        h5_prepare_tasks = []
        t_day_prepare_tasks = []

        # prepare T-1 factor tasks
        for data_dict in task_data_info_all["t_1_factor_data_info"].values():
            cur_data = {
                "name": data_dict["name"],
                "path": data_dict["path"],
                "lag": data_dict["lag"],
                "column": list(data_dict["column"]),
                "start_date": self.factor_data.tradingday(self.calc_date, -int(data_dict["lag"]))[0],
                "end_date": self.calc_date,
            }
            h5_prepare_tasks.append({
                "strategy": self.strategy,
                "factor_class_list": [],
                "calc_start_date": "",
                "calc_end_date": "",
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {data_dict["name"]: cur_data},
                    "other_t_day_data_info": {}
                }
            })

        # prepare T Day data
        for data in task_data_info_all["t_day_data_info"]:
            t_day_prepare_tasks.append({
                "strategy": self.strategy,
                "factor_class_list": [],
                "calc_start_date": self.calc_date,
                "calc_end_date": self.calc_date,
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [data],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {},
                    "other_t_day_data_info": {}
                }
            })

        # prepare other T Day data
        for data_dict in task_data_info_all["other_t_day_data_info"]:
            cur_data = copy.deepcopy(data_dict)
            task = {
                "strategy": self.strategy,
                "factor_class_list": [],
                "calc_start_date": self.calc_date,
                "calc_end_date": self.calc_date,
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {},
                    "other_t_day_data_info": {cur_data["name"]: cur_data}
                }
            }
            t_day_prepare_tasks.append(task)

        for data_dict in task_data_info_all["xdb_data_info"]:
            cur_data = copy.deepcopy(data_dict)
            task = {
                "strategy": "",
                "factor_class_list": [],
                "calc_start_date": self.calc_date,
                "calc_end_date": self.calc_date,
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {cur_data["name"]: cur_data},
                    "t_1_factor_data_info": {},
                    "other_t_day_data_info": {}
                }
            }
            xdb_prepare_tasks.append(task)

        # prepare industry dataframe
        # if len(set(task_data_info_exclude_t_1['t_day_data_info']) & {'MarketIndTTick'}) > 0:
        industry_lag = 2
        if mode == RunMode.prod_prepare and len(xdb_prepare_tasks) > 0:
            # 盘前准备模式需要，xdb数据可能需要最多往前20天的
            industry_lag += 20
        if len(xdb_prepare_tasks) > 0 or 'MarketIndTTick' in task_data_info_all['t_day_data_info']:
            start_date_new = self.factor_data.tradingday(self.calc_date, -industry_lag)[0]
            cur_data = {
                "name": 'industry_tmp',
                "lag": 0,
                "path": '/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
                "column": ['Industry'],
                "start_date": start_date_new,
                "end_date": self.calc_date
            }
            cur_data2 = {
                "name": 'industry',
                "lag": 0,
                "path": '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                "column": ['amt'],
                "start_date": start_date_new,
                "end_date": self.calc_date
            }
            h5_prepare_tasks.append({
                "strategy": self.strategy,
                "factor_class_list": [],
                "calc_start_date": "",
                "calc_end_date": "",
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {'industry_tmp': cur_data},
                    "other_t_day_data_info": {}
                }
            })

            h5_prepare_tasks.append({
                "strategy": self.strategy,
                "factor_class_list": [],
                "calc_start_date": "",
                "calc_end_date": "",
                "factor_type": FactorUtil.FactorType.PREPARE,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {'industry': cur_data2},
                    "other_t_day_data_info": {}
                }
            })

        # generate calc tasks:
        calc_tasks = []

        for factor in factor_type_groups["pure_t_1_factor"]:
            t_1_factor_data = {}
            # 针对每个T-1 Factor表，都计算因子需求的起止时间
            for data_dict in factor.t_1_factor_data:
                break_flag = True
                counter = 0
                start_date = ''
                while break_flag:
                    if counter > 5:
                        raise RuntimeError("tradingday接口调用失败超过5次！")

                    try:
                        start_date = self.factor_data.tradingday(self.calc_date, -int(data_dict["lag"]))[0]
                        break_flag = False
                    except Exception as e:
                        logger.warning("tradingday接口调用失败！重试...")
                        counter += 1

                t_1_factor_data[data_dict["name"]] = {
                    "name": data_dict["name"],
                    "path": data_dict["path"],
                    "lag": data_dict["lag"],
                    "column": data_dict["column"],
                    "start_date": start_date,
                    "end_date": self.calc_date
                }

            task = {
                "strategy": self.strategy,
                "factor_class_list": [factor],
                "calc_start_date": self.calc_date,
                "calc_end_date": self.calc_date,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": t_1_factor_data,
                    "other_t_day_data_info": {}
                }
            }
            calc_tasks.append(task)

        for factor in factor_type_groups["t_day_factor"] + factor_type_groups["combined_t_1_factor"]:
            task = {
                "strategy": self.strategy,
                "factor_class_list": [factor],
                "calc_start_date": self.calc_date,
                "calc_end_date": self.calc_date,
                "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                "task_data_info": {
                    "t_day_data_info": factor.t_day_data,
                    "xdb_data_info": {},
                    "t_1_factor_data_info": {},
                    "other_t_day_data_info": {}
                }
            }

            if factor.xdb_data:
                xdb_info = {}
                for item in factor.xdb_data:
                    cur_item = copy.deepcopy(item)
                    break_flag = True
                    counter = 0
                    dates = []
                    while break_flag:
                        if counter > 5:
                            raise RuntimeError("tradingday接口调用失败超过5次！")

                        try:
                            dates = self.factor_data.tradingday(self.calc_date, -int(item["lag"] + 1))
                            break_flag = False
                        except Exception as e:
                            logger.warning("tradingday接口调用失败！重试...")
                            counter += 1

                    cur_item["dates"] = dates
                    xdb_info[cur_item["name"]] = cur_item
                task["task_data_info"]["xdb_data_info"] = xdb_info

            if factor.t_1_factor_data:
                t_1_factor_info = {}
                for item in factor.t_1_factor_data:
                    cur_item = copy.deepcopy(item)
                    break_flag = True
                    counter = 0
                    tmp_trading_days = []
                    while break_flag:
                        if counter > 5:
                            raise RuntimeError("tradingday接口调用失败超过5次！")

                        try:
                            tmp_trading_days = self.factor_data.tradingday(self.calc_date, -int(item["lag"]))  # 只计算当前因子的需求
                            break_flag = False
                        except Exception as e:
                            logger.warning("tradingday接口调用失败！重试...")
                            counter += 1

                    cur_item["start_date"] = tmp_trading_days[0]
                    cur_item["end_date"] = tmp_trading_days[-2]
                    t_1_factor_info[cur_item["name"]] = cur_item
                task["task_data_info"]["t_1_factor_data_info"] = t_1_factor_info

            if factor.other_t_day_data:
                other_t_day_data_info = {}
                for item in factor.other_t_day_data:
                    cur_item = copy.copy(item)

                    other_t_day_data_info[cur_item["name"]] = cur_item

                task["task_data_info"]["other_t_day_data_info"] = other_t_day_data_info

            calc_tasks.append(task)

        task_dict["xdb_prepare_tasks"] = xdb_prepare_tasks
        task_dict["h5_prepare_tasks"] = h5_prepare_tasks
        task_dict["t_day_prepare_tasks"] = t_day_prepare_tasks
        task_dict["calc_tasks"] = calc_tasks
        return task_dict

    def collect_task_data_info(self, factor_type_groups):

        day_data_set = set()
        t_1_factor_data_dict = {}
        xdb_data_dict = {}
        other_day_data_dict = {}

        factor_class_list_t_1 = factor_type_groups["pure_t_1_factor"]
        factor_class_list_others = factor_type_groups["t_day_factor"] + factor_type_groups["combined_t_1_factor"]

        # get data info for factors except pure t-1 factor
        for factor in factor_class_list_others:
            if len(factor.t_day_data) > 0:
                day_data_set = day_data_set.union(set(factor.t_day_data))

            for data_dict in factor.xdb_data:
                data_name = data_dict["name"]
                if data_name in xdb_data_dict:
                    xdb_data_dict[data_name]['lag'] = max(xdb_data_dict[data_name]['lag'], data_dict["lag"])
                else:
                    xdb_data_dict[data_name] = {}
                    xdb_data_dict[data_name]['name'] = data_name
                    xdb_data_dict[data_name]['lag'] = data_dict["lag"]

            for data_dict in factor.t_1_factor_data:
                data_name = data_dict["name"]
                if data_name in t_1_factor_data_dict:
                    t_1_factor_data_dict[data_name]["lag"] = max(t_1_factor_data_dict[data_name]["lag"],
                                                                 data_dict["lag"])
                    t_1_factor_data_dict[data_name]['column'] = t_1_factor_data_dict[data_name][
                        'column'].union(set(data_dict['column']))
                else:
                    t_1_factor_data_dict[data_name] = {}
                    t_1_factor_data_dict[data_name]["name"] = data_name
                    t_1_factor_data_dict[data_name]['path'] = data_dict["path"]
                    t_1_factor_data_dict[data_name]["lag"] = data_dict["lag"]
                    t_1_factor_data_dict[data_name]["column"] = set(data_dict["column"])

            for data_dict in factor.other_t_day_data:
                data_name = data_dict["name"]

                if data_name not in other_day_data_dict:
                    other_day_data_dict[data_name] = {}
                    other_day_data_dict[data_name]['name'] = data_name
                    other_day_data_dict[data_name]['path'] = data_dict["path"]

        # tmp_result = {
        #     "t_day_data_info": list(day_data_set),
        #     "xdb_data_info": xdb_data_dict,
        #     "t_1_factor_data_info": t_1_factor_data_dict,
        #     "other_t_day_data_info": other_day_data_dict
        # }
        # other_result = copy.deepcopy(tmp_result)

        # get data info for pure t-1 factor
        for factor in factor_class_list_t_1:
            if len(factor.t_day_data) > 0:
                day_data_set = day_data_set.union(set(factor.t_day_data))

            for data_dict in factor.xdb_data:
                data_name = data_dict["name"]
                if data_name in xdb_data_dict:
                    xdb_data_dict[data_name]['lag'] = max(xdb_data_dict[data_name]['lag'], data_dict["lag"])
                else:
                    xdb_data_dict[data_name] = {}
                    xdb_data_dict[data_name]['name'] = data_name
                    xdb_data_dict[data_name]['lag'] = data_dict["lag"]

            for data_dict in factor.t_1_factor_data:
                data_name = data_dict["name"]
                if data_name in t_1_factor_data_dict:
                    t_1_factor_data_dict[data_name]["lag"] = max(t_1_factor_data_dict[data_name]["lag"],
                                                                 data_dict["lag"])
                    t_1_factor_data_dict[data_name]['column'] = t_1_factor_data_dict[data_name][
                        'column'].union(set(data_dict['column']))
                else:
                    t_1_factor_data_dict[data_name] = {}
                    t_1_factor_data_dict[data_name]["name"] = data_name
                    t_1_factor_data_dict[data_name]['path'] = data_dict["path"]
                    t_1_factor_data_dict[data_name]["lag"] = data_dict["lag"]
                    t_1_factor_data_dict[data_name]["column"] = set(data_dict["column"])

            for data_dict in factor.other_t_day_data:
                data_name = data_dict["name"]

                if data_name not in other_day_data_dict:
                    other_day_data_dict[data_name] = {}
                    other_day_data_dict[data_name]['name'] = data_name
                    other_day_data_dict[data_name]['path'] = data_dict["path"]


        all_result = {
            "t_day_data_info": list(day_data_set),
            "xdb_data_info": xdb_data_dict,
            "t_1_factor_data_info": t_1_factor_data_dict,
            "other_t_day_data_info": other_day_data_dict
        }

        return all_result

    def get_factor_class_list(self):
        return self.factor_class_list
