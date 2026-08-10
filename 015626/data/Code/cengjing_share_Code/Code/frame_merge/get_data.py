import pandas as pd
from xquant.futuredata import FutureData



# 更新期货主力合约
def update_ZL_contract(variety, date, zl_id = None):
    path = '/data/user/015615/IndexFuture/data_center/ZL_contract.pickle'
    hist_ZL_contract = pd.read_pickle(path)
    
    if zl_id is None:
        fd = FutureData()
        new_ZL_contract = fd.get_change_date(variety, date, 'ZL00')[0]
    else:
        new_ZL_contract = zl_id
    
    new_ZL_contract_index = pd.MultiIndex.from_arrays([[variety], [date]], names = ('variety', 'date'))
    new_ZL_contract = pd.DataFrame(new_ZL_contract, index = new_ZL_contract_index, columns = ['ZL_contract'])
    
    if hist_ZL_contract.index.isin([(variety, date)]).any():
        hist_ZL_contract.drop((variety,date),inplace = True)
    hist_ZL_contract = hist_ZL_contract.append(new_ZL_contract)
    hist_ZL_contract = hist_ZL_contract.sort_index()

    hist_ZL_contract.to_pickle(path)


# 获取期货主力合约
def get_ZL_contract(variety, date):
    path = '/data/user/015615/IndexFuture/data_center/ZL_contract.pickle'
    hist_ZL_contract = pd.read_pickle(path)
    return hist_ZL_contract.loc[variety, date][0]


# 更新交易日
def update_trading_days(date):
    path = '/data/user/015615/IndexFuture/data_center/history_trading_days.pickle'
    hist_trading_days = pd.read_pickle(path)
    
    if date in hist_trading_days.index:
        hist_trading_days.drop(index = [date],inplace = True)
    hist_trading_days = hist_trading_days.append(pd.DataFrame(date, index = [date], columns = ['trading_days']))
    hist_trading_days = hist_trading_days.sort_index()
    
    hist_trading_days.to_pickle(path)


# 获取交易日
def get_trading_days(start_date, end_date):
    path = '/data/user/015615/IndexFuture/data_center/history_trading_days.pickle'
    hist_trading_days = pd.read_pickle(path)
    return hist_trading_days['trading_days'].loc[start_date:end_date].tolist()