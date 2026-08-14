from realtimeApi.getdata_from_open import *

# 注意：统计数据和同花顺数据存在差别，同花顺数据中931分表示的是930-931数据，而我们的时间窗口930表示的是930-931数据
# 1、盘前数据获取
date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
concept_Num = get_concept_num()

# 2、获取一个板块的多个因子值
factor_list = ['ClosePx','HighPx','TotalVolumeTrade','TotalValueTrade']
factor_result = get_oneconcept_alldata(concept_name='石化油服',factor_list=None)

# 3、获取多个板块的一个因子值
concept_list=['其他机械','保险','二胎','钢铁']
close = get_allconcept_onedata(factor='ClosePx',concept_list=None)

# 4、获取板块数据
# 可用的factor有['Pct_Change','Max_Num','Min_Num','MaxNumFromOpen','MinNumFromOpen','UpNum_2','DownNum_-2,'TotalVolumeTrade','TotalValueTrade']
concept_result = get_concept_value(factor = 'TotalVolumeTrade',concept_list=None)



#判断一下时间滞后性
date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
save_path = '/data/group/800319/RealTime_Data/'+ date + '/'
pkl_list = concept_Num.index.to_list()

while int(datetime.datetime.now().strftime('%H%M'))<1500:
    for concept in pkl_list:
        now_time = (datetime.datetime.now().strftime('%H%M%S'))
        hour_min = int(now_time[:4])

        result = pd.read_pickle(save_path+concept+'.pkl')
        result[list(result.keys())[0]].index[-1]

        if result[list(result.keys())[0]].index[-1]!=hour_min:
            print(now_time + ' ' +concept+'数据更新不及时',result[list(result.keys())[0]].index[-1])

    time.sleep(1)



