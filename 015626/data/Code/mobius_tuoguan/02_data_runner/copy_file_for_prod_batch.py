import os
from loguru import logger
from datetime import date
from xquant.factordata import FactorData
import shutil
import hashlib
from multiprocessing import Pool
import notice


def send_link_message(msg):
    lm = notice.LinkMessage()
    lm.sendMessage(msg)


def get_file_md5(filename):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(32768), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def check_constituent(today, next_day, index_symbol):
    s = FactorData() 
    today_hs300 = s.hset('INDEX', today, index_symbol, weightType=1)
    next_hs300 = s.hset('INDEX', next_day, index_symbol, weightType=1)

    hs300_stock = set(today_hs300['stock'].values)
    next_hs300_stock = set(next_hs300['stock'].values)

    diff = next_hs300_stock - hs300_stock 
    if len(diff) == 0:
        logger.info("stock constituent same, index={}, today={}, next_day={}", index_symbol, today, next_day)
        return True, hs300_stock, diff
    else:
        logger.info("stock constituent diff, index={}, today={}, next_day={}, diff={}", index_symbol, today, next_day, diff)
        return False, next_hs300_stock, diff


def copy_and_check(source, dest, stock):
    shutil.copy2(os.path.join(source, stock), os.path.join(dest, stock))
    source_md5 = get_file_md5(os.path.join(source, stock))
    dest_md5 = get_file_md5(os.path.join(dest, stock))
    if source_md5 != dest_md5:
        logger.error("md5 diff, source={}, dest={}", source_md5, dest_md5)


def copy_constituent(stock_list, source, dest):
    pool = Pool(processes=36)
    for stock in stock_list:
        pool.apply_async(copy_and_check, args=(source, dest, stock,))
    pool.close()
    pool.join()


def copy_2_check(source, dest):
    shutil.copy2(source, dest)
    source_md5 = get_file_md5(source)
    dest_md5 = get_file_md5(dest)
    if source_md5 != dest_md5:
        logger.error("md5 diff, source={}, dest={}", source, dest)


def copy_indicator(today, next_day, offset_list):
    index_list = ['000300.SH', '000905.SH', '000852.SH']
    for index_symbol in index_list:
        diff, stock_list, diff_list = check_constituent(today, next_day, index_symbol)
        if diff:
            for offset in offset_list:
                logger.info("stock constituent same, begin to copy stock files, today={}, offset={}", today, offset)
                source = os.path.join('/dfs/user/666466/03_mobius/02_FactorData', today, 'offset_' + offset, '01_Indicator')
                dest = os.path.join('/dfs/user/666466/06_prod_data/02_FactorData', today, 'offset_' + offset, '01_Indicator')
                if not os.path.exists(dest):
                    os.makedirs(dest, exist_ok=True)
                copy_constituent(stock_list, source, dest)
        else:
            s = FactorData()
            trading_list = s.tradingday(today, -21)
            for offset in offset_list:
                logger.info("stock constituent diff, begin to copy stock files, today={}, offset={}", today, offset)
                source = os.path.join('/dfs/user/666466/03_mobius/02_FactorData', today, 'offset_' + offset, '01_Indicator')
                dest = os.path.join('/dfs/user/666466/06_prod_data/02_FactorData', today, 'offset_' + offset, '01_Indicator')
                if not os.path.exists(dest):
                    os.makedirs(dest, exist_ok=True)
                copy_constituent(stock_list, source, dest)
                for i in range(len(trading_list) - 1):
                    day = trading_list[i]
                    logger.info("stock constituent diff, begin to copy stock files, day={}, offset={}", day, offset)
                    source = os.path.join('/dfs/user/666466/03_mobius/02_FactorData', day, 'offset_' + offset, '01_Indicator')
                    dest = os.path.join('/dfs/user/666466/06_prod_data/02_FactorData', day, 'offset_' + offset, '01_Indicator')
                    if not os.path.exists(dest):
                        os.makedirs(dest, exist_ok=True)
                    copy_constituent(diff_list, source, dest)
               
    # copy future and index
    for offset in offset_list:
        source = os.path.join('/dfs/user/666466/03_mobius/02_FactorData', today, 'offset_' + offset, '01_Indicator')
        dest = os.path.join('/dfs/user/666466/06_prod_data/02_FactorData', today, 'offset_' + offset, '01_Indicator')
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)

        files_list = ['FS_IH_1MIN', 'FS_IF_1MIN', 'FS_IC_1MIN', 'FS_IM_1MIN'] 

        for file_name in files_list:
            logger.info("copy future files, today={}, offset={}, file={}", today, offset, file_name)
            copy_2_check(os.path.join(source, file_name), os.path.join(dest, file_name))

        index_list.append('000016.SH')
        for symbol in index_list:
            logger.info("copy index files, today={}, offset={}, symbol={}", today, offset, symbol)
            copy_2_check(os.path.join(source, symbol), os.path.join(dest, symbol))


