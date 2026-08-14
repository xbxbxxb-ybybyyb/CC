from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
sys.path.append('/data/group/800442/800319')
from ConceptApi import ConceptApi

def Point_Score(factor_name, Sentiment_Score, Sentiment):
    if factor_name=='投机情绪':
        Sentiment_Score['涨停数量'] = (Sentiment['当日涨停数量'] >= 90) * 10 + \
                                  ((Sentiment['当日涨停数量'] >= 45) & (Sentiment['当日涨停数量'] < 90)) * 7.5 + \
                                  ((Sentiment['当日涨停数量'] >= 25) & (Sentiment['当日涨停数量'] < 45)) * 5 + \
                                  ((Sentiment['当日涨停数量'] >= 10) & (Sentiment['当日涨停数量'] < 25)) * 2.5 + \
                                  ((Sentiment['当日涨停数量'] < 10)) * 0

        Sentiment_Score['连板数量'] = (Sentiment['当日连板数量'] >= 35) * 10 + \
                              ((Sentiment['当日连板数量'] >= 18) & (Sentiment['当日连板数量'] < 35)) * 7.5 + \
                              ((Sentiment['当日连板数量'] >= 9) & (Sentiment['当日连板数量'] < 18)) * 5 + \
                              ((Sentiment['当日连板数量'] >= 2) & (Sentiment['当日连板数量'] < 9)) * 2.5 + \
                              ((Sentiment['当日连板数量'] < 2)) * 0

        Sentiment_Score['炸板率'] = (Sentiment['当日炸板率'] < 0.2) * 10 + \
                                  ((Sentiment['当日炸板率'] > 0.2) & (Sentiment['当日炸板率'] <= 0.3)) * 7.5 + \
                                  ((Sentiment['当日炸板率'] > 0.3) & (Sentiment['当日炸板率'] <= 0.4)) * 5 + \
                                  ((Sentiment['当日炸板率'] > 0.4) & (Sentiment['当日炸板率'] <=0.5)) * 2.5 + \
                                  ((Sentiment['当日炸板率'] >0.5)) * 0

        Sentiment_Score['连板高度'] = (Sentiment['当日连板高度'] >= 5) * 10 + \
                              ((Sentiment['当日连板高度'] >= 3) & (Sentiment['当日连板高度'] <= 4)) * 6 + \
                              (Sentiment['当日连板高度'] == 2) * 3 + ((Sentiment['当日连板高度'] < 2)) * 0

    elif factor_name=='板块情绪':
        #########1、龙头股情绪#############
        Sentiment_Score['龙头股情绪'] = Sentiment['龙头股封板数量']*2 +\
                                   Sentiment['龙头股上涨6%数量']*1+\
                                   Sentiment['龙头股上涨3%数量']*0.5+\
                                   Sentiment['龙头股下跌数量']*-0.5+\
                                   Sentiment['龙头股下跌-3%数量']*-1+\
                                   Sentiment['龙头股下跌-6%数量']*-2+ \
                                   Sentiment['龙头股跌停数量'] * -2.5

        range_score = Sentiment['昨日龙头股数量'].apply(lambda x: 6 if x <= 3 else 10)
        ######如果最高板的封板高度
        range_score[Sentiment['当日连板高度'].rolling(242).max()>=5]=10

        Sentiment_Score['龙头股情绪'] = range_score * (Sentiment_Score['龙头股情绪'] + Sentiment['昨日龙头股数量'] * 2) / (Sentiment['昨日龙头股数量'] * 4)
        Sentiment_Score['龙头股情绪']=Sentiment_Score['龙头股情绪'].apply(lambda x:0 if x<0 else x)
        #########2、强势股情绪#############
        Sentiment_Score['强势股情绪'] = Sentiment['强势股封板数量']*2 +\
                                   Sentiment['强势股上涨6%数量']*1+\
                                   Sentiment['强势股上涨3%数量']*0.5+\
                                   Sentiment['强势股下跌数量']*-0.5+\
                                   Sentiment['强势股下跌-3%数量']*-1+\
                                   Sentiment['强势股下跌-6%数量']*-2+ \
                                   Sentiment['强势股跌停数量'] * -2.5

        range_score = Sentiment['昨日强势股数量'].apply(lambda x: 6 if x <= 7 else 10)
        Sentiment_Score['强势股情绪'] = range_score * (Sentiment_Score['强势股情绪'] + Sentiment['昨日强势股数量'] * 2) / (Sentiment['昨日强势股数量'] * 4)

    elif factor_name=='投机氛围':
        Sentiment_Score['涨停股溢价'] = \
            (Sentiment['昨日涨停股涨跌幅'] >= 0.06) * 10 + \
            ((Sentiment['昨日涨停股涨跌幅'] >= 0.05) & (Sentiment['昨日涨停股涨跌幅'] < 0.06)) * 7.5 + \
            ((Sentiment['昨日涨停股涨跌幅'] >= 0.035) & (Sentiment['昨日涨停股涨跌幅'] < 0.05)) * 5 + \
            ((Sentiment['昨日涨停股涨跌幅'] >= 0.01) & (Sentiment['昨日涨停股涨跌幅'] < 0.035)) * 2.5 + \
            ((Sentiment['昨日涨停股涨跌幅'] < 0.01)) * 0

        Sentiment_Score['炸板股溢价'] = \
            (Sentiment['昨日炸板股涨跌幅'] >= 0.03) * 10 + \
            ((Sentiment['昨日炸板股涨跌幅'] >= 0.02) & (Sentiment['昨日炸板股涨跌幅'] < 0.03)) * 7.5 + \
            ((Sentiment['昨日炸板股涨跌幅'] >= 0.01) & (Sentiment['昨日炸板股涨跌幅'] < 0.02)) * 5 + \
            ((Sentiment['昨日炸板股涨跌幅'] >= -0.01) & (Sentiment['昨日炸板股涨跌幅'] < 0.01)) * 2.5 + \
            ((Sentiment['昨日炸板股涨跌幅'] < -0.01)) * 0

        Sentiment_Score['追高股溢价'] = \
            (Sentiment['昨日追高股涨跌幅'] >= 0.045) * 10 + \
            ((Sentiment['昨日追高股涨跌幅'] >= 0.03) & (Sentiment['昨日追高股涨跌幅'] < 0.045)) * 7.5 + \
            ((Sentiment['昨日追高股涨跌幅'] >= 0.015) & (Sentiment['昨日追高股涨跌幅'] < 0.03)) * 5 + \
            ((Sentiment['昨日追高股涨跌幅'] >= 0) & (Sentiment['昨日追高股涨跌幅'] < 0.015)) * 2.5 + \
            (Sentiment['昨日追高股涨跌幅'] < 0) * 0

        Sentiment_Score['抄底股溢价'] = \
            (Sentiment['昨日抄底股涨跌幅'] >= 0.045) * 10 + \
            ((Sentiment['昨日抄底股涨跌幅'] >= 0.03) & (Sentiment['昨日抄底股涨跌幅'] < 0.045)) * 7.5 + \
            ((Sentiment['昨日抄底股涨跌幅'] >= 0.015) & (Sentiment['昨日抄底股涨跌幅'] < 0.03)) * 5 + \
            ((Sentiment['昨日抄底股涨跌幅'] >= 0) & (Sentiment['昨日抄底股涨跌幅'] < 0.015)) * 2.5 + \
            (Sentiment['昨日抄底股涨跌幅'] < 0) * 0

    return Sentiment_Score

