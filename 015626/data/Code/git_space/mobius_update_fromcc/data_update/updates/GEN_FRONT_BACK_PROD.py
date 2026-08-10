import os
from datetime import datetime
from loguru import logger
from generator import Generator
from common.tools import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt

'''
使用该脚本将值testcase_base_path文件夹路径下生成如下形式的参数
└── 20240424# 目标交易日日期
    ├── params.json# 策略前端参数(供客户端使用), 即: 第一层参数
    ├── settings.json# 策略一体化框架参数(后端参数), 即: 第二层参数
    └── config.json# 策略自身参数(后端参数), 即:第三层参数
'''

def prepare_next_trading_day():
    # 填写当前日期, 参数生成为下一个交易日
    # cur_date = datetime.now().strftime("%Y%m%d")
    _, cur_date, _ = check_update_date()
    cur_date = str(cur_date)
    target_date = get_next_trading_day(cur_date)
    #target_date = '20240615'
    # 参数文件生成的目标路径, 需要改路径的写入权限
    # testcase_base_path = os.getcwd()
    testcase_base_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/Mobius_para/prod/'

    # 填写前段参数的zone
    front_param_zone = '503304'

    # 后端参数config.json文件所在文件夹地址, 可不指定, 默认为: testcase_base_path 的路径加上日期(target_date)文件夹
    backend_params_dirpath = "/home/appadmin/cppParam/MobiusCrossSectionCalculator"

    # 填写铃客通知的员工工号
    user_ids = ['016700']

    generator = Generator(user_ids)
    logger.info("Begin preparing parameters, trading_date={}", target_date)
    generator.write_params_file(mode='prod', base_path=testcase_base_path, gen_trading_day=target_date, backend_params_dirpath=backend_params_dirpath, zone=front_param_zone, zone_ids=[front_param_zone])
    logger.info("Finish preparing parameters done, trading_date={}", target_date)

    # 1.1上传后台参数文件
    from xquant.investment.strategyfile import upload_gccstrategy_file, upload_strategy_file
    upload_gccstrategy_file(strategy_id = "MobiusCrossSectionCalculator", strategy_date = str(target_date),  
                         upload_file_path=os.path.join(testcase_base_path, target_date),  is_stop=False, is_tradingsession=False)
                        
    # 1.2上传前端参数文件
    file_info = upload_strategy_file(strategy_id="MobiusCrossSectionCalculator", strategy_date= str(target_date), file_type=1,
                         upload_file_path = os.path.join(testcase_base_path, target_date, f'front_MobiusCrossSectionCalculator#{front_param_zone}.json'), is_delete=False, is_ready = 1)
    assert file_info == True
    
    
if __name__ == '__main__':
    prepare_next_trading_day()
