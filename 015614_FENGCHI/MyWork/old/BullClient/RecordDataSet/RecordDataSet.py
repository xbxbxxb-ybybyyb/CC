# coding: utf-8
# Author：fengchi863
# Date ：2020/8/20 8:41

import pandas as pd

from BullClient.dataApi.stockList import trans_int2windcode


class RecordDataSet:
    def __init__(self):
        self.root_path = '/data/user/fengchi/BullClient/'
        self.raw_entrust_path = '/data/user/fengchi/BullClient/entrust_0817.csv'
        self.raw_deliver_path = '/data/user/fengchi/BullClient/deliver_0817.csv'
        self.raw_stock_path = '/data/user/fengchi/BullClient/stock_0817.csv'
        self.entrust_path = '/data/user/fengchi/BullClient/entrust.csv'
        self.deliver_path = '/data/user/fengchi/BullClient/deliver.csv'
        self.stock_path = '/data/user/fengchi/BullClient/stock.csv'
        self.clean_deliver_path = '/data/user/fengchi/BullClient/clean_deliver.csv'
        self.stock_code_and_name_dict = None

    def _read_raw_data(self, raw_data):
        if raw_data is 'entrust':
            return pd.read_csv(self.raw_entrust_path, index_col=0)
        elif raw_data is 'deliver':
            return pd.read_csv(self.raw_deliver_path, index_col=0)
        elif raw_data is 'stock':
            return pd.read_csv(self.raw_stock_path, index_col=0)
        else:
            raise (ValueError('%s data is not available!' % raw_data))

    def entrust_processing(self):
        data = self._read_raw_data('entrust')
        data = data[data['委托类别'] != '撤单']
        data = data.drop(['REPORT_NO'], axis=1)
        data = data.rename({'股票代码': '证券代码'}, axis=1)
        data.loc[data['证券代码'] == 43, '证券代码'] = 1914

        # 剔除非股票的代码
        def is_stock_code(code: int):
            if str(code).__len__() == 6 and code // 100000 <= 2:
                return False
            elif str(code).__len__() == 6 and code // 100000 == 5:
                return False
            else:
                return True

        data = data[data['证券代码'].apply(lambda x: is_stock_code(x))]

        # 获取股票名称
        stock_code_and_name = pd.read_excel('../other_data/stock_code_and_name.xlsx', encoding='gb18030')
        stock_code_and_name_dict = {}
        for idx, curr in stock_code_and_name.iterrows():
            stock_code = curr['证券代码']
            stock_name = curr['证券简称']
            stock_code_and_name_dict[stock_code] = stock_name

        self.stock_code_and_name_dict = stock_code_and_name_dict

        data['证券名称'] = data['证券代码'].apply(lambda x: stock_code_and_name_dict[trans_int2windcode(x)])
        columns = ['委托日期', '委托时间', '委托类别', '证券代码', '证券名称', '买卖方向', '委托状态', \
                   '委托数量', '委托价格', '撤单数量', '成交数量', '成交价格', '成交金额']
        data = data[columns]
        data = data.sort_values(['委托日期', '委托时间', '证券代码'])
        data = data.reset_index(drop=True)
        data.to_csv(self.entrust_path)

    def deliver_processing(self):
        data = self._read_raw_data('deliver')
        data.drop(['REPORT_NO', 'BUSINESS_NO'], axis=1, inplace=True)
        data.rename(columns={'INIT_DATE': '委托日期',
                             'REPORT_TIME': '委托时间',
                             'BUSINESS_TIME': '成交时间',
                             'BUSINESS_FLAG': '买卖方向',
                             'STOCK_CODE': '证券代码',
                             'STOCK_NAME': '证券名称',
                             'BUSINESS_AMOUNT': '成交数量',
                             'BUSINESS_PRICE': '成交价格',
                             'BUSINESS_BALANCE': '成交金额',
                             'POST_AMOUNT': '剩余股数',
                             'BUSINESS_TIMES': '成交次数',
                             }, inplace=True)
        data = data.drop(['成交次数'], axis=1)
        data.loc[data['成交数量'] > 0, '买卖方向'] = '买入'
        data.loc[data['成交数量'] < 0, '买卖方向'] = '卖出'
        data = data[(data['成交时间'] > 90000) & (data['成交时间'] < 160000)]

        # 剔除非股票的代码
        def is_stock_code(code: int):
            if str(code).__len__() == 6 and code // 100000 <= 2:
                return False
            elif str(code).__len__() == 6 and code // 100000 == 5:
                return False
            elif str(code).__len__() == 6 and code // 100000 == 7:
                return False
            else:
                return True

        data = data[data['证券代码'].apply(lambda x: is_stock_code(x))]
        data.loc[data['证券代码'] == 43, '证券代码'] = 1914

        # 按成交时间排列
        data = data.sort_values(['委托日期', '成交时间', '证券代码'])
        data = data.reset_index(drop=True)
        data.to_csv(self.deliver_path)

    def stock_processing(self):
        data = self._read_raw_data('stock')
        data = data.drop(['EXCHANGE_TYPE'], axis=1)
        data = data.rename(columns={'DC_BUSINESS_DATE': '持仓日期',
                                    'STOCK_CODE': '证券代码',
                                    'BEGIN_AMOUNT': '开盘持仓',
                                    'CURRENT_AMOUNT': '收盘持仓',
                                    'SUM_BUY_AMOUNT': '总买入股数',
                                    'SUM_BUY_BALANCE': '总买入金额',
                                    'SUM_SELL_AMOUNT': '总卖出股数',
                                    'SUM_SELL_BALANCE': '总卖出金额',
                                    })
        data.loc[data['证券代码'] == 43, '证券代码'] = 1914

        # 剔除非股票的代码
        def is_stock_code(code: int):
            if str(code).__len__() == 6 and code // 100000 <= 2:
                return False
            elif str(code).__len__() == 6 and code // 100000 > 6:
                return False
            elif str(code).__len__() == 6 and code // 100000 == 5:
                return False
            else:
                return True

        data = data[data['证券代码'].apply(lambda x: is_stock_code(x))]

        data['证券名称'] = data['证券代码'].apply(lambda x: self.stock_code_and_name_dict[trans_int2windcode(x)])

        data = data.sort_values(['持仓日期', '证券代码'])
        data = data.reset_index(drop=True)
        data.to_csv(self.stock_path)

    def clean_deliver_processing(self):
        deliver = pd.read_csv(self.deliver_path, index_col=0)
        buy_deliver = deliver[deliver['买卖方向'] == '买入']
        buy_deliver = buy_deliver.sort_values(['委托日期', '证券代码', '成交时间', '剩余股数'])
        sell_deliver = deliver[deliver['买卖方向'] == '卖出']
        sell_deliver = sell_deliver.sort_values(['委托日期', '证券代码', '成交时间', '剩余股数'], ascending=False)
        sell_deliver = sell_deliver.sort_values(['委托日期', '证券代码', '成交时间'])
        deliver = pd.concat([buy_deliver, sell_deliver], axis=0)
        deliver = deliver.sort_values(['委托日期', '证券代码', '成交时间'])
        deliver = deliver.reset_index(drop=True)
        # 对不是建仓交易之前的删除
        stock_set = set(deliver['证券代码'].tolist())
        flag_dict = dict(zip(list(stock_set), [False] * len(stock_set)))
        len_deliver = len(deliver)
        for idx in range(len_deliver):
            deal = deliver.loc[idx, :]
            if not flag_dict[deal['证券代码']]:
                if deal['成交数量'] != deal['剩余股数']:
                    deliver = deliver.drop(idx, axis=0)
                else:
                    flag_dict[deal['证券代码']] = True
            else:
                continue
        deliver = deliver.reset_index(drop=True)
        deliver.to_csv(self.clean_deliver_path)

    def get_entrust_data(self):
        return pd.read_csv(self.entrust_path, index_col=0)

    def get_deliver_data(self):
        return pd.read_csv(self.deliver_path, index_col=0)

    def get_stock_data(self):
        return pd.read_csv(self.stock_path, index_col=0)

    def get_clean_deliver_data(self):
        return pd.read_csv(self.clean_deliver_path, index_col=0)

if __name__ == '__main__':
    rds = RecordDataSet()
    # rds.entrust_processing()
    # rds.deliver_processing()
    # rds.stock_processing()
    rds.clean_deliver_processing()
    # entrust = rds.get_entrust_data()
    # deliver = rds.get_deliver_data()
    # stock = rds.get_stock_data()
