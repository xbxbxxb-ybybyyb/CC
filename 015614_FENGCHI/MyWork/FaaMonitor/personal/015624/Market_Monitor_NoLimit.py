import requests,json, sys
sys.path.append('/data/group/800319/')
from realtimeApi.getdata_from_open import *
from dataApi import getData

# 信息传送 #
def send_message(msg,users=['015624']):
    ########发送消息##########
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)

#########已经写完的模式###################
# 1、高标低吸模式：提供板块的高位横盘龙头/人气股：Pop_Stock，板块涨幅必须大于concept_pct，低吸个股最大涨幅必须低于pct_max
# （1）出现个股涨停，在0%-4%之间的位置低吸核心人气股
# （2）没有个股涨停，但是板块强度高，在0%-4%之间的位置低吸核心人气股
Concept_Pop_Stock={'六氟磷酸锂':['002407.SZ','002709.SZ','002759.SZ','002326.SZ']}
def Dragon_SideWay_Buy(Concept_Pop_Stock,concept_limit=0.03,pct_max=0.04):
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
    # 1、获取板块数据,先确保到当前位置还有板块需要交易
    if len(Concept_Pop_Stock)>0:
        Concept_list =set(Concept_Pop_Stock.keys())
        Concept_Pct = get_concept_value(factor='Pct_Change', concept_list=Concept_list)
        Concept_Choice = Concept_Pct.iloc[-1][Concept_Pct.iloc[-1]>0].index.to_list()
        # 开始板块循环
        for Concept in Concept_Choice:
            # 获取板块个股数据
            Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
            Pop_pct = Concept_stock[Concept_Pop_Stock[Concept]] /pre_close.loc[Concept_Pop_Stock[Concept]]-1
            Limit_Stock = (Concept_stock == max_price.loc[Concept_stock.columns])
            # 先排除掉一字板，可能是因为个股自身的消息面；所以必须要时间是要＞930
            if Limit_Stock.index[-1]>=930:
                buy_list = []
                # 两种情况：（可以统一归类为一种，日内出现了涨停，低吸强度较好的人气股）
                # （1）个股日内刚封板，此时低吸强度较好的龙头人气股
                # （2）个股日内已经封板了，此时低吸水下到水上的龙头人气股
                # （3）板块内没有个股封板，但是板块强度很高
                if (((Limit_Stock.iloc[-1].sum()-Limit_Stock.loc[925].sum())>=1) or (Concept_Pct[Concept].iloc[-1]>=concept_limit)):
                    # 3、在这个封板点，如果个股在水上，且涨幅低于4%(8%)，就是买点
                    WaterUp_stock = Pop_pct.iloc[-1][Pop_pct.iloc[-1]>0][Pop_pct.iloc[-1]<0.08]
                    for stock in WaterUp_stock.index:
                        if ((stock[:3] == '300') or (stock[:3] == '688')):
                            if (WaterUp_stock.loc[stock]< pct_max * 2):
                                buy_list.append(stock)
                        else:
                            if (WaterUp_stock.loc[stock]< pct_max):
                                buy_list.append(stock)

                if len(buy_list)>0:
                    Limit_Stock_Now = Limit_Stock.iloc[-1][Limit_Stock.iloc[-1]==True].index.to_list()
                    s = FactorData()
                    buy_stock_name = s.get_factor_value('Basic_factor', buy_list, [datetime.datetime.now().strftime('%Y%m%d')],['short_name'])['short_name']

                    if len (Limit_Stock_Now)>0:
                        limit_stock_now = s.get_factor_value('Basic_factor', Limit_Stock_Now , [datetime.datetime.now().strftime('%Y%m%d')], ['short_name'])['short_name']
                        message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：资金回流板块，涨停个股为'+str(set(limit_stock_now))+'，低吸龙头人气股' + str(set(buy_stock_name)))
                    else:
                        message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：资金回流板块，低吸龙头人气股' + str(set(buy_stock_name)))
                    send_message(message)
                    Concept_list.remove(Concept)
                    # 把已经交易的人气股删除 #
                    Concept_Pop_Stock[Concept] = set(Concept_Pop_Stock[Concept]).difference(set(buy_list))
                    if len(Concept_Pop_Stock[Concept])==0:
                        Concept_Pop_Stock.pop(Concept)

    return Concept_Pop_Stock

