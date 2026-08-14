from ConceptApi import *
import requests,json, sys

sys.path.append('/data/group/800319/')
from realtimeApi.getdata_from_open import *
from dataApi import getData, stockList

# 信息传送 #
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

############ 每日晚间运行：先进行数据准备 ##################
class EveryDay_Concept_Select(object):
    def __init__(self,Today):
        # 1、获取当天所有板块
        Conept_AllStock = pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx', sheet_name=0,index_col=0).iloc[:, :3]
        Concept_list = {}
        for concept in sorted(list(set(Conept_AllStock['子主题']))):
            if (len(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index)) < 50) & (
                    len(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index)) > 5):
                Concept_list[concept] = list(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index))

        self.Concept_list = Concept_list
        self.Conept_AllStock = Conept_AllStock
        # 2、获取当天日期
        date_list = getData.get_date_range(20210101, int(Today))[-20:]
        start_date = date_list[0]
        end_date = date_list[-1]
        date_list1 = [str(x) for x in date_list]

        self.start_date = start_date
        self.end_date = end_date
        # 3、获取个股数据
        s = FactorData()
        Stock_Price = s.get_factor_value('WIND_AShareEODPrices',factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH','S_DQ_CLOSE','S_DQ_LOW','S_DQ_AMOUNT','S_DQ_LIMIT','S_DQ_ADJCLOSE','S_DQ_STOPPING'],trade_dt=['>=' + str(start_date),'<='+ str(end_date)])
        pre_close = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_PRECLOSE')
        open = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_OPEN')
        high = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_HIGH')
        low = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_LOW')
        close = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE')
        amt = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_AMOUNT')
        close_adj = Stock_Price.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_ADJCLOSE')

        Limit_Price = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1,factor_names=['mdc_maxpx']).iloc[:, 0].unstack()
        Lowest_Price = s.get_factor_value('Basic_factor', stock=[], mddate=date_list1, factor_names=['mdc_minpx']).iloc[:, 0].unstack()

        pre_close.index = [int(x) for x in pre_close.index]
        open.index = [int(x) for x in open.index]
        high.index = [int(x) for x in high.index]
        low.index = [int(x) for x in low.index]
        close.index = [int(x) for x in close.index]
        amt.index = [int(x) for x in amt.index]
        close_adj.index = [int(x) for x in close_adj.index]
        Limit_Price.index = [int(x) for x in Limit_Price.index]
        Lowest_Price.index = [int(x) for x in Lowest_Price.index]

        min_close = getData.get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date).dropna(how='all', axis=1)
        min_close.fillna(method='ffill', inplace=True)
        min_close.columns = pd.Series(min_close.columns).apply(lambda x: stockList.trans_int2windcode(x))


        code_list=list(set(Limit_Price.columns).intersection(close.columns).intersection(min_close.columns))

        self.close = close
        self.pre_close = pre_close
        self.open = open
        self.amt = amt
        # 4、获取连板高度
        Limit_Stock = (close[code_list] == Limit_Price[code_list])
        Lowest_Stock = (close[code_list] == Lowest_Price[code_list])

        self.Limit_Stock = Limit_Stock
        self.Lowest_Stock = Lowest_Stock

        Limit_High = get_basic_values('Limit_High', start_date=start_date, end_date=end_date,read_path='/data/group/800319/Temporary_Data/RawData/BasicData/').shift(1)
        Limit_High.columns=pd.Series(Limit_High.columns).apply(lambda x:stockList.trans_int2windcode(x))

        Limit_High = Limit_High*Limit_Stock + Limit_Stock*1

        self.Limit_High = Limit_High


        Limit_Price_inday = pd.DataFrame(np.array(Limit_Price.loc[min_close.index.get_level_values('date')]),
                                       index=min_close.index, columns=Limit_Price.columns)[code_list]

        Limit_stock_inday = min_close[code_list]==Limit_Price_inday
        self.Limit_stock_inday = Limit_stock_inday

    def Get_Concept_Active(self,active_pct=0.02,active_rank=20,active_day=5):
        # 1、获取个股涨跌幅
        stock_pct = self.close.pct_change(1)
        stk_pct = pd.concat([self.Conept_AllStock[['子主题']], stock_pct[self.Conept_AllStock.index].T], axis=1)
        con_pct = stk_pct.groupby('子主题').mean().T
        con_pct_rank = con_pct.rank(axis=1,ascending=False)

        # 2、获取最近5日活跃过的板块
        Change_concept = ((con_pct >= active_pct) & (con_pct_rank <= active_rank)).iloc[-active_day-1:]

        # （1）最近5日没有异动过的板块
        No_Change_concept = Change_concept.sum()[Change_concept.sum()==0].index.to_list()
        self.No_Change_concept = No_Change_concept

        # （2）最近5日活跃过但是昨天没有活跃的板块
        Active_Concept = (Change_concept.iloc[:-1].sum() > 0) & (Change_concept.iloc[-1] == False)
        Active_Concept = Active_Concept[Active_Concept == True].index.to_list()
        self.Active_Concept = Active_Concept

        # （3）最近5日没有异动，但是当日异动的板块
        Boom_Concept = (Change_concept.iloc[:-1].sum()==0) & (Change_concept.iloc[-1]==True)
        Boom_Concept = Boom_Concept[Boom_Concept==True].index.to_list()
        self.Boom_Concept = Boom_Concept

        # （4）板块内最高高度板为2连板及以上
        con_limit = pd.concat([self.Conept_AllStock[['子主题']], self.Limit_High[self.Conept_AllStock.index].T], axis=1)
        con_limit = con_limit.groupby('子主题').max().T
        Dragon_Concept = con_limit.iloc[-1][con_limit.iloc[-1]>=2].index.to_list()
        self.Dragon_Concept = Dragon_Concept

    def Get_Market_Dragon(self):
        ###########获取市场中的前三高的板，最高必须为3板##############
        Limit_market=self.Limit_High.copy()
        Limit_market[(Limit_market.T-Limit_market.max(axis=1)).T==0]=0
        Limit_market[(Limit_market.T - Limit_market.max(axis=1)).T == 0] = 0
        Limit_market=Limit_market.max(axis=1)
        Limit_market = Limit_market.apply(lambda x: max(3, x))
        #####对于个股和市场高度差距过高>=4板，且个股自身也是高位板>=5板，那就不做：市场不依赖于个股自己
        No_trade = (self.Limit_High.T - self.Limit_High.max(axis=1) <= -4).T & (self.Limit_High >= 5)
        ########最后一个板必须是一致封板：即在板上的时间占比大于70%#############
        Together_board=self.Limit_stock_inday.groupby('date').sum()
        Market_Dragon = ((((self.Limit_High.T - Limit_market) >= 0).T) & (Together_board / 242 >= 0.7) & ~No_trade).shift(1)
        ######后一天放量收阴：要不然是相比于昨天收跌，要不然是收盘价比开盘价低##################
        stock_code=list(set(self.pre_close.columns).intersection(set(self.close.columns)))
        K_line=((self.close.loc[Market_Dragon.index,stock_code]<self.open.loc[Market_Dragon.index,stock_code]) |
                (self.close.loc[Market_Dragon.index,stock_code]<self.pre_close.loc[Market_Dragon.index,stock_code]))
        ######后一天放量,或者跌停###########
        Max_amt=((self.amt/self.amt.rolling(5).mean().shift(1)>=1.5).loc[Market_Dragon.index,stock_code] | ((self.close.loc[Market_Dragon.index,stock_code]==self.Lowest_Stock.loc[Market_Dragon.index,stock_code])))
        ######筛选出来的市场高度票的反包########
        Stock_Choice=(Market_Dragon & K_line & Max_amt)
        self.Stock_Choice=Stock_Choice

        StockList = self.Stock_Choice.loc[self.end_date][self.Stock_Choice.loc[self.end_date] == True].index.to_list()
        if len(StockList) == 0:
            print('昨日无龙头股首阴')
        return StockList

    def Get_Concept_Select(self,save_path='/data/user/015624/板块筛选/'):
        # 1、活跃板块策略：开盘位置半路+非主流板块盘中位置半路+板块横盘高标低吸+日间层面低吸+板块高度高时的补涨板
        # （1）板块筛选：近5日爆发过，但是昨日没有爆发的板块
        # （2）板块龙头股：近10日涨幅>=20% & 最大的前2只个股 + 2连板及以上的个股
        # （3）板块人气股：近10日涨幅>=20% + 2连板及以上的个股
        # （4）板块未调整人气股：近10日涨幅>=20% & 当前回撤幅度＜最大涨幅/2的个股 + 2连板及以上的个股
        # （5）板块未启动个股：近10日涨幅≤10% & 近3日没有涨停
        Catch_Concept = pd.DataFrame(index=self.Active_Concept,columns=['龙头股','人气股','未调整人气股','未启动个股'])
        for concept in Catch_Concept.index:
            concept_stock = list(set(self.Conept_AllStock[self.Conept_AllStock['子主题']==concept].index))
            active_stock = self.close[concept_stock].pct_change(10).iloc[-1][self.close[concept_stock].pct_change(10).iloc[-1]>=0.2]

            max_up = self.close[concept_stock].iloc[10:].max()/self.close[concept_stock].iloc[-10]-1
            now_retrace = self.close[concept_stock].iloc[-1]/self.close[concept_stock].iloc[10:].max()-1
            No_retrace_stock = (abs(now_retrace)<max_up/2)[(abs(now_retrace)<max_up/2)==True]

            No_retrace_Power_Stock = set(No_retrace_stock.index).intersection(set(active_stock.index))
            Dragon_Stock = active_stock.sort_values().iloc[-2:].index.to_list()
            Power_Stock = active_stock.index.to_list()
            Limit_Stock = self.Limit_High[concept_stock].iloc[-1][self.Limit_High[concept_stock].iloc[-1]>=2].index.to_list()

            Delay_Stock = (self.close[concept_stock].pct_change(10).iloc[-1] <= 0.1) & (self.Limit_Stock[concept_stock].iloc[-3:].sum() == 0)
            Delay_Stock = set(Delay_Stock[Delay_Stock == True].index)

            if len(set(Power_Stock).union(set(Limit_Stock)))>0:
                Catch_Concept.loc[concept,'龙头股'] = set(Dragon_Stock).union(set(Limit_Stock))
                Catch_Concept.loc[concept, '人气股'] = set(Power_Stock).union(set(Limit_Stock))
                Catch_Concept.loc[concept, '未调整人气股'] = set(No_retrace_Power_Stock).union(set(Limit_Stock))
                Catch_Concept.loc[concept, '未启动个股'] = Delay_Stock
        Catch_Concept.dropna(inplace=True)

        self.Catch_Concept = Catch_Concept

        # 2、盘中龙头低吸策略：连板龙头的不卡位低吸
        #（1）筛选出龙头为2板或者以上高度的板块，个板块对应的龙头股
        Limit_Concept = pd.DataFrame(index=self.Dragon_Concept,columns=['龙头股','最高连板数'])
        for concept in Limit_Concept.index:
            concept_stock = list(set(self.Conept_AllStock[self.Conept_AllStock['子主题'] == concept].index))
            Dragon_Stock = set(self.Limit_High[concept_stock].iloc[-1][self.Limit_High[concept_stock].iloc[-1]>=2].index)
            if len(Dragon_Stock)>0:
                Limit_Concept.loc[concept,'龙头股'] = Dragon_Stock
                Limit_Concept.loc[concept, '最高连板数'] = self.Limit_High[concept_stock].iloc[-1].max()
        Limit_Concept.dropna(inplace=True)

        self.Limit_Concept=Limit_Concept

        # 3、打板：异动前排板
        # （1）板块筛选：最近5日从没有爆发过的板块
        # （2）获取板块内全部个股
        NoChange_Concept = pd.DataFrame(index=self.No_Change_concept,columns=['板块个股'])
        for concept in NoChange_Concept.index:
            concept_stock = set(self.Conept_AllStock[self.Conept_AllStock['子主题'] == concept].index)
            if len(Dragon_Stock)>0:
                NoChange_Concept.loc[concept,'板块个股'] = concept_stock

        self.NoChange_Concept = NoChange_Concept

        # 4、打板：板块高度低时的补涨板
        # （1）板块筛选：昨日爆发板块+封板高度在2板及以上的板块
        Boom_Concept = set(self.Dragon_Concept).union(set(self.Boom_Concept))
        DelayUP_Concpet = pd.DataFrame(index=Boom_Concept,columns=['龙头股','连板高度','补涨股'])
        for concept in DelayUP_Concpet.index:
            concept_stock = set(self.Conept_AllStock[self.Conept_AllStock['子主题'] == concept].index)
            Dragon_Stock = set(self.Limit_High[concept_stock].iloc[-1][self.Limit_High[concept_stock].iloc[-1]==self.Limit_High[concept_stock].iloc[-1].max()].index)

            Delay_Stock = (self.close[concept_stock].pct_change(10).iloc[-1]<=0.1) & (self.Limit_Stock[concept_stock].iloc[-3:].sum()==0)
            Delay_Stock = set(Delay_Stock[Delay_Stock==True].index)

            if len(Dragon_Stock)>0:
                DelayUP_Concpet.loc[concept,'龙头股']=Dragon_Stock
                DelayUP_Concpet.loc[concept, '连板高度'] = self.Limit_High[concept_stock].iloc[-1].max()
                DelayUP_Concpet.loc[concept,'补涨股']=Delay_Stock
        DelayUP_Concpet.dropna(inplace=True)
        self.DelayUP_Concpet = DelayUP_Concpet

        # 5、打板：昨天爆发板块，最先涨停的前3个板
        LimitDragon_Concept = pd.DataFrame(index=self.Boom_Concept,columns=['龙头股'])
        for concept in DelayUP_Concpet.index:
            concept_stock = set(self.Conept_AllStock[self.Conept_AllStock['子主题'] == concept].index)
            Dragon_Stock = set(self.Limit_High[concept_stock].iloc[-1][self.Limit_High[concept_stock].iloc[-1]==True].index)

            if len(Dragon_Stock)>0:
                if len(Dragon_Stock)<=3:
                    LimitDragon_Concept.loc[concept,'龙头股'] = Dragon_Stock
                else:
                    Stock_LimitTime = pd.Series(index=Dragon_Stock)
                    Inday_Limit = self.Limit_stock_inday[Dragon_Stock].loc[self.end_date]
                    for stock in Stock_LimitTime.index:
                        Stock_LimitTime.loc[stock] = int(Inday_Limit[stock][Inday_Limit[stock]==True].index[0])
                    LimitDragon_Concept.loc[concept,'龙头股'] = set(Stock_LimitTime.sort_values().iloc[:3].index)

        LimitDragon_Concept.dropna(inplace=True)
        self.LimitDragon_Concept = LimitDragon_Concept

        # 6、龙头首阴反包个股
        Market_Dragon = self.Get_Market_Dragon()
        Market_Dragon = pd.DataFrame(Market_Dragon,columns=['首阴龙头'])

        self.Market_Dragon = Market_Dragon

        # 数据保存
        writer = pd.ExcelWriter(save_path + str(self.end_date) + '板块初步筛选.xlsx')
        self.Catch_Concept.to_excel(writer, sheet_name='活跃板块策略')
        self.Limit_Concept.to_excel(writer, sheet_name='连板龙头的不卡位低吸')
        self.NoChange_Concept.to_excel(writer, sheet_name='异动前排板')
        self.DelayUP_Concpet.to_excel(writer, sheet_name='补涨板')
        self.LimitDragon_Concept.to_excel(writer, sheet_name='昨日爆发板块前排顶板')
        self.Market_Dragon.to_excel(writer, sheet_name='首阴龙头')
        writer.close()

        send_file(['015624'], save_path + str(self.end_date) + '板块初步筛选.xlsx')

###########获取数据##############
Today = datetime.datetime.now().strftime('%Y%m%d')
Today = '20210607'
self = EveryDay_Concept_Select(Today)
self.Get_Concept_Active()
self.Get_Concept_Select()
