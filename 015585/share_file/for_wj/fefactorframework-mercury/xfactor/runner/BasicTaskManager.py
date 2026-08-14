from abc import abstractmethod
import pandas as pd
import os
import copy
import settings
import xfactor.FactorUtil as FactorUtil
from xfactor.factor_precheck.precheck import format_check
from h5data.IO import IO
from loguru import logger


class BasicTaskManager(object):

    def __init__(self, factor_name_list, start_date, end_date, strategy):
        self.factor_class_list = FactorUtil.get_factor_class_list(factor_name_list)
        self.factor_data = FactorUtil.factor_data
        self.strategy = strategy
        basic = IO.read_data([start_date, end_date], alt=settings.path_dict[strategy]["Basic"])
        self.calc_days = list(
            map(lambda x: x.strftime('%Y%m%d'), basic.index.get_level_values(0).drop_duplicates()))
        self.start_date = self.calc_days[0]
        self.end_date = self.calc_days[-1]

    # 生成task
    # T日/T-1日因子，按照日期拆分数据，日期间并行
    def generate_task(self):
        factor_type_groups = FactorUtil.split_calc_factor_into_group(self.strategy, self.factor_class_list)
        task_data_info_exclude_t_1, task_data_info_all = self.collect_task_data_info(factor_type_groups)

        task_dict = {}
        strategies = self.strategy.split("/")

        # generate prepare tasks:
        data_prepare_tasks = []

        for data_dict in task_data_info_all["t_1_factor_data_info"].values():
            cur_data = {
                "name": data_dict["name"],
                "path": data_dict["path"],
                "lag": data_dict["lag"],
                "column": list(data_dict["column"]),
                "start_date": self.factor_data.tradingday(self.start_date, -int(data_dict["lag"]))[0],
                "end_date": self.end_date,
            }
            data_prepare_tasks.append({
                "strategy": "",
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

        if 'MarketIndTTick' in task_data_info_all['t_day_data_info']:
            max_xdb_lag = FactorUtil.get_max_xdb_lag(self.factor_class_list)
            max_xdb_lag = 0 if max_xdb_lag == -1 else max_xdb_lag
            start_date_new = self.factor_data.tradingday(self.start_date, -int(max_xdb_lag + 2))[0]
            cur_data = {
                "name": 'industry_tmp',
                "lag": 0,
                "path": '/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
                "column": ['Industry'],
                "start_date": start_date_new,
                "end_date": self.end_date
            }
            cur_data2 = {
                "name": 'industry',
                "lag": 0,
                "path": '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                "column": ['amt'],
                "start_date": start_date_new,
                "end_date": self.end_date
            }
            data_prepare_tasks.append({
                "strategy": "",
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

            data_prepare_tasks.append({
                "strategy": "",
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

        # if task_data_info_all["xdb_data_info"]:
        #     cur_data2 = {
        #         "name": 'valid_dates',
        #         "path": settings.xdb_valid_dates_path,
        #     }
        #     data_prepare_tasks.append({
        #         "strategy": "",
        #         "factor_class_list": [],
        #         "calc_start_date": "",
        #         "calc_end_date": "",
        #         "factor_type": FactorUtil.FactorType.PREPARE,
        #         "task_data_info": {
        #             "t_day_data_info": [],
        #             "xdb_data_info": {},
        #             "t_1_factor_data_info": {},
        #             "other_t_day_data_info": {'valid_dates': cur_data2}
        #         }
        #     })
        # generate calc tasks:
        calc_tasks = []

        for factor in factor_type_groups["pure_t_1_factor"]:
            t_1_factor_data = {}
            for data_dict in factor.t_1_factor_data:
                start_date = self.factor_data.tradingday(self.start_date, -int(data_dict["lag"]))[0]
                t_1_factor_data[data_dict["name"]] = {
                    "name": data_dict["name"],
                    "path": data_dict["path"],
                    "lag": data_dict["lag"],
                    "column": data_dict["column"],
                    "start_date": start_date,
                    "end_date": self.end_date
                }

            task = {
                "strategy": "",
                "factor_class_list": [factor],
                "calc_start_date": self.start_date,
                "calc_end_date": self.end_date,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "task_data_info": {
                    "t_day_data_info": [],
                    "xdb_data_info": {},
                    "t_1_factor_data_info": t_1_factor_data,
                    "other_t_day_data_info": {}
                }
            }
            for i in strategies:
                dup_task = copy.deepcopy(task)
                dup_task["strategy"] = i
                calc_tasks.append(dup_task)


        if factor_type_groups["t_day_factor"] or factor_type_groups["combined_t_1_factor"]:
            for date in self.calc_days:
                task = {
                    "strategy": "",
                    "factor_class_list": factor_type_groups["t_day_factor"] + factor_type_groups["combined_t_1_factor"],
                    "calc_start_date": date,
                    "calc_end_date": date,
                    "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                    "task_data_info": {
                        "t_day_data_info": task_data_info_exclude_t_1["t_day_data_info"],
                        "xdb_data_info": {},
                        "t_1_factor_data_info": {},
                        "other_t_day_data_info": task_data_info_exclude_t_1["other_t_day_data_info"]
                    }
                }

                if task_data_info_exclude_t_1["xdb_data_info"]:
                    xdb_info = copy.deepcopy(task_data_info_exclude_t_1["xdb_data_info"])
                    for data_dict in xdb_info.values():
                        dates = self.factor_data.tradingday(date, -int(data_dict["lag"] + 1))
                        data_dict["dates"] = dates
                    task["task_data_info"]["xdb_data_info"] = xdb_info

                if task_data_info_exclude_t_1["t_1_factor_data_info"]:
                    t_1_factor_info = copy.deepcopy(task_data_info_exclude_t_1["t_1_factor_data_info"])
                    for data_dict in t_1_factor_info.values():
                        tmp_trading_days = self.factor_data.tradingday(date, -int(data_dict["lag"]))
                        data_dict["start_date"] = tmp_trading_days[0]
                        data_dict["end_date"] = tmp_trading_days[-2] # 从计算当日往前取lag天，踢出计算当日
                    task["task_data_info"]["t_1_factor_data_info"] = t_1_factor_info

                for i in strategies:
                    dup_task = copy.deepcopy(task)
                    dup_task["strategy"] = i
                    calc_tasks.append(dup_task)

        task_dict["data_prepare_tasks"] = data_prepare_tasks
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


        tmp_result = {
            "t_day_data_info": list(day_data_set),
            "xdb_data_info": xdb_data_dict,
            "t_1_factor_data_info": t_1_factor_data_dict,
            "other_t_day_data_info": other_day_data_dict
        }
        other_result = copy.deepcopy(tmp_result)

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

        return other_result, all_result

    def get_factor_class_list(self):
        return self.factor_class_list
