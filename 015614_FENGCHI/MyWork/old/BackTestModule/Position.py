

class Position:
    """
    实现仓位记录的类
    记录某一时某个账户的持仓信息
    """
    def __init__(self, startup_cash : float):
        self.cash = startup_cash #账户资金
        self.holding = {}  #key:values对，key为股票代码，values为持仓数量
        self.free_cash = startup_cash
        self.frozen_cash = 0
        self.frozen_holding = {}
        self.tradable_holding = {}

    def Buy(self,stk_id,num,price):
        """
        调用Broker粗糙版的模拟交易所买入，更新仓位
        :param stk_id:
        :param num:
        :param date:
        :param price:
        :param broker:
        :return:
        """
        vol = num
        if stk_id in self.holding:
            self.holding[stk_id] += vol
        else:
            self.holding[stk_id] = vol
        if stk_id in self.frozen_holding:
            self.frozen_holding[stk_id] += vol
        else:
            self.frozen_holding[stk_id] = vol
        self.cash -= price*vol

    def Sell(self,stk_id,num,price):
        """
        调用Broker粗糙版的模拟交易所卖出，更新仓位
        :param stk_id:
        :param num:
        :param date:
        :param price:
        :param broker:
        :return:
        """
        if stk_id not in self.holding:
            raise('No holding position of selling stock %d'%stk_id)
        if stk_id not in self.tradable_holding:
            raise ('No tradable position of selling stock %d'%stk_id)
        elif self.tradable_holding[stk_id]<num:
            raise('Not enough position of stock %d for selling'%stk_id)

        # price, vol = broker.Sell(stk_id, price, num, date_time)
        self.holding[stk_id] -= num
        self.tradable_holding[stk_id] -= num
        self.cash += price * num
        if self.holding[stk_id]==0:
            self.holding.pop(stk_id)
    def new_day(self):
        for stk in self.holding:
            self.tradable_holding[stk] = self.holding[stk]
        self.frozen_holding = {}
        pass

    def Close_All_Position(self):
        """
        清仓
        :param broker:
        :return:
        """
        pass
    def deal_with_dividend(self,dividend_info):
        for stk_id in dividend_info.index:
            if stk_id not in self.holding:
                raise Exception('Stock %s is not in holding'%(str(stk_id)))
            holding = self.holding[stk_id]
            cash_change = (holding * dividend_info.loc[stk_id, 'payoutRatio'] * 0.9 - \
                           holding * dividend_info.loc[stk_id, 'receiveRatio'])
            holding_change = holding * dividend_info.loc[stk_id, 'shareRatio']
            self.holding[stk_id] +=holding_change
            self.cash += cash_change