import os

from loguru import logger


class TimeEventHandler:
    def __init__(self, factor_save_path, time_table, log_info=print, log_error=print):
        self.__complete_flag = []
        self.__subscribed_factors = dict()

        self.__factor_save_path = factor_save_path
        self.__timetable = time_table
        self.__machine_num = 4
        self.__log_info = log_info
        self.__log_error = log_error

    def set_subscribed_factors(self, time_factor_dic):
        self.__subscribed_factors = time_factor_dic
        for key in self.__subscribed_factors:
            logger.info(f'订阅因子: 时间点={key}, 因子列表={str(self.__subscribed_factors[key])}')

    def process_factors_time_event(self):
        flag_file_list = os.listdir(os.path.join(self.__factor_save_path, 'flag'))

        for time_spot in self.__timetable:
            ready_factors_flag = "factors_ready_" + time_spot
            if ready_factors_flag in self.__complete_flag:
                continue

            complete_count = 0
            for file_name in flag_file_list:
                if ready_factors_flag in file_name:
                    complete_count += 1

            # 因子全部计算完成
            if complete_count == self.__machine_num:
                self.__complete_flag.append(ready_factors_flag)
                factor_path = os.path.join(self.__factor_save_path, time_spot)
                logger.info(f'因子全部计算完成, 即将触发模型预测！')
                return [time_spot, factor_path]
            # 订阅因子全部计算完成
            factor_flag_dir = os.path.join(self.__factor_save_path, 'flag', time_spot)
            complete_factor_class_list = os.listdir(factor_flag_dir)
            if self.__subscribed_factors and time_spot in self.__subscribed_factors:
                subscribed_factors = self.__subscribed_factors[time_spot]
                sub_count = 0
                for i in subscribed_factors:
                    if i in complete_factor_class_list:
                        sub_count += 1
                if sub_count == len(subscribed_factors):
                    self.__complete_flag.append(ready_factors_flag)
                    factor_path = os.path.join(self.__factor_save_path, time_spot)
                    logger.info(f'{sub_count}个订阅因子全部计算完成, 即将触发模型预测！')
                    return [time_spot, factor_path]
        return None
