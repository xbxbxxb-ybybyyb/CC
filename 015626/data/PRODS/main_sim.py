
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from xquant.investment.strategyfile import *
import os, json
from datetime import datetime
from loguru import logger
from generator import Generator
from common.tools import *
from xquant.xqutils.helper import link

def send_link(message):
    lm = link.LinkMessage()
    lm.sendMessage(str(message))
    del(lm)
    
def get_md_params_json_sim(save_path):

    md_params_dict = {
        "user": "USERATSQUANTUDPSIM05",
        "password": "ge.u_+EYcsW9qP",
        "udp_ip": "168.62.5.47",
        "udp_port": 18088,
        "udp_backup": [
            {
                "ip": "168.62.5.48",
                "port": 18088
            }
        ],
        "tcp_ip": "168.62.5.42",
        "tcp_port": 9662,
        "tcp_backup": [
            {
                "ip": "168.62.5.42",
                "port": 9662
            }
        ],
        "interface_ip": "100.69.9.58",
        "index_list": [
            "000016.SH",
            "000300.SH",
            "000905.SH",
            "000852.SH"
        ],
        "future_list": [
            "IH",
            "IF",
            "IC",
            "IM"
        ]
    }
    output_file = open(os.path.join(save_path, 'sim-mobius-udp-config-168.62.1.62.json'), 'w')
    json.dump(md_params_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()
    file_info = sim_upload_gccstrategy_file(strategy_id="Mobius_udp", strategy_date= str(next_date),
                                                 upload_file_path = save_path, is_tradingsession=False)
    assert file_info == True
    
def get_front_params(save_path):
    udp_front_dict = {'path':os.path.join('/home/appadmin/cppParam/Mobius_udp/','sim-mobius-udp-config-168.62.1.62.json')}
    output_file = open(os.path.join(save_path, f'sim_Mobius_udp{zone}.json'), 'w')
    json.dump(udp_front_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()
    
    file_info = sim_upload_strategy_file(strategy_id="Mobius_udp", strategy_date= str(next_date), file_type=1,
                                                 upload_file_path = os.path.join(save_path, f'sim_Mobius_udp{zone}.json'), is_delete=False, is_ready = 1)
    assert file_info == True
    
    udp_front_dict = {'path':os.path.join('/home/appadmin/cppParam/MobiusCrossSectionCalculator/', 'settings.json')}
    output_file = open(os.path.join(save_path, f'sim_Mobius_indicator{zone}.json'), 'w')
    json.dump(udp_front_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()
    
    file_info = sim_upload_strategy_file(strategy_id="MobiusCrossSectionCalculator", strategy_date= str(next_date), file_type=1,
                                                 upload_file_path = os.path.join(save_path, f'sim_Mobius_indicator{zone}.json'), is_delete=False, is_ready = 1)
    assert file_info == True
    
if __name__ == '__main__':
    zone = '#304301'
    testcase_base_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/Mobius_para/sim/'
    
    _, cur_date, _ = check_update_date()
    cur_date = str(cur_date)
    next_date = udt.get_trading_day_offset(str(cur_date),1)[0].strftime('%Y%m%d')
    target_date = get_next_trading_day(cur_date)
    # 填写铃客通知的员工工号
    user_ids = ['016700']
    generator = Generator(user_ids)
    logger.info("Begin preparing parameters, trading_date={}", target_date)
    generator.write_params_file(testcase_base_path, target_date)
    get_md_params_json_sim(os.path.join(testcase_base_path, target_date))
    get_front_params(os.path.join(testcase_base_path, target_date))
    logger.info("Finish preparing parameters done, trading_date={}", target_date)
    
    file_info = sim_upload_gccstrategy_file(strategy_id="MobiusCrossSectionCalculator", strategy_date= str(next_date),
                                                 upload_file_path = os.path.join(testcase_base_path, target_date),  is_tradingsession=False)
    assert file_info == True

    
    send_link('mobius sim para done!')

