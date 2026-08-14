import pandas as pd
from xquant.factordata import FactorData
fd = FactorData()

def getEXRightDividend():

    EXRightDividend = fd.get_factor_value(
        "WIND_AShareEXRightDividendRecord",
        factors=['BONUS_SHARE_RATIO', 'CONVERSED_RATIO', 'RIGHTSISSUE_RATIO', 'SEO_RATIO', 'RIGHTSISSUE_PRICE',
                 'SEO_PRICE', 'CASH_DIVIDEND_RATIO', 'EX_DATE', 'S_INFO_WINDCODE'],
        EX_DATE = ['>=20150101'],
    )

    EXRightDividend['shareRatio'] = EXRightDividend[['BONUS_SHARE_RATIO', 'CONVERSED_RATIO',
            'RIGHTSISSUE_RATIO', 'SEO_RATIO']].sum(axis=1)
    EXRightDividend['receiveRatio'] = pd.concat([EXRightDividend['RIGHTSISSUE_RATIO'] * EXRightDividend[
            'RIGHTSISSUE_PRICE'], EXRightDividend['SEO_RATIO'] * EXRightDividend['SEO_PRICE']], axis=1).sum(axis=1)
    EXRightDividend['payoutRatio'] = EXRightDividend['CASH_DIVIDEND_RATIO']
    EXRightDividend = EXRightDividend[['EX_DATE', 'S_INFO_WINDCODE', 'shareRatio', 'receiveRatio', 'payoutRatio']]
    EXRightDividend.columns = ['date', 'code', 'shareRatio', 'receiveRatio', 'payoutRatio']
    EXRightDividend['date'] = EXRightDividend['date'].map(int)
    EXRightDividend = EXRightDividend[EXRightDividend['code'].map(lambda x: x[0]).isin(['0','3','6'])]
    EXRightDividend['code'] = EXRightDividend['code'].map(lambda x: int(x[:6]))
    EXRightDividend = EXRightDividend.sort_values('date')
    return EXRightDividend

