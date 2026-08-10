import os
import sys
import pandas as pd
from multifactor.data.semaphore import ZooKeeper, Semaphore
import multifactor.utility.dt as tdt
import datetime as dt


if __name__ == '__main__':
    # determine whether to init update routine
    if pd.Timestamp(dt.date.today() + pd.Timedelta('1D')) != tdt.get_trading_day_offset(dt.date.today(), 1)[0]:
        sys.exit()
    zk_td = ZooKeeper(log_name='cronb td', log_file_name=os.path.join(private_log_path, 'cronb_trading_date.log'), auto_trading_date_flag=True)
    zk_cd = ZooKeeper(log_name='cronb cd', log_file_name=os.path.join(private_log_path, 'cronb_calendar_date.log'), auto_trading_date_flag=False)
    zk_ip = ZooKeeper(log_name='cronb ip', log_file_name=os.path.join(private_log_path, 'cronb_introspect.log'), auto_trading_date_flag=False,
                      base_flag_dir=flag_root_path)
    smp = Semaphore(flag_root_path)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    handlers = list()
    # minute aggregation
    zk_td.fire('minute aggregation', ['md', 'minute'], os.path.join(root, 'data', 'minute_aggregation.py'))
    smp.touch('minute', zk_td.date)
    # alpha indexes
    zk_td.fire('alpha indexes', ['univ'], os.path.join(root, 'data', 'alpha_index.py'))
    # barra risk
    zk_cd.fire('barra risk', ['fdd', 'rdf'], os.path.join(root, 'data', 'barra_risk.py'))
    # custom universe
    zk_td.fire('custom universe', [], os.path.join(root, 'data', 'custom_universe.py'))
    # custom base
    zk_td.fire('custom base', [], os.path.join(root, 'data', 'custom_md_base.py'))
    # custom market descriptors
    zk_td.fire('custom market descriptors', [], os.path.join(root, 'data', 'custom_md_descriptors.py'))
    # market factors
    handlers.append(zk_td.fire('market factors', [], os.path.join(root, 'factor', 'update_prod_md.py'), 'multiprocess'))
    # custom descriptors
    zk_cd.fire('custom descriptors', [], os.path.join(root, 'data', 'custom_descriptors.py'))
    # fundamental fix
    zk_cd.fire('fundamental fix', [], os.path.join(root, 'data', 'fundamental_fix.py'))
    # fundamental factors
    handlers.append(zk_cd.fire('fundamental factors', [], os.path.join(root, 'factor', 'update_prod_fdd.py'), 'multiprocess'))
    # force append check failed factors
    # zk_cd.fire('factors force append', [], os.path.join(root, 'snippet', 'update_helper.py'))
    # generate covariance matrix
    zk_td.fire('covariance matrix', [], os.path.join(root, 'data', 'risk_model_minute.py'))
    # suntime factors
    handlers.append(zk_td.fire('suntime factors', ['suntime'], os.path.join(root, 'factor', 'update_prod_cfc.py'), 'multiprocess'))
    # join unfinished processes
    [p.join() for p in handlers]
    # blacklist filters
    zk_cd.fire('blacklist filters', [], os.path.join(root, 'data', 'blacklist_filters.py'))
    # check generated factors
    status_check_str = little_tracker()
    if status_check_str == 'all fresh':
        zk_td.logger.info('*' * 30)
        zk_td.logger.info('factors all fresh')
        smp.touch('base', zk_td.date)  # may cross day, use script init date
    else:
        zk_td.logger.warning(status_check_str)
        smp.touch('base', zk_td.date, suffix='.failed')
        sys.exit()
    # init factor synthesize program
    # kingslanding
    zk_td.fire('vanilla turtle', ['index_weight'], os.path.join(root, 'strategy', 'vanilla_prod_turtle.py'))
    zk_td.fire('bolt kingslanding', [], os.path.join(root, 'strategy', 'bolt_prod_kingslanding.py'))
    zk_td.fire('vanilla kingslanding', [], os.path.join(root, 'strategy', 'vanilla_pilot_kingslanding.py'))
    # stormborn
    zk_td.fire('bolt stormborn', [], os.path.join(root, 'strategy', 'bolt_prod_stormborn.py'))
    zk_td.fire('vanilla stormborn', [], os.path.join(root, 'strategy', 'vanilla_pilot_stormborn.py'))
    # titan
    zk_td.fire('xgbolt titan', [], os.path.join(root, 'strategy', 'xgb_prod_titan.py'))
    zk_td.fire('vanilla titan', [], os.path.join(root, 'strategy', 'vanilla_pilot_titan.py'))
    # stacking
    zk_ip.fire('vanilla stacking', [], os.path.join(root, 'strategy', 'vanilla_pilot_stacking.py'))
    zk_td.fire('transfer portfolio', [], os.path.join(root, 'snippet', 'file_helper.py'))
    # derived macro factors
    zk_ip.fire('macro factors', [], os.path.join(root, 'data', 'macro_factors.py'))
    zk_ip.fire('derived macro factors', ['macro'], os.path.join(root, 'data', 'derived_macro_factors.py'))
    zk_td.logger.info('-------- all set --------')