# 可以日间做一个初步筛选
# 2、龙头不卡位低吸：提供市场总龙头Market_Dragon，Concept_Dragon_Stock，板块涨幅必须大于concept_pct，低吸个股最大涨幅必须低于pct_max
Concept_Dragon_Stock={'六氟磷酸锂':['002407.SZ','002709.SZ','002759.SZ','002326.SZ']}
Market_Dragon= {'003032.SZ'}
def Drgon_LowerBuy(Market_Dragon,Concept_Dragon_Stock,concept_pct=0.015,pct_max=0.04):
    if len(Concept_Dragon_Stock)>0:
        all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
        max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
        pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
        Concept_list = set(Concept_Dragon_Stock.keys())
        # 1、市场高标是否涨停
        stock_close = get_stock_factor(factor_list=['ClosePx'],stock_list=Market_Dragon)
        if (stock_close['ClosePx'].iloc[-1] == max_price.loc[Market_Dragon]).sum()>=1:
            Concept_Pct = get_concept_value(factor='Pct_Change', concept_list=Concept_list)
            Concept_Choice = Concept_Pct.iloc[-1][Concept_Pct.iloc[-1] > concept_pct].index.to_list()
            # 2、对于板块涨幅符合标准的板块
            for Concept in Concept_Choice:
                # 3、获取板块个股数据，只有板块内没有涨停板，才会考虑接下来的龙头低吸
                concept_stock = get_oneconcept_alldata(concept_name=Concept,factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
                if (concept_stock.iloc[-1]==max_price.loc[concept_stock.columns]).sum() == 0:
                    # 4、市场高标涨停，板块强度较高且板块没有涨停，如果龙头个股在水上，且涨幅低于4%(8%)，就是买点
                    dragon_pct = concept_stock[Concept_Dragon_Stock[Concept]]/pre_close.loc[Concept_Dragon_Stock[Concept]]-1
                    buy_list = []
                    for stock in Concept_Dragon_Stock[Concept]:
                        if ((stock[:3]=='300') or (stock[:3]=='688')):
                            if (dragon_pct.iloc[-1]<pct_max*2) & (dragon_pct.iloc[-1]>0):
                                buy_list.append(stock)
                        else:
                            if (dragon_pct.iloc[-1]<pct_max) & (dragon_pct.iloc[-1]>0):
                                buy_list.append(stock)
                    # 5、如果有交易标的，就买入
                    if len(buy_list)>0:
                        s = FactorData()
                        buy_stock_name = s.get_factor_value('Basic_factor', buy_list, [datetime.datetime.now().strftime('%Y%m%d')],['short_name'])['short_name']
                        message = str((time.strftime("%H:%M:%S", time.localtime())) + ' ' + Concept + '发生交易：市场高标封板，低吸龙头' + str(set(buy_stock_name)))
                        send_message(message)
                        Concept_Dragon_Stock.pop(Concept)

    return Concept_Dragon_Stock

# 3、开盘半路模式:提供表现活跃的板块（没有结束的板块）Concept_list，板块龙头股Dragon_Stock，板块涨幅必须位于concept_pct_list之间，追涨个股涨幅要求必须大于up_pct
Concept_Dragon_Stock={'六氟磷酸锂':['002407.SZ','002709.SZ','002759.SZ','002326.SZ']}
def Dragon_BuyHalfWay(Concept_Dragon_Stock,concept_pct_list=[-0.05,0.03],up_pct=0.01):
    if len(Concept_Dragon_Stock) > 0:
        now_time = int(datetime.datetime.now().strftime('%H%M'))
        # 只会在开盘的前10分钟交易
        if ((now_time>=930) & (now_time<=940)):
            concept_min,concept_max = concept_pct_list[0], concept_pct_list[1]
            all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
            max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
            pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
            Concept_list = set(Concept_Dragon_Stock.keys())
            # 获取板块数据,板块整体涨幅大于-0.05
            Concept_Pct = get_concept_value(factor='Pct_Change', concept_list=Concept_list)
            Concept_Choice = Concept_Pct.iloc[-1][Concept_Pct.iloc[-1] > concept_min][Concept_Pct.iloc[-1] < concept_max].index.to_list()
            for Concept in Concept_Choice:
                Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
                Concept_stock_pct = Concept_stock / pre_close.loc[Concept_stock.columns] - 1
                Concept_limit = (Concept_stock == max_price.loc[Concept_stock.columns])
                if len(Concept_stock_pct)>=2:
                    # 3、龙头股拉升且龙头股率先拉升,当前拉升的个股和龙头股必须有交集
                    stock_growup = Concept_stock_pct.iloc[-1]-Concept_stock_pct.iloc[-4:-1].min()
                    stock_growup = stock_growup[stock_growup>=up_pct].index.to_list()
                    dragon_grow_up = set(stock_growup).intersection(set(Concept_Dragon_Stock[Concept]))
                    # 龙头涨跌幅必须位于板块个股的前三名 #
                    if len(dragon_grow_up)>0:
                        dragon_pct_rank = Concept_stock_pct.iloc[-1].rank(ascending=False).loc[dragon_grow_up]
                        buy_stock = dragon_pct_rank[dragon_pct_rank<4].index.to_list()
                        if len(buy_stock)>0:
                            buy_list = []
                            for stock in buy_stock:
                                if (stock[:3]=='300') or (stock[:3]=='688'):
                                    if (Concept_stock_pct[stock].iloc[-1] < 0.15) & (Concept_stock_pct[stock].iloc[-1] > 0.05):
                                        buy_list.append(stock)
                                else:
                                    if (Concept_stock_pct[stock].iloc[-1]<0.07) & (Concept_stock_pct[stock].iloc[-1]>0.03):
                                        buy_list.append(stock)

                            if len(buy_list)>0:
                                s = FactorData()
                                buy_stock_name = s.get_factor_value('Basic_factor', buy_list,[datetime.datetime.now().strftime('%Y%m%d')],['short_name'])['short_name']
                                message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：板块开盘启动，追高龙头' + str(set(buy_stock_name)))
                                send_message(message)
                                Concept_Dragon_Stock.pop(Concept)
    return Concept_Dragon_Stock

# 4、盘中半路模式：提供表现活跃的板块（没有结束的板块）Concept_list，板块人气股Pop_Stock，板块政府涨幅必须大于concept_pct，追涨个股涨幅要求必须大于up_pct
Concept_Pop_Stock={'六氟磷酸锂':['002407.SZ','002709.SZ','002759.SZ','002326.SZ']}
def Dragon_BuyInMarket(Concept_Pop_Stock,concept_pct=0.01,up_pct=0.01):
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
    if len(Concept_Pop_Stock)>0:
        Concept_list = set(Concept_Pop_Stock.keys())
        Concept_Pct = get_concept_value(factor='Pct_Change')  # 获取板块数据
        # 1、市场至少有2个及以上的板块涨幅在3%以上
        if len(Concept_Pct)>=30: # 盘中半路至在10：00之后
            if (Concept_Pct.iloc[-1]>= 0.03).sum()>=2:
                # 2、判断自己的板块涨幅是否大于1%
                Concept_Choice = Concept_Pct[Concept_list].iloc[-1][Concept_Pct[Concept_list].iloc[-1] > concept_pct][Concept_Pct[Concept_list].iloc[-1] < 0.03].index.to_list()
                for Concept in Concept_Choice:
                    # 获取板块个股数据
                    Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
                    Concept_stock_pct = Concept_stock / pre_close.loc[Concept_stock.columns] - 1
                    Concept_limit = (Concept_stock == max_price.loc[Concept_stock.columns])
                    # 3、在拉升前3分钟，至少都满足该条件：
                    # （1）板块没有除了一字板以外的封板个股(封板个股-一字板个股数量=0）
                    # （2）板块至少存在3个以上人气股涨幅＞2%，且最高涨幅不能高于7%
                    Concept_active_stock = Concept_Pop_Stock[Concept]
                    for i in range(1,3):
                        if Concept_limit.iloc[-i].sum() - max(Concept_limit.loc[925].sum(),Concept_limit.loc[930].sum()) <= 0:
                            active_stock = (Concept_stock_pct[Concept_Pop_Stock[Concept]].iloc[-1] > 0.02) & (Concept_stock_pct[Concept_Pop_Stock[Concept]].max() <= 0.07)
                            active_stock = active_stock[active_stock == True].index.to_list()
                            Concept_active_stock = set(Concept_active_stock).intersection(set(active_stock))
                        else:
                            Concept_active_stock=[]
                    # 如果满足条件的标的≥3：
                    if len(Concept_active_stock)>=3:
                        # 3、人气股拉升且人气股率先拉升
                        stock_growup = Concept_stock_pct.iloc[-1] - Concept_stock_pct.iloc[-4:-1].min()
                        pop_stock_growup = set(stock_growup[stock_growup >= up_pct].index.to_list()) & (set( Concept_Pop_Stock[Concept]))
                        # 当前拉升的个股和龙头股必须有交集 #
                        if len(pop_stock_growup)>0:
                            #如果当前涨幅＞7%那就不追
                            buy_stock = Concept_stock_pct[pop_stock_growup].iloc[-1]
                            buy_list = []
                            for stock in buy_stock.index:
                                if (stock[:3]=='300') or (stock[:3]=='688'):
                                    if (Concept_stock_pct[stock].iloc[-1] < 0.15) & (Concept_stock_pct[stock].iloc[-1] > 0.03):
                                        buy_list.append(stock)
                                else:
                                    if (Concept_stock_pct[stock].iloc[-1]<0.07) & (Concept_stock_pct[stock].iloc[-1]>0.03):
                                        buy_list.append(stock)

                            if len(buy_list)>0:
                                s = FactorData()
                                buy_stock_name = s.get_factor_value('Basic_factor', buy_list,[datetime.datetime.now().strftime('%Y%m%d')],['short_name'])['short_name']
                                message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：板块启动，追高人气股' + str(set(buy_stock_name)))
                                send_message(message)
                                Concept_Pop_Stock.pop(Concept)

    return Concept_Pop_Stock

# 5、市场龙头反包板：提供市场龙头Market_Dragon
def Market_Dragon_Limit(Market_Dragon):
    if len(Market_Dragon)>0:
        all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
        max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
        # 1、获取市场龙头的分钟频数据
        Market_ClosePx = get_stock_factor(factor_list=['ClosePx'],stock_list=Market_Dragon)
        if len(Market_ClosePx)>=2:
            # 2、观测市场龙头是否在该分钟涨停
            Market_Limit = (Market_ClosePx['ClosePx'] == max_price.loc[Market_Dragon])
            Market_Limit = (Market_Limit.iloc[-1]==True) & (Market_Limit.iloc[-2]==False)
            Market_Limit = Market_Limit[Market_Limit==True].index.to_list()
            if len(Market_Limit)>0:
                message = str(time.strftime("%H:%M:%S", time.localtime()) + ' 发生交易：市场龙头反包板' + str(Market_Limit))
                send_message(message)
                for x in Market_Limit:
                    Market_Dragon.remove(x)

    return Market_Dragon

#######################数据测试：盘前数据准备##############################
#######################开始时间########################
now_time = int(datetime.datetime.now().strftime('%H%M'))
while now_time<925:
    now_time = int(datetime.datetime.now().strftime('%H%M'))
while (now_time>=925) & (now_time<1500):
    # 午休
    while (now_time>1130) & (now_time<1300):
        time.sleep(10)
        now_time = int(datetime.datetime.now().strftime('%H%M'))
    # 测试
    now_time = int(datetime.datetime.now().strftime('%H%M'))
    try:
        Concept_Pop_Stock_lowerbuy = Dragon_SideWay_Buy(Concept_Pop_Stock, concept_limit=0.03, pct_max=0.04)
        Concept_Dragon_Stock = Drgon_LowerBuy(Market_Dragon, Concept_Dragon_Stock, concept_pct=0.015, pct_max=0.04)
        Concept_Dragon_Stock = Dragon_BuyHalfWay(Concept_Dragon_Stock, concept_pct_list=[-0.05, 0.03], up_pct=0.01)
        Concept_Pop_Stock_halfway = Dragon_BuyInMarket(Concept_Pop_Stock, concept_pct=0.01, up_pct=0.01)
        Market_Dragon = Market_Dragon_Limit(Market_Dragon)
        time.sleep(1)
    except:
        print(now_time+'可能存在小问题')
