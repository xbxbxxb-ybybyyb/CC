import ray
import pandas as pd
from xquant.compute.aimr import AIMR
import requests, json, datetime,datetime,os,time
from tqdm import tqdm
import pickle
from xquant.compute.streamcalculation import run_realtime_calculation_by_securities

######发送信息#######
def send_message(users, msg):
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
users=['015624']

#factor_list = ['ClosePx','HighPx','LowPx','OpenPx','TotalVolumeTrade','TotalValueTrade','NumTrades']
factor_list = ['ClosePx','HighPx','TotalVolumeTrade','TotalValueTrade']

# 因子回调计算函数
def Get_RealTime_Data(concept_name,factor_list=factor_list,save_path='/data/group/800442/800319/RealTime_Data/'):
    # factor = 'ClosePx','HighPx','LowPx','OpenPx','TotalVolumeTrade','TotalValueTrade','NumTrades'
    # TotalVolumeTrade：多少手
    # TotalValueTrade：多少万元
    # NumTrades：笔数

    #1、 先判断当日的文件夹在不在，不在就创建文件夹
    #####获取板块标的
    Conept_AllStock = pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx', sheet_name=0,index_col=0).iloc[:, :3]

    concept_list = {}
    for concept in concept_name:
        concept_list[concept.replace('/', '_')] = set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index)

    date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
    os.listdir(save_path)
    if os.path.exists(save_path+date)==False:
        os.makedirs(save_path+date)

    security_list = []
    name_list = []

    for name in concept_list.keys():
        name_list.append(name)
        security_list.append(list(set(concept_list[name])))
        if os.path.exists(save_path + date+'/'+name) == False:
            os.makedirs(save_path + date+'/'+name)

    name_list=pd.DataFrame(name_list,columns=['name_list'])

    def calc_callback(self, df_dict,name_list=name_list):
        # 可选步骤：变更标的
        #if not hasattr(self,'flag'):  #如果没有flag，加一个flag
        #    self.flag = False
        #if self.flag == False:  #如果flag==False ，变更股票池，变更的股票池内容自定义，如何设计flag==False也自定义
        #    sub_stocks = security_list.copy()
        #    self.change_stocks(sub_stocks)
        #    self.flag == True
        #    print('Stock Pool Change Successful')

        # 计算步骤：计算因子数据，并返回因子数据的DataFrame
        Concept_Result={}
        for factor in factor_list:
            result_list = []
            for stock in df_dict.keys():
                if type(df_dict[stock]) == dict:
                    Tmp_series = df_dict[stock]['kline1m']
                    New_Time = Tmp_series.iloc[-1:, :]
                    try:
                        if 'KLineCategory' not in Tmp_series.columns:
                            Tmp_series = New_Time.copy()
                        else:
                            Tmp_series=Tmp_series[Tmp_series['KLineCategory']==11.0]
                            Tmp_series=pd.concat([Tmp_series,New_Time])
                        Tmp_series = Tmp_series.set_index('MDTime')[factor]
                        Tmp_series = Tmp_series.groupby(Tmp_series.index).first()
                        Tmp_series.rename(stock, inplace=True)
                        result_list.append(Tmp_series)
                    except:
                        print(stock+'可能存在停牌，无成交量等问题，具体可以查看个股')
                else:
                    pass

            calc_df = pd.concat(result_list, axis=1)
            calc_df.index = (calc_df.index / 100000).astype(int)

            if ((factor == 'ClosePx') or (factor == 'HighPx') or (factor == 'LowPx') or (factor == 'OpenPx') or (factor == 'TotalValueTrade')):
                calc_df = calc_df / 10000
            elif (factor == 'TotalVolumeTrade'):
                calc_df = calc_df / 100

            if (int(datetime.datetime.now().strftime('%H%M'))<930) or (int(datetime.datetime.now().strftime('%H%M'))>=1500):
                calc_df = calc_df.groupby('MDTime').last()
            ## 把因子值和对应结果赋值
            Concept_Result[factor]=calc_df

        factor_name = name_list.loc[self.worker_no, 'name_list']
        now_time = datetime.datetime.now().strftime('%H%M%S')
        if int(now_time)<=150000:
            with open(save_path + date + '/' + factor_name+'/'+ now_time + '.pkl', 'wb') as f:
                pickle.dump(Concept_Result,f)

            print('finish calculation! now mdtime{}!'.format(df_dict['kline1m']['MDTime'].iloc[-1]))
        else:
            print('timeout after market:{}!'.format(now_time))

        return None

    #（1）选择alram+realtime模式范例：playback_or_realtime="realtime"
    run_realtime_calculation_by_securities(data_input_account="USERXQUANT01", data_input_mode=["KLine1M_RAW"],
                                           security_list=security_list,
                                           security_type="stock", calculation_mode="alarm",
                                           tick_sample_interval = 3,
                                           playback_or_realtime="realtime",options={"local_mode": False},
                                           calc_callback=calc_callback, verbose=0)


#concept_num=int(AIMR.getParam()) #获取第几个进程
concept_num=1
#股票池
Conept_AllStock = pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=0 ,index_col=0).iloc[:, :3]
Conept_DelStock = set(pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=1 ,index_col=0)['子主题名称'].dropna())
concept_list=[]
for concept in sorted(list(set(Conept_AllStock['子主题']))):
    if len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))>=50:
        pass
        #print(concept + '板块中个股数量超过50个，数量过多暂不计算')
    elif len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))<=5:
        pass
        #print(concept + '板块中个股数量低于5个，数量过少暂不计算')
    elif concept in Conept_DelStock:
        pass
        #print(concept+'属于不监控板块，暂不计算')
    else:
        concept_list.append(concept)

concept_list = sorted(concept_list)

choice_num = int(len(concept_list)/4)+1

concept_name = concept_list[choice_num*(concept_num-1):choice_num*concept_num]

send_message(users,'该进程进程包含'+str(len(concept_name))+'个板块：'+str(list(concept_name)))
Get_RealTime_Data(concept_name)