def copy_factor(today, offset_list):
    for offset in offset_list:
        logger.info("copy factor raw files, today={}, offset={}", today, offset)
        dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/02_Factor/raw'
        os.makedirs(dest, exist_ok=True)
        source = f'/dfs/user/666466/03_mobius/02_FactorData/{today}/offset_{offset}/02_Factor/raw/{today}'
        dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/02_Factor/raw/{today}'
        copy_2_check(source, dest)

        logger.info("copy factor norm files, today={}, offset={}", today, offset)
        dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/02_Factor/norm'
        os.makedirs(dest, exist_ok=True)
        source = f'/dfs/user/666466/03_mobius/02_FactorData/{today}/offset_{offset}/02_Factor/norm/{today}'
        dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/02_Factor/norm/{today}'
        copy_2_check(source, dest)


def copy_signal(today, next_day, signal_list, offset_list):
    for signal in signal_list:
        for offset in offset_list:
            logger.info("copy signal raw files, today={}, offset={}", today, offset)
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/03_signal/{signal}/raw'
            os.makedirs(dest, exist_ok=True)

            # copy norm
            source = f'/dfs/user/666466/03_mobius/02_FactorData/{today}/offset_{offset}/03_signal/{signal}/raw/{today}'
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{today}/offset_{offset}/03_signal/{signal}/raw/{today}'
            copy_2_check(source, dest)

            # copy norm2
            logger.info("copy signal norm2 files, today={}, offset={}", today, offset)
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{next_day}/offset_{offset}/03_signal/{signal}/history_files/signalNorm2Value'
            os.makedirs(dest, exist_ok=True)
            source = f'/dfs/user/666466/03_mobius/02_FactorData/{next_day}/offset_{offset}/03_signal/{signal}/history_files/signalNorm2Value/{today}'
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{next_day}/offset_{offset}/03_signal/{signal}/history_files/signalNorm2Value/{today}'
            copy_2_check(source, dest)


def copy_base(today):
    logger.info("copy index weight file, today={}", today)
    source = f"/dfs/group/900001/XDB/00_MarketData/03_IndexData/10_IndexWeight/{today}/inx_ixcsiwgtnd"
    dest = f"/dfs/user/666466/06_prod_data/00_MarketData/03_IndexData/10_IndexWeight/{today}/inx_ixcsiwgtnd"
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    copy_2_check(source, dest)

    logger.info("copy contract file, today={}", today)
    source = f"/dfs/group/900001/XDB/00_MarketData/02_FutureData/02_UHFData/03_CCFX/10_ContractInfo/{today}/contract_univ"
    dest = f"/dfs/user/666466/06_prod_data/00_MarketData/02_FutureData/02_UHFData/03_CCFX/10_ContractInfo/{today}/contract_univ"
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    copy_2_check(source, dest)

    logger.info("copy SZ daily data file, today={}", today)
    source = f"/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/00_SZ/08_DailyData/{today}/Stock_SZ_DailyData_{today}"
    dest = f"/dfs/user/666466/06_prod_data/00_MarketData/00_StockData/02_UHFData/00_SZ/08_DailyData/{today}/Stock_SZ_DailyData_{today}"
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    copy_2_check(source, dest)

    logger.info("copy SH daily data file, today={}", today)
    source = f"/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/01_SH/08_DailyData/{today}/Stock_SH_DailyData_{today}"
    dest = f"/dfs/user/666466/06_prod_data/00_MarketData/00_StockData/02_UHFData/01_SH/08_DailyData/{today}/Stock_SH_DailyData_{today}"
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    copy_2_check(source, dest)

    logger.info("copy wind ashare file, today={}", today)
    source = f"/dfs/group/900001/XDB/00_MarketData/00_StockData/03_FinancialData/00_WindData/00_AShareCapitalization/{today}/Stock_AShareCapitalization_{today}"
    dest = f"/dfs/user/666466/06_prod_data/00_MarketData/00_StockData/03_FinancialData/00_WindData/00_AShareCapitalization/{today}/Stock_AShareCapitalization_{today}"
    dest_dir = os.path.dirname(dest)
    os.makedirs(dest_dir, exist_ok=True)
    copy_2_check(source, dest)


