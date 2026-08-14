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

###################涨停模式#########################
# 1、异动前排板:提供存在消息面的板块Concept_list,符合市场方向的交易标的Direction_Stock,板块整体涨幅必须大于concept_pct
def BigChange_Limit(Concept_list,Direction_Stock,concept_pct=0.005):
    # 注意：该方式不需要删除板块，因为涨停数量≥3了后不会再触发了
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
    # 1、获取板块数据，判断板块强度是否符合条件
    Concept_Pct = get_concept_value(factor='Pct_Change',concept_list=Concept_list)
    Concept_Pct= Concept_Pct.iloc[-1][Concept_Pct.iloc[-1]>=concept_pct].index.to_list()
    for Concept in Concept_Pct:
        #获取板块内个股
        # 获取板块个股数据
        Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
        Cocnept_stock_pct = Concept_stock / pre_close.loc[Concept_stock.columns] - 1
        Concept_limit = (Concept_stock == max_price.loc[Concept_stock.columns])
        if len(Concept_limit)>=2:
            # 判断：如果符合市场方向的标的存在，就获取，如果不存在，就获取全部个股
            if Concept in Direction_Stock.keys():
                prepare_stock = set(Direction_Stock[Concept])
            else:
                prepare_stock = set(Cocnept_stock_pct.columns)
            # 2、判断该板块上一分钟封板数量是否≥3，如果是，则不交易：
            if Concept_limit.iloc[-2].sum()<3:
                # 3、获取该分钟封板个股（即上一分钟未封板，这一分钟封板）
                Minute_Limit = (Concept_limit[prepare_stock].iloc[-1]==True) & (Concept_limit[prepare_stock].iloc[-2]==False)
                buy_stock = Minute_Limit[Minute_Limit==True].index.to_list()
                if len(buy_stock)>0:
                    message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：异动板块前排板' + str(buy_stock))
                    send_message(message)
                    Concept_list.remove(Concept)
    return Concept_list

# 2、补涨板：提供有补涨板机会的板块Concept_list，板块的龙头标的Dragon_stock，板块的低位标的Lower_Stock，是否需要龙头涨停才打板：IF_Dragon_Limit
def Concept_LowerLimit(Concept_list,Dragon_stock,Lower_Stock,IF_Dragon_Limit=True):
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
    for Concept in Concept_list:
        # 1、获取板块数据
        Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
        Concept_limit = (Concept_stock == max_price.loc[Concept_stock.columns])
        Cocnept_stock_pct = Concept_stock / pre_close.loc[Concept_stock.columns] - 1
        Concept_dragon_stock = Dragon_stock[Concept]
        Concept_lower_stock = Lower_Stock[Concept]
        if len(Concept_limit)>=2:
            if IF_Dragon_Limit==True:
                # 2、只要龙头股涨停，就可以交易
                if Concept_limit[Concept_dragon_stock].iloc[-1].sum()>0:
                    # 3、低位个股这一分钟封板，就交易
                    trade_stock = (Concept_limit[Concept_lower_stock].iloc[-1]==True) & ((Concept_limit[Concept_lower_stock].iloc[-2]==False))
                    trade_stock = trade_stock[trade_stock==True].index.to_list()
                    if len(trade_stock)>0:
                        message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：异动板块前排板' + str(trade_stock))
                        send_message(message)
                        Concept_list.remove(Concept)

            elif IF_Dragon_Limit==False:
                # 2、只要龙头震荡，就可以交易
                if Cocnept_stock_pct[Concept_dragon_stock].iloc[-1].min()>-0.05:
                    # 3、低位个股这一分钟封板，就交易
                    trade_stock = (Concept_limit[Concept_lower_stock].iloc[-1] == True) & ((Concept_limit[Concept_lower_stock].iloc[-2] == False))
                    trade_stock = trade_stock[trade_stock == True].index.to_list()
                    if len(trade_stock) > 0:
                        message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：异动板块前排板' + str(trade_stock))
                        send_message(message)
                        Concept_list.remove(Concept)

    return Concept_list

# 3、分歧顶高度板：提供昨日爆发板块Concept_list，昨日爆发板块的前排股Dragon_stock
def Disagree_Limit(Concept_list,Dragon_stock):
    now_time = int(datetime.datetime.now().strftime('%H%M'))
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    if ((now_time >= 930) & (now_time < 940)):
        for Concept in Concept_list:
            # 1、获取板块个股数据，和涨停标的
            Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
            Concept_limit = (Concept_stock == max_price.loc[Concept_stock.columns])[Dragon_stock[Concept]]
            if len(Concept_limit)>=2:
                # 2、获取板块该分钟涨停的个股
                trade_stock =(Concept_limit.iloc[-1]==True) & (Concept_limit.iloc[-2]==False)
                trade_stock = trade_stock[trade_stock==True].index.to_list()
                if len(trade_stock) > 0:
                    message = str(time.strftime("%H:%M:%S", time.localtime()) + ' ' + Concept + '发生交易：板块分歧交易最强' + str(trade_stock))
                    send_message(message)
                    Concept_list.remove(Concept)

    return Concept_list

