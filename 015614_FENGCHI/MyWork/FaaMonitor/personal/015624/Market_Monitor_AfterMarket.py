import pandas as pd
import numpy as np
import cvxpy as cp
from tqdm import tqdm
from xquant.factordata import FactorData
from multiprocessing import Pool
import matplotlib.pyplot as plt
import time,datetime
import requests,json,datetime,time,sys,ConceptApi
from tqdm import tqdm
from xquant.thirdpartydata.marketdata import MarketData
from xquant.factordata import FactorData
sys.path.append('/data/group/800319')
from dataApi import getData,tradeDate,stockList
from realtimeApi.getdata_from_open import *

################市场情绪：日频数据############################
def send_file(users, file):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)

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
    def __init__(self,start_date,end_date,read_path='/data/group/800319/Temporary_Data/RawData/BasicData/'):
        self.read_path=read_path
        date_list = getData.get_date_range(start_date, end_date)
        self.start_date=date_list[0]
        self.end_date=date_list[-1]
        self.date_list = date_list
        date_list1=[str(x) for x in date_list]

        s = FactorData()
        ma = MarketData()
        turn = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1, factor_names=['turn']).iloc[:,0].unstack().dropna(how='all', axis=1).shift(1).astype(float)
        Limit_Price = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1,factor_names=['mdc_maxpx']).iloc[:, 0].unstack().dropna(how='all',axis=1)[turn.columns].astype(float)
        Lowest_Price = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1, factor_names=['mdc_minpx']).iloc[:, 0].unstack().dropna(how='all',axis=1)[turn.columns].astype(float)
        pre_close = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1, factor_names=['mdc_pre_close']).iloc[:, 0].unstack().dropna(how='all',axis=1)[turn.columns].astype(float)

        open = pd.DataFrame(index=date_list1,columns = pre_close.columns).astype(float)
        high = open.copy()
        low = open.copy()
        close = open.copy()
        amt = open.copy()
        for code in tqdm(open.columns):
            Result = ma.getMDSecurityKLineDataFrame(code, str(start_date) + '091500', str(end_date) + '150000', 10, 25).set_index('MDDate')
            open[code] = Result['OpenPx']
            high[code] = Result['HighPx']
            low[code] = Result['LowPx']
            close[code] = Result['ClosePx']
            amt[code] = Result['TotalValueTrade']

        pre_close.columns= open.columns =high.columns =low.columns =close.columns = amt.columns = Limit_Price.columns =Lowest_Price.columns = turn.columns\
            =pd.Series(pre_close.columns).apply(lambda x: stockList.trans_windcode2int(x))
        pre_close.index = open.index = high.index = low.index = close.index = amt.index = Limit_Price.index = Lowest_Price.index = turn.index \
            =[int(t) for t in pre_close.index]

        open = open.astype(float)
        high = high.astype(float)
        low = low.astype(float)
        close = close.astype(float)
        amt = amt.astype(float)

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

        self.Sentiment_Score['投机情绪得分']=Score[['涨停数量','连板数量','炸板率']].sum(axis=1)/0.35
        self.Sentiment_Score['龙头情绪得分']=Score[['龙头股情绪','连板高度']].sum(axis=1)/0.25
        self.Sentiment_Score['投机氛围得分']=Score[['强势股情绪','涨停股溢价','炸板股溢价','追高股溢价','抄底股溢价']].sum(axis=1)/0.4
        self.Sentiment_Score['情绪得分'] = Score.sum(axis=1)
    ####保存数据#######
    def save_Result(self,date_list,save_path='/data/user/015624/'):
        writer = pd.ExcelWriter(save_path + str(self.end_date)+'历史市场情绪分析.xlsx')
        round(self.Sentiment_Score.loc[date_list],2).to_excel(writer, sheet_name='日间情绪得分')
        round(self.Sentiment.loc[date_list],2).to_excel(writer, sheet_name='日间各部分情绪得分')
        writer.close()


end_date = int(datetime.datetime.now().strftime('%Y%m%d'))
date_list = getData.get_date_range(20130101, end_date)
start_date = date_list[-90]
end_date=date_list[-1]
end_date_before=date_list[-2]
begin = datetime.datetime.now()
self=Daily_Market_Sentiment(start_date,end_date=end_date)
print('初始化完成:',datetime.datetime.now()-begin)
self.Cal_sentiment()
print('打分完成',datetime.datetime.now()-begin)
self.save_Result(self.date_list[-5:])   #保存

print(((self.close/self.pre_close-1).loc[end_date,self.buy_higher.loc[end_date_before][self.buy_higher.loc[end_date_before]==True].index]).sort_values())
print(self.Dragon_Stock.loc[end_date_before][self.Dragon_Stock.loc[end_date_before]==True])

send_file(['015624'] , '/data/user/015624/%s历史市场情绪分析.xlsx'%str(end_date))



