import sys
sys.path.insert(4,'/cross_section_new/')
from cross_section_new import *
import os
from datetime import datetime
from loguru import logger
from generator_new import Generator
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
#    target_date = '20250623'
    # 参数文件生成的目标路径, 需要改路径的写入权限
    # testcase_base_path = os.getcwd()
    testcase_base_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/Mobius_para/prod_sh/'

    # 填写前段参数的zone
    front_param_zone_list = ['503106']#['503106','503107']
    zone_amicontext_map = {'503106':'mobius_cross_section_calculator_context',
                           '503107':'mobius_cross_section_calculator_context_10'}

    # 后端参数config.json文件所在文件夹地址, 可不指定, 默认为: testcase_base_path 的路径加上日期(target_date)文件夹
    backend_params_dirpath = "/home/appadmin/cppParam/MobiusCrossSectionCalculator"

    # 填写铃客通知的员工工号
    user_ids = ['016700']

    for front_param_zone in front_param_zone_list:
        ami_context = zone_amicontext_map[front_param_zone]
        generator = Generator(user_ids)
        logger.info("Begin preparing parameters, trading_date={}", target_date)
        generator.write_params_file(mode='prod', base_path=testcase_base_path, gen_trading_day=target_date, backend_params_dirpath=os.path.join(backend_params_dirpath, front_param_zone), zone=front_param_zone, zone_ids=front_param_zone_list, ami_context=ami_context)
        logger.info("Finish preparing parameters done, trading_date={}", target_date)

    # 1.1上传后台参数文件
    from xquant.investment.strategyfile import upload_gccstrategy_file, upload_strategy_file
    upload_gccstrategy_file(strategy_id = "MobiusCrossSectionCalculator", strategy_date = str(target_date),
                         upload_file_path=os.path.join(testcase_base_path, target_date),  is_stop=False, is_tradingsession=False)

    # 1.2上传前端参数文件
    for front_param_zone in front_param_zone_list:
        file_info = upload_strategy_file(strategy_id="MobiusCrossSectionCalculator", strategy_date= str(target_date), file_type=1,
                         upload_file_path = os.path.join(testcase_base_path, target_date, front_param_zone, f'front_MobiusCrossSectionCalculator#{front_param_zone}.json'), is_delete=False, is_ready = 1)
        assert file_info == True
    
def check_cross_data():
    _, end_date, _ = check_update_date()
    pre_day = udt.get_trading_day_offset(str(end_date), -1)[0].strftime('%Y%m%d')
    next_day = udt.get_trading_day_offset(str(end_date), 1)[0].strftime('%Y%m%d')

    import json
    with open(f"/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData/{next_day}/{end_date}", "r") as  f:
        lines = f.readlines()
        obj = json.loads(lines[0])
    with open(f"/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData/{next_day}/{pre_day}", "r") as  f:
        lines = f.readlines()
        obj_pre = json.loads(lines[0])

    assert len(obj) == len(obj_pre)

    for i in range(len(obj)):
        assert len(obj[i]) == len(obj_pre[i]), i
        assert len(obj[i]['details']) == len(obj_pre[i]['details']), i
        for j in range(len(obj[i]['details'])):
            assert len(obj[i]['details'][j]) == len(obj_pre[i]['details'][j]), str(i) + ' ' + str(j)
    print('check done!')
    
if __name__ == '__main__':
    check_cross_data()
    prepare_next_trading_day()