class Daily_Market_Sentiment(object):
    def __init__(self,start_date,end_date,code_list,read_path='/data/group/800442/800319/Daily_ConCept/RawData/BasicData/'):
        self.read_path=read_path
        date_list = get_date_range(start_date, end_date)
        self.start_date=date_list[0]
        self.end_date=date_list[-1]
        self.date_list = date_list
        date_list1=[str(x) for x in date_list]

        s = FactorData()
        ma = MarketData()

        turn = get_daily_1factor('close', date_list)[code_list]
        Limit_Price = get_daily_1factor('limit_max', date_list)[code_list]
        Lowest_Price = get_daily_1factor('limit_min', date_list)[code_list]
        pre_close = get_daily_1factor('pre_close', date_list)[code_list]
        open = get_daily_1factor('open', date_list)[code_list]
        high = get_daily_1factor('high', date_list)[code_list]
        low = get_daily_1factor('low', date_list)[code_list]
        close = get_daily_1factor('close', date_list)[code_list]
        amt = get_daily_1factor('amt', date_list)[code_list]


        Limit_stock = (Limit_Price == close)  # 每日涨停个股
        Open_Board_stock = (Limit_Price > close) & (Limit_Price == high)  # 炸板个股

        Active_Stock = ConceptApi.get_basic_values('Active_Stock', start_date=start_date, end_date=end_date,read_path=read_path)  # 每日活跃板块的活跃个股
        stock_pool = ConceptApi.get_basic_values('stock_pool', start_date=start_date, end_date=end_date,read_path=read_path).shift(1)  # 股票池
        #############获取强势股，龙头股##################
        All_Power_stock = ConceptApi.get_basic_values('Power_stock', start_date=start_date, end_date=end_date,read_path=read_path)  # 强势股
        Power_in_time = ConceptApi.get_basic_values('Power_in_time', start_date=start_date, end_date=end_date,read_path=read_path)  # 强势股入选池子入选了多久
        All_Power_stock = All_Power_stock & (Power_in_time <= 20)

        Dragon_Stock = ConceptApi.get_basic_values('Dragon_Stock', start_date=start_date, end_date=end_date,read_path=read_path)  # 龙头股

        # 强势个股为活跃板块中的强势个股,必须是非龙头股
        Power_stock = ((Active_Stock.rolling(5).max() == 1) & All_Power_stock) & ~Dragon_Stock.fillna(False)
        Power_stock = Power_stock  # 强势股

        Limit_High = ConceptApi.get_basic_values('Limit_High', start_date=start_date, end_date=end_date,read_path=read_path)  # 连板高度

        ###抄底追高板块：近5日换手率位于市场前30% & 没有触板,且上涨的个股中，上涨最多的30只个股 ；反之亦然
        NoLimit_Stock = (high<Limit_Price) & (turn.rolling(5).mean().rank(axis=1, ascending=False,pct=True) < 0.3)

        buy_higher = ((close / pre_close - 1)[NoLimit_Stock & (close/pre_close-1>0)].rank(axis=1, ascending=False) <= 30)
        buy_lower = ((close / pre_close - 1)[NoLimit_Stock & (close/pre_close-1<0)].rank(axis=1, ascending=False) <= 30)

        self.Limit_High=Limit_High
        self.All_Power_stock = All_Power_stock & stock_pool  # 全市场强势股
        self.Power_stock = Power_stock & stock_pool  # 板块强势股
        self.Dragon_Stock = Dragon_Stock & stock_pool  # 龙头股
        self.Active_Stock = Active_Stock  #市场活跃股
        self.Limit_Price=Limit_Price
        self.close = close
        self.open=open
        self.high = high
        self.low=low
        self.pre_close = pre_close
        self.amt=amt
        self.Lowest_Price=Lowest_Price

        self.stock_pool = stock_pool
        self.Limit_stock = (Limit_stock & stock_pool)
        self.Open_Board_stock = Open_Board_stock & stock_pool

        self.buy_higher = buy_higher & stock_pool
        self.buy_lower = buy_lower & stock_pool
    #########板块情绪#########
    def Cal_Concpet(self, sentiment):
        stock_pct = (self.close / self.pre_close - 1)    ##收盘涨跌幅
        ########1、龙头股############
        Dragon_Stock = self.Dragon_Stock.shift(1)
        code_list = set(stock_pct.columns).intersection(set(self.Limit_stock.columns)).intersection(Dragon_Stock.columns)
        sentiment['昨日龙头股数量'] = Dragon_Stock.sum(axis=1)

        sentiment['龙头股封板数量'] = self.Limit_stock[code_list][Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股上涨6%数量'] =((stock_pct[code_list] >= 0.06) & self.Open_Board_stock[code_list])[Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股上涨3%数量']=((stock_pct[code_list] >= 0.03) & (stock_pct[code_list] < 0.06))[Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股下跌数量'] = ((stock_pct[code_list] >= -0.03) & (stock_pct[code_list] < 0))[Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股下跌-3%数量'] =((stock_pct[code_list] >= -0.06) & (stock_pct[code_list] < -0.03))[Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股下跌-6%数量'] =((stock_pct[code_list] >= -0.09) & (stock_pct[code_list] < -0.06))[Dragon_Stock[code_list] == True].sum(axis=1)
        sentiment['龙头股跌停数量'] = (stock_pct[code_list] <= -0.09)[Dragon_Stock[code_list] == True].sum(axis=1)

        sentiment['龙头股平均涨幅'] = stock_pct[code_list][Dragon_Stock[code_list] == True].mean(axis=1)
        ########2、强势股############
        Power_stock = self.Power_stock.shift(1)
        code_list = set(stock_pct.columns).intersection(set(self.Limit_stock.columns)).intersection(Power_stock.columns)
        sentiment['昨日强势股数量'] = Power_stock.sum(axis=1)

        sentiment['强势股封板数量'] = self.Limit_stock[code_list][Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股上涨6%数量'] = ((stock_pct[code_list] >= 0.06) & self.Open_Board_stock[code_list])[
            Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股上涨3%数量'] = ((stock_pct[code_list] >= 0.03) & (stock_pct[code_list] < 0.06))[
            Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股下跌数量'] = ((stock_pct[code_list] >= -0.03) & (stock_pct[code_list] < 0))[
            Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股下跌-3%数量'] = ((stock_pct[code_list] >= -0.06) & (stock_pct[code_list] < -0.03))[
            Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股下跌-6%数量'] = ((stock_pct[code_list] >= -0.09) & (stock_pct[code_list] < -0.06))[
            Power_stock[code_list] == True].sum(axis=1)
        sentiment['强势股跌停数量'] = (stock_pct[code_list] <= -0.09)[Power_stock[code_list] == True].sum(axis=1)

        sentiment['强势股平均涨幅'] = stock_pct[code_list][Power_stock[code_list] == True].mean(axis=1)

        return sentiment
    #######市场投机氛围##########
    def Cal_Market(self, sentiment):
        stock_pct = (self.close / self.pre_close - 1)    ##收盘涨跌幅
        #####1、昨日涨停个股溢价率##########
        Limit_stock = self.Limit_stock.shift(1)

        sentiment['昨日涨停股数量'] = Limit_stock.sum(axis=1)
        sentiment['昨日涨停股涨跌幅'] = stock_pct[Limit_stock == True].mean(axis=1)
        ######2、昨日炸板个股溢价率##########
        Open_Board_stock = self.Open_Board_stock.shift(1)

        sentiment['昨日炸板股数量'] = Open_Board_stock.sum(axis=1)
        sentiment['昨日炸板股涨跌幅'] = stock_pct[Open_Board_stock == True].mean(axis=1)
        ######3、昨日追高板块溢价率##########
        buy_higher = self.buy_higher.shift(1)

        sentiment['昨日追高股数量'] = buy_higher.sum(axis=1)
        sentiment['昨日追高股涨跌幅'] = stock_pct[buy_higher == True].mean(axis=1)
        ########4、昨日抄底板块溢价率########
        buy_lower = self.buy_lower.shift(1)

        sentiment['昨日抄底股数量'] = buy_lower.sum(axis=1)
        sentiment['昨日抄底股涨跌幅'] = stock_pct[buy_lower == True].mean(axis=1)

        return sentiment
        #######投机情绪#######
    #######投机情绪#######
    def Cal_Speculation(self, sentiment):
        sentiment['当日涨停数量'] = self.Limit_stock.sum(axis=1)
        sentiment['当日连板数量'] = (self.Limit_stock.rolling(2).sum()==2).sum(axis=1)
        sentiment['当日炸板率'] = self.Open_Board_stock.sum(axis=1) / (self.Open_Board_stock.sum(axis=1) + self.Limit_stock.sum(axis=1))

        sentiment['当日连板高度'] = (self.Limit_High.rolling(3).max().shift(1)*self.Limit_stock+self.Limit_stock).max(axis=1)
        return sentiment
    ######计算市场情绪########
    def Cal_sentiment(self):
        ############获取具体指标结果###########
        sentiment = pd.DataFrame(index=self.close.index,columns=['指数涨跌幅'])
        ####1、板块情绪#####
        sentiment=self.Cal_Concpet(sentiment)
        ####2、投机情绪####
        sentiment = self.Cal_Speculation(sentiment)
        ####3、市场投机氛围#####
        sentiment = self.Cal_Market(sentiment)

        self.Sentiment = sentiment
        ############获取情绪得分##################
        Sentiment_Score = pd.DataFrame(index=self.Sentiment.index, columns=['情绪得分', '投机情绪得分', '龙头情绪得分', '投机氛围得分'])
        Sentiment_Score = Point_Score('投机情绪', Sentiment_Score, self.Sentiment)
        Sentiment_Score = Point_Score('板块情绪', Sentiment_Score, self.Sentiment)
        Sentiment_Score = Point_Score('投机氛围', Sentiment_Score, self.Sentiment)

        self.Sentiment_Score = Sentiment_Score
        #############计算权重#################
        Weight = pd.DataFrame(index=self.date_list,columns=['涨停数量','连板数量','炸板率','连板高度',
                                                            '龙头股情绪','强势股情绪',
                                                            '涨停股溢价','炸板股溢价','追高股溢价','抄底股溢价'])

        Weight['涨停数量'] =  Weight['连板数量'] =0.15
        Weight['炸板率'] = 0.05
        Weight['连板高度'] = 0.05

        Weight['龙头股情绪']=0.2
        Weight['强势股情绪']=0.1

        Weight['涨停股溢价']=Weight['炸板股溢价']=0.1
        #########无追高板块，追高板块权重为0
        Weight['追高股溢价'] = 0.1
        Weight['追高股溢价'][self.buy_higher.sum(axis=1) == 0] = 0
        Weight['抄底股溢价'] = 0
        Weight['抄底股溢价'][Weight['追高股溢价']==0]=0.1

        #########如果无龙头股，权重给强势股；如果无强势股，权重给龙头股；如果既没有龙头股也没有强势股，则该部分得分为0
        Weight['龙头股情绪'][sentiment['昨日龙头股数量'] == 0] = 0
        Weight['强势股情绪'][sentiment['昨日龙头股数量'] == 0] = 0.25

        Weight['强势股情绪'][sentiment['昨日强势股数量'] == 0] = 0
        Weight['龙头股情绪'][sentiment['昨日强势股数量'] == 0] = 0.25

        Weight['强势股情绪'][sentiment['昨日强势股数量'] == 0][sentiment['昨日龙头股数量'] == 0] = 0
        Weight['龙头股情绪'][sentiment['昨日强势股数量'] == 0][sentiment['昨日龙头股数量'] == 0] = 0

        Weight['炸板率'][sentiment['当日涨停数量'] == 0] = 0

        ######市场情绪得分统计##########
        Score = (Sentiment_Score * Weight)

        return Score.sum(axis=1)

class MarketDailySentiment(crossFactor):
    def st_factor(self):
        market_sentiment =  Daily_Market_Sentiment(self.cal_date_range[0], self.end, code_list=self.code_list)
        factor = market_sentiment.Cal_sentiment()
        stock_pct = np.array(factor)[:,np.newaxis].repeat(len(self.code_list),axis=1)

        return stock_pct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nanmean(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return arr_match_index(res,self.cal_date_range,self.date_range)

    def result(self):
        return arr_match_index(self.st_factor(), self.cal_date_range, self.date_range)

if __name__=='__main__':
    f = MarketDailySentiment(group=None, func=None,author='tx',extend_days=5,factor_name='MarketDailySentiment',
                         logic='市场情绪',freq='daily')
    f.save_result()

