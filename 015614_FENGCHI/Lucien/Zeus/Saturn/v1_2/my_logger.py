# coding: utf-8
# Author：fengchi863
# Date ：2022/7/14 19:23
import sys
import os
import datetime
from loguru import logger


class MyLogger:
    def __init__(self, strategy_name=None, version=None, model_name=None, remarks=None):
        root_path = '/data/user/015614/Zeus/logs/'
        if remarks:
            log_path = f'{root_path}/{strategy_name}/{version}/{model_name}_{remarks}/'
        else:
            log_path = f'{root_path}/{strategy_name}/{version}/{model_name}/'
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file_path = os.path.join(log_path, f'{cur_time}.log')
        self.logger = logger
        # 清空所有设置
        self.logger.remove()
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        self.logger.add(log_file_path, level='DEBUG',
                        format='{time:YYYYMMDD HH:mm:ss} - '  # 时间
                               '{level} - {message}',  # 模块名.方法名:行号
                        rotation="10 MB")

        """
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(log_file_path, level='DEBUG',
                        format='{time:YYYYMMDD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               '{module}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        rotation="10 MB")
        """

    def get_logger(self):
        return self.logger