def copy_entry(today, next_day):
    offset_list = ['0']
    # signals = ['20250328_im_im_v1unifac', '20250328_im_im_v1unifac_crn', '20240628_im_im_v1unifac','20250328_ic_ic_v7unifac', '20250328_ic_ic_v7unifac_crn','20250328_if_if_v7c', '20250328_if_if_v7_crn']

    signals = ['20250328_im_im_v1_crn_ew', '20250328_im_im_v1unifac_crn_trend', '20250328_ic_ic_v7_crn_ew', '20250328_ic_ic_v7unifac_crn_trend', '20250328_if_if_v7_crn_ew', '20250328_if_if_v7_crn_trend', '20250328_im_im_v1unifac', '20250328_im_im_v1unifac_crn', '20240628_im_im_v1unifac','20250328_ic_ic_v7unifac', '20250328_ic_ic_v7unifac_crn','20250328_if_if_v7c', '20250328_if_if_v7_crn']
    copy_list = []
    for offset in offset_list:
        if check_flag(today, offset):
            logger.info("{} all flag exist".format(today))
            total_flag = os.path.join(f'/dfs/user/666466/04_flags/{today}/offset_{offset}', today + '_total.success') 
            create_flag(total_flag)
            copy_list.append(offset)
        else:
            logger.info("{} all flag not exist, offset={}".format(today, offset))

    copy_indicator(today, next_day, copy_list)
    copy_factor(today, copy_list)
    copy_signal(today, next_day, signals, copy_list)
    copy_base(today)
    if len(copy_list) > 0:
        remove_old_data(today, '0')
    send_link_message('数据拷贝完成, date={}'.format(today))

def create_flag(source_file):
    with open(source_file, 'w') as flag_file:
        flag_file.write('')
    return None


def check_flag(day, offset):
    indicator_flag = f'/dfs/user/666466/04_flags/{day}/offset_{offset}/01_Indicator/pre_run.success'
    factor_flag =    f'/dfs/user/666466/04_flags/{day}/offset_{offset}/factor/PreMobiusFactor.success'
    model_flag_ic =  f'/dfs/user/666466/04_flags/{day}/offset_{offset}/model/IC/{day}.success'
    model_flag_if =  f'/dfs/user/666466/04_flags/{day}/offset_{offset}/model/IF/{day}.success'
    model_flag_im =  f'/dfs/user/666466/04_flags/{day}/offset_{offset}/model/IF/{day}.success'

    if os.path.exists(indicator_flag) and os.path.exists(factor_flag) and os.path.exists(model_flag_ic) and os.path.exists(model_flag_if) and os.path.exists(model_flag_im):
        return True
    else:
        return False


def remove_folder(source):
    if os.path.exists(source):
        shutil.rmtree(source)


def remove_old_data(today, offset):
    # return None
    factor_day_past = 65
    signal_day_past = 35
    indicator_day_past = 25
    s = FactorData()
    cdate_list = s.tradingday(today, -65)

    factor_begin = int(cdate_list[0])
    signal_begin = int(cdate_list[-35])
    indicator_begin = int(cdate_list[-25])

    root = '/dfs/user/666466/06_prod_data/02_FactorData'
    for root, dirs, files in os.walk(root):
        for d in dirs:
            if not d.isdigit():
                continue
            if int(d) < factor_begin:
                raw = os.path.join(root, d, 'offset_{}'.format(offset), '02_Factor', 'raw')
                logger.info("remove factor old data, {}", raw)
                remove_folder(raw)
                norm = os.path.join(root, d, 'offset_{}'.format(offset), '02_Factor', 'norm')
                logger.info("remove factor old data, {}", norm)
                remove_folder(norm)

            if int(d) < indicator_begin:
                raw = os.path.join(root, d, 'offset_{}'.format(offset), '01_Indicator')
                logger.info("remove indicator old data, {}", raw)
                remove_folder(raw)

            if int(d) < signal_begin:
                raw = os.path.join(root, d, 'offset_{}'.format(offset), '03_signal')
                logger.info("remove signal old data, {}", raw)
                remove_folder(raw)


