import datetime as dt
import multifactor.utility.dt as udt
from xquant.xqutils.helper import link
from overnight.factor_generator import prepare_history, executor_factor
from overnight.utility import update_stock_multitime_data, get_current_futures_contract
from overnight.prepare_hot_dummy import prepare_hot_dummy
from multifactor.data.utils import *
from overnight.naming_config import *

lm = link.LinkMessage()

if __name__ == '__main__':
    _, date, _ = check_update_date()
    print('start to update factor proof')
    lm.sendMessage('start to update factor proof')
    prepare_hot_dummy(date)
    executor_factor(date, mode = 'history')
    prod_csv = pd.read_csv(os.path.join(factor_path, f'{date}_1449', f'{date}_1449.csv'), index_col=0)['norm']
    proof_csv = pd.read_csv(os.path.join(hisfactor_path, f'{date}_1449', f'{date}_1449.csv'), index_col=0)['norm']
    csv = pd.concat([prod_csv, proof_csv], axis = 1)
    csv.columns = ['prod', 'proof']
    csv['abs_diff'] = abs(csv['prod'] - csv['proof'])
    wrong = csv[csv['abs_diff'] > 0.00001]
    if len(wrong) > 0:
        lm.sendMessage(str(wrong))
        print(wrong)
    if len(prod_csv) != len(proof_csv):
        lm.sendMessage('因子数量不匹配')
        print('因子数量不匹配')

    print(str(dt.datetime.now()) + '*** prepare history ***')
    lm.sendMessage(str(dt.datetime.now()) + " start to prepare history data" )
    update_stock_multitime_data()
    prepare_history()
    
    today = dt.datetime.now().strftime('%Y%m%d')
    next_trading_day = udt.get_trading_day_offset(today, 1)[0].strftime('%Y%m%d')
    ticker_list = []
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IC.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IF.CFE', trade_date=today, mode='season'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='recent'))
    ticker_list.append(get_current_futures_contract(prod_id='IH.CFE', trade_date=today, mode='season'))
    lm.sendMessage(str(ticker_list))
    lm.sendMessage(str(dt.datetime.now()) + " history data done!")