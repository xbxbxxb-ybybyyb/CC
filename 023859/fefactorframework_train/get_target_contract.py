from xquant.futuredata import FutureData
fd = FutureData()
from xquant.factordata import FactorData
s = FactorData()

def get_target_contract_name(start_date=20220818, end_date=20220819):
    end_date_ = int(s.tradingday(end_date, 3)[-1])  # 按照当前算法，换仓日前一天需要触发哪个合约，换仓日后一天才知道，故仅做回测使用，实盘不行
    date_contract_dict = {}
    delivery_date = []
    tradingdays = s.tradingday(start_date, end_date_)
    for i in range(len(tradingdays)):
        date = tradingdays[i]
        available_contracts = fd.get_instrument_all('IM', date, date)
        last_contract = available_contracts[-1]
        date_contract_dict[date] = last_contract
        if i == 0:
            yesterday_last_contract = last_contract
            continue
        if last_contract != yesterday_last_contract:
            delivery_date.append(tradingdays[i - 1])
            date_contract_dict[tradingdays[i - 2]] = last_contract  # 交割日前一天也选择次月合约
            date_contract_dict[tradingdays[i - 1]] = last_contract  # 交割日选择次月合约

        yesterday_last_contract = last_contract

    return delivery_date, date_contract_dict

delivery_date, date_contract_dict = get_target_contract_name()