def copy_entry_55(today, next_day):
    offset_list = ['55']
    signals = ['20241213_ic_ic_v7unifac', '20241213_ic_ic_v7unifac_crn', '20241213_if_if_v7c', '20241213_if_if_v7_crn', '20241213_im_im_v1unifac', '20241213_im_im_v1unifac_crn']

    copy_list = []
    for offset in offset_list:
        if check_flag(today, offset):
            logger.info("{} all flag exist".format(today))
            total_flag = os.path.join(f'/dfs/user/666466/04_flags/{today}/offset_{offset}', today + '_total.success') 
            create_flag(total_flag)
            copy_list.append(offset)
        else:
            logger.info("{} all flag not exist, offset={}".format(today, offset))

    copy_indicator(today, next_day, copy_list)
    copy_factor(today, copy_list)
    copy_signal(today, next_day, signals, copy_list)
    if len(copy_list) > 0:
        remove_old_data(today, '55')
    send_link_message('数据拷贝完成, date={}, offset=55'.format(today))


def copy_entry_50(today, next_day):
    offset_list = ['50']
    signals = ['20241213_ic_ic_v7unifac', '20241213_ic_ic_v7unifac_crn', '20241213_if_if_v7c', '20241213_if_if_v7_crn', '20241213_im_im_v1unifac', '20241213_im_im_v1unifac_crn']

    copy_list = []
    for offset in offset_list:
        if check_flag(today, offset):
            logger.info("{} all flag exist".format(today))
            total_flag = os.path.join(f'/dfs/user/666466/04_flags/{today}/offset_{offset}', today + '_total.success') 
            create_flag(total_flag)
            copy_list.append(offset)
        else:
            logger.info("{} all flag not exist, offset={}".format(today, offset))

    copy_indicator(today, next_day, copy_list)
    copy_factor(today, copy_list)
    copy_signal(today, next_day, signals, copy_list)
    if len(copy_list) > 0:
        remove_old_data(today, '50')
    send_link_message('数据拷贝完成, date={}, offset=50'.format(today))


if __name__ == '__main__':
    # copy_indicator('20250508', '20250509', ['0'])
    # s = FactorData()
    # cdate_list = s.tradingday(20250317, -31)
    # for today in cdate_list:
    #     copy_base(today) 
    #copy_entry('20250508', '20250509')
    s = FactorData()
    cdate_list = s.tradingday('20250516', -65)
    for day in cdate_list:
        copy_factor(day, ['50', '55'])

    #signals = ['20250328_im_im_v1_crn_ew', '20250328_im_im_v1unifac_crn_trend', '20250328_ic_ic_v7_crn_ew', '20250328_ic_ic_v7unifac_crn_trend', '20250328_if_if_v7_crn_ew', '20250328_if_if_v7_crn_trend', '20250328_im_im_v1unifac', '20250328_im_im_v1unifac_crn', '20240628_im_im_v1unifac','20250328_ic_ic_v7unifac', '20250328_ic_ic_v7unifac_crn', '20250328_if_if_v7c', '20250328_if_if_v7_crn']
    #signals = ['20241213_ic_ic_v7unifac', '20241213_ic_ic_v7unifac_crn', '20241213_if_if_v7c', '20241213_if_if_v7_crn', '20241213_im_im_v1unifac', '20241213_im_im_v1unifac_crn']
    #cdate_list = s.tradingday(20250519, -2)
    #i = 0
    #for day in cdate_list[:-1]:
    #    copy_signal(day, cdate_list[i + 1], signals, ['55'])
    #    i = i + 1


  