# 4、市场龙头反包板：提供市场龙头Market_Dragon
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

# 5.1 跌停潮逆势板：提供主流板块Concept_list，主流板块未出现大幅调整的标的Active_stock，主流板块整体跌幅小于Concept_pct，跌停数量为Down_Num
def LimitDown_CooperationLimit(Concept_list,Active_stock,Concept_pct=-0.01,Down_Num=5):
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    pre_close = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'pre_close']
    # 1、获取涨幅在-1%以下的板块
    Concept_Pct = get_concept_value(factor='Pct_Change', concept_list=Concept_list)
    Concept_Choice = Concept_Pct.iloc[-1][Concept_Pct.iloc[-1] < Concept_pct ].index.to_list()
    for Concept in Concept_Choice:
        # 2、判断板块内跌停的个股数量是否大于等于5
        Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
        Concept_stock_pct = Concept_stock/pre_close.loc[Concept_stock.columns]-1
        if (Concept_stock_pct.iloc[-1]<-0.07).sum()>=Down_Num:
            # 3、观察那些没有大幅调整的活跃板块是否上板，上板就交易
            Limit_stock = (Concept_stock[Active_stock[Concept]] == max_price.loc[Active_stock[Concept]])
            if len(Limit_stock)>=2:
                # 4、个股在该分钟刚刚上板
                Limit_stock = (Limit_stock.iloc[-1]==True) &  (Limit_stock.iloc[-2]==False)
                Limit_stock = Limit_stock[Limit_stock==True].index.to_list()
                if len(Limit_stock)>0:
                    message = str(time.strftime("%H:%M:%S", time.localtime()) + ' 发生交易：逆势封板个股' + str(Limit_stock))
                    send_message(message)
                    Concept_list.remove(Concept)
    return Concept_list

#5.2 跌停潮逆势板的第二日接力：提供主流板块Concept_list，昨日逆势封板的个股Active_stock，主流板块整体跌幅小于Concept_pct
def LimitDown_TomorrowLimit(Concept_list,Active_stock,Concept_pct=0.01):
    all_data = data_prepare(datetime.datetime.now().strftime('%Y%m%d'))
    max_price = all_data.loc[datetime.datetime.now().strftime('%Y%m%d'), 'max_price']
    # 1、获取涨幅在1%以下的板块
    Concept_Pct = get_concept_value(factor='Pct_Change', concept_list=Concept_list)
    Concept_Choice = Concept_Pct.iloc[-1][Concept_Pct.iloc[-1] < Concept_pct].index.to_list()

    for Concept in Concept_Choice:
        # 2、判断板块内前一分钟涨停数量是否≥3，如果是则不交易
        Concept_stock = get_oneconcept_alldata(concept_name=Concept, factor_list=['ClosePx'])['ClosePx'].fillna(method='ffill')
        Concept_Limit_stock =(Concept_stock == max_price.loc[Concept_stock.columns])
        if len(Concept_Limit_stock)>=2:
            if Concept_Limit_stock.iloc[-2].sum()<3:
                # 3、昨天逆势涨停的个股在该分钟刚刚上板
                Limit_stock = (Concept_Limit_stock[Active_stock[Concept]].iloc[-1] == True) & (Concept_Limit_stock[Active_stock[Concept]].iloc[-2] == False)
                Limit_stock = Limit_stock[Limit_stock==True].index.to_list()
                if len(Limit_stock)>0:
                    message = str(time.strftime("%H:%M:%S", time.localtime()) + ' 发生交易：逆势封板个股的第二日接力' + str(Limit_stock))
                    send_message(message)
                    Concept_list.remove(Concept)

    return Concept_list


################盘前正经的数据准备########################
# 1、获取上个交易日日期，并读取文件
#股票池
Conept_AllStock = pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=0 ,index_col=0).iloc[:, :3]
Conept_DelStock = set(pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=1 ,index_col=0)['子主题名称'].dropna())
concept_monitor=[]
for concept in sorted(list(set(Conept_AllStock['子主题']))):
    if (len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))<50) & (len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))>5):
        if concept not in Conept_DelStock:
            concept_monitor.append(concept)

# 1、获取上个交易日日期，并读取文件
yesterday = getData.get_date_range(start_date=20210101,end_date=int(datetime.datetime.now().strftime('%Y%m%d')))[-2]
Concept_Select = pd.read_excel('/data/user/015624/板块筛选/'+str(yesterday)+'板块初步筛选.xlsx',sheet_name='活跃板块策略',index_col=0)
Concept_Select2 = pd.read_excel('/data/user/015624/板块筛选/'+str(yesterday)+'板块初步筛选.xlsx',sheet_name='异动前排板',index_col=0)
Concept_Select3 = pd.read_excel('/data/user/015624/板块筛选/'+str(yesterday)+'板块初步筛选.xlsx',sheet_name='补涨板',index_col=0)
Concept_Select4 = pd.read_excel('/data/user/015624/板块筛选/'+str(yesterday)+'板块初步筛选.xlsx',sheet_name='昨日爆发板块前排顶板',index_col=0).dropna()
Concept_Select5 = pd.read_excel('/data/user/015624/板块筛选/'+str(yesterday)+'板块初步筛选.xlsx',sheet_name='首阴龙头',index_col=0)

# （1）异动前排板
Concept_list_BigChange_Limit = list(set(Concept_Select2.index.to_list()).intersection(set(concept_monitor)))
Direction_Stock_BigChange_Limit = {}
for concept in Concept_list_BigChange_Limit:
    Direction_Stock_BigChange_Limit[concept] = eval(Concept_Select2.loc[concept,'板块个股'])
# （2）补涨板
Concept_list_LowerLimit_True = list(set(Concept_Select3.index.to_list()).intersection(set(concept_monitor)))
Dragon_stock_BigChange_Limit_True = {}
Lower_Stock_BigChange_Limit_True = {}
for concept in Concept_list_LowerLimit_True:
    Dragon_stock_BigChange_Limit_True[concept] = eval(Concept_Select3.loc[concept,'龙头股'])
    Lower_Stock_BigChange_Limit_True[concept] = eval(Concept_Select3.loc[concept,'补涨股'])

Concept_list_LowerLimit_False = list(set(Concept_Select.index.to_list()).intersection(set(concept_monitor)))
Dragon_stock_BigChange_Limit_False = {}
Lower_Stock_BigChange_Limit_False = {}
for concept in Concept_list_LowerLimit_False:
    Dragon_stock_BigChange_Limit_False[concept] = eval(Concept_Select.loc[concept,'龙头股'])
    Lower_Stock_BigChange_Limit_False[concept] = eval(Concept_Select.loc[concept,'未启动个股'])

# （3）分歧顶高度板
Concept_list_Disagree_Limit = list(set(Concept_Select4.index.to_list()).intersection(set(concept_monitor)))
Dragon_stock_Disagree_Limit ={}
for concept in Concept_list_Disagree_Limit:
    Dragon_stock_Disagree_Limit[concept] = eval(Concept_Select4.loc[concept,'龙头股'])

# （4）市场龙头反包板
Market_Dragon = list(set(Concept_Select5['首阴龙头']))

# （5）逆势跌停潮的接力
Concept_list_LimitDown_CooperationLimit = list(set(Concept_Select.index.to_list()).intersection(set(concept_monitor)))
Active_stock_LimitDown_CooperationLimit = {}
for concept in Concept_list_LimitDown_CooperationLimit:
    Active_stock_LimitDown_CooperationLimit[concept] =  eval(Concept_Select.loc[concept,'未调整人气股'])

Concept_list_LimitDown_TomorrowLimit = Concept_list_LimitDown_CooperationLimit.copy()
Active_stock_LimitDown_TomorrowLimit = Active_stock_LimitDown_CooperationLimit.copy()
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
        Concept_list_BigChange_Limit = BigChange_Limit(Concept_list=Concept_list_BigChange_Limit,Direction_Stock=Direction_Stock_BigChange_Limit)
        Concept_list_LowerLimit_True = Concept_LowerLimit(Concept_list=Concept_list_LowerLimit_True, Dragon_stock=Dragon_stock_BigChange_Limit_True, Lower_Stock=Lower_Stock_BigChange_Limit_True, IF_Dragon_Limit=True)
        Concept_list_LowerLimit_False = Concept_LowerLimit(Concept_list=Concept_list_LowerLimit_False, Dragon_stock=Dragon_stock_BigChange_Limit_False, Lower_Stock=Lower_Stock_BigChange_Limit_False, IF_Dragon_Limit=False)
        Concept_list_Disagree_Limit = Disagree_Limit(Concept_list=Concept_list_Disagree_Limit, Dragon_stock=Dragon_stock_Disagree_Limit)
        Market_Dragon = Market_Dragon_Limit(Market_Dragon=Market_Dragon)
        Concept_list_LimitDown_CooperationLimit = LimitDown_CooperationLimit(Concept_list=Concept_list_LimitDown_CooperationLimit, Active_stock=Active_stock_LimitDown_CooperationLimit)
        Concept_list_LimitDown_TomorrowLimit = LimitDown_TomorrowLimit(Concept_list=Concept_list_LimitDown_TomorrowLimit,Active_stock=Active_stock_LimitDown_TomorrowLimit)
        time.sleep(1)
    except:
        print(now_time+'可能存在小问题')

