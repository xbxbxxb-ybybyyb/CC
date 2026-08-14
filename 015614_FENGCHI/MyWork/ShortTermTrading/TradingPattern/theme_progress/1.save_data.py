import numpy as np
import pandas as pd
from tqdm import tqdm

from ShortTermTrading.ConceptApi import ConceptApi
from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values, get_concept_values, Get_Concept_Code
from ShortTermTrading.dataApi import getData
from xquant.factordata import FactorData


########把2019.1-2020.12.4的数据储存一下#############
class Save_Data(object):
    ###获取基础数据###
    def __init__(self, start_date, end_date, read_path='/data/group/800319/Daily_ConCept/RawData/BasicData/'):
        self.read_path = read_path
        date_list = getData.get_date_range(start_date, end_date)
        fd = FactorData()
        self.start_date = date_list[0]
        self.end_date = end_date
        self.date_list = date_list

        date_list1 = getData.get_date_range(20120101, end_date)
        date_list1 = date_list1[date_list1.index(self.start_date) - 30:]
        start_date = date_list1[0]
        self.date_list1 = date_list1
        # ##指数数据##
        # Index_close = getData.get_daily_1factor('close', type='bench')[['SZZZ', 'CYBZ']].loc[date_list1]
        # 使用WIND全A
        Index_close = fd.get_factor_value('WIND_AIndexWindIndustriesEOD',
                                          factors=['TRADE_DT', 'S_DQ_CLOSE'],
                                          trade_dt=['>=20120101', '<=20201231'],
                                          s_info_windcode=['881001.WI']).set_index('TRADE_DT').sort_index()
        Index_close.index = Index_close.index.map(int)
        Index_close = Index_close.loc[date_list1]
        Index_pct = Index_close.pct_change().loc[date_list] * 100
        Index_Min = getData.get_minute_1factor('close', type='bench')[['SZZZ', 'CYBZ']].loc[start_date:end_date]
        Index_Min.fillna(method='ffill', inplace=True)
        Index_pre_close = getData.get_daily_1factor('close', type='bench')[['SZZZ', 'CYBZ']].shift(1).loc[
                          start_date:end_date]
        Index_pct_min = pd.DataFrame(np.array(Index_pre_close.loc[Index_Min.index.get_level_values('date')]),
                                     index=Index_Min.index, columns=Index_pre_close.columns)
        Index_pct_min = (Index_Min / Index_pct_min - 1).dropna(how='all')
        ##分钟数据##
        min_close = getData.get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date).dropna(
            how='all', axis=1)
        min_close.fillna(method='ffill', inplace=True)
        min_amt = getData.get_minute_1factor('amt', start_datetime=start_date, end_datetime=end_date).dropna(how='all',
                                                                                                             axis=1)
        min_vol = getData.get_minute_1factor('vol', start_datetime=start_date, end_datetime=end_date).dropna(how='all',
                                                                                                             axis=1)
        ##个股数据##
        close = getData.get_daily_1factor('close', date_list=date_list).dropna(how='all', axis=1)
        high = getData.get_daily_1factor('high', date_list=date_list).dropna(how='all', axis=1)
        low = getData.get_daily_1factor('low', date_list=date_list).dropna(how='all', axis=1)
        pre_close = getData.get_daily_1factor('pre_close', date_list=date_list).dropna(how='all', axis=1)
        turn = getData.get_daily_1factor('free_turn', date_list=date_list).dropna(how='all', axis=1)
        amt = getData.get_daily_1factor('amt', date_list=date_list1).dropna(how='all', axis=1)
        Stock_Pct = getData.get_daily_1factor('pct_chg', date_list=date_list)
        close_adj = getData.get_daily_1factor('close_badj', date_list=date_list).dropna(how='all', axis=1)
        high_adj = getData.get_daily_1factor('high_badj', date_list=date_list).dropna(how='all', axis=1)

        pre_close_inday = pd.DataFrame(np.array(pre_close.loc[min_close.index.get_level_values('date')]),
                                       index=min_close.index, columns=pre_close.columns)
        self.Stock_Pct = Stock_Pct
        self.Index_pct = Index_pct
        self.Index_close = Index_close
        self.close = close
        self.high = high
        self.low = low
        self.pre_close = pre_close
        self.turn = turn
        self.amt = amt
        self.close_adj = close_adj
        self.high_adj = high_adj

        self.Index_Min = Index_Min
        self.Index_pre_close = Index_pre_close
        self.Index_pct_min = Index_pct_min  # 日内累计涨跌幅

        self.min_close = min_close
        self.min_amt = min_amt
        self.min_vol = min_vol
        self.pre_close_inday = pre_close_inday

        #########读取已经写好的日间数据#############
        stock_pool = ConceptApi.get_basic_values('stock_pool', start_date=start_date, end_date=end_date,
                                                 read_path=read_path)  # 股票池
        Limit_stock = ConceptApi.get_basic_values('Limit_stock', start_date=start_date, end_date=end_date,
                                                  read_path=read_path)  # 涨停个股
        Dragon_Stock = ConceptApi.get_basic_values('Dragon_Stock', start_date=start_date, end_date=end_date,
                                                   read_path=read_path)  # 全市场龙头股

        self.stock_pool = stock_pool
        self.Limit_stock = Limit_stock & stock_pool & stock_pool.shift(-1)
        self.Dragon_Stock = Dragon_Stock & stock_pool & stock_pool.shift(-1)

        ########读取已经写好的日内数据#################
        Limit_stock_inday = ConceptApi.get_minute_values('Limit_stock_inday', start_date=start_date, end_date=end_date,
                                                         read_path=read_path)  # 个股日内涨停情况
        Limit_High_min = ConceptApi.get_minute_values('Limit_High_min', start_date=start_date, end_date=end_date,
                                                      read_path=read_path)  # 个股日内最高连板情况

        self.Limit_stock_inday = Limit_stock_inday
        self.Limit_High_min = Limit_High_min

        ######日内分钟涨幅#####################
        # Quick_up=np.fmax(self.min_close.pct_change(1),self.min_close.pct_change(2))
        # Quick_up = np.fmax(Quick_up, self.min_close.pct_change(3))
        # Quick_up = np.fmax(Quick_up, self.min_close.pct_change(4))
        # Quick_up = np.fmax(Quick_up, self.min_close.pct_change(5))
        # Quick_up = self.min_close.pct_change(3)
        # self.Quick_up = Quick_up

        ######需要剔除的板块######
        basic_values = get_basic_values('Active_Concept')
        concept = Get_Concept_Code()
        concept_dict = concept.to_dict()['S_INFO_NAME']
        reverse_concept_dict = dict((value,key) for key,value in concept_dict.items())

        apart_concept_df = pd.read_excel('/data/group/800319/fengchi/pattern_test/temp_data/概念筛选-20210106.xlsx', sheet_name='Sheet1')
        self.apart_concept_list = apart_concept_df['Name'].tolist()
        self.apart_concept_list.remove('次新股指数')
        self.apart_concept_list = list(map(lambda x: reverse_concept_dict[x], self.apart_concept_list))

    def get_every_concept_list(self, concept_num_df, date):
        s = concept_num_df.loc[date]
        small_list = s[(5 <= s) & (s <= 10)].index.tolist()
        middle_list = s[(11 <= s) & (s <= 30)].index.tolist()
        big_list = s[s > 30].index.tolist()
        return small_list, middle_list, big_list

    def judge_concept_pct(self, date, concept, concept_pct_df, concept_list):
        if concept in concept_pct_df.loc[date][concept_list].sort_values(ascending=False)[:int(0.1*len(concept_list))].index.tolist():
            return True
        else:
            return False

    ###获取主流板块和活跃个股###
    def get_Active_concept(self, save_path='/data/user/fengchi/首阴反包/'):
        ###获取概念板块数量和日收益率###
        Concept_num = get_basic_values('Concept_num', self.start_date, self.end_date, self.read_path)
        Concept_Pct = get_basic_values('Concept_Pct', self.start_date, self.end_date, self.read_path)
        Concept_Close = get_basic_values('Concept_Close', self.start_date, self.end_date, self.read_path)  # 收盘价
        Concept_Pct.dropna(how='all', axis=1, inplace=True)
        concept_list = Concept_Pct.columns.to_list()
        concept_list = list(set(concept_list).difference(set(self.apart_concept_list)))

        self.Concept_num = Concept_num
        self.Concept_Pct = Concept_Pct
        self.Concept_Close = Concept_Close

        ###每日活跃概念筛选：即不需要排序###
        def Cal_Concept_Active(concept, date_list=self.date_list1, cal_date_range=self.date_list,
                               Concept_num=Concept_num, Concept_Pct=Concept_Pct,
                               stock_pool=self.stock_pool, Stock_Pct=self.Stock_Pct, Limit_stock=self.Limit_stock):
            Active_Concept = pd.DataFrame(False, index=cal_date_range, columns=[concept])
            for date in cal_date_range:
                small_list, middle_list, big_list = self.get_every_concept_list(Concept_num, date)
                Num = Concept_num.loc[date, concept]
                if ((Num >= 5) & (Num <= 10)):  ##如果是小版块##
                    ##先判断板块整体涨跌幅是不是大于4
                    if Concept_Pct.loc[date, concept] >= 3.5:
                        if not self.judge_concept_pct(date, concept, Concept_Pct, small_list):
                            continue
                        ##再判断板块是不是有超额##
                        if Concept_Pct.loc[date, concept] - self.Index_pct.loc[date, 'S_DQ_CLOSE'] >= 1:
                            ##再判断当天个股涨幅是否达到要求##
                            concept_stock = get_concept_values('Concept_StockList', concept, date, date).loc[date]
                            concept_stock = concept_stock[concept_stock == True].index.to_list()
                            concept_stock = list(set(concept_stock).intersection(
                                set(stock_pool.loc[date][stock_pool.loc[date] == True].index.to_list())))
                            stock_pct_today = Stock_Pct.loc[date, concept_stock]  ##当天该概念:去掉ST，全部个股的涨跌幅###
                            Limit_stock_today = Limit_stock.loc[date, concept_stock]
                            ######至少有2只个股涨幅大于5%，且至少有1只个股涨停####
                            if (((stock_pct_today >= 5).sum() > 2) & (Limit_stock_today.sum() >= 1)):
                                #######板块内近20天累计最高一板不放进来########
                                stock_pct_today = (
                                    Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock])
                                if (stock_pct_today).sum().sum() > 1:
                                    Active_Concept.loc[date, concept] = True
                elif ((Num >= 11) & (Num <= 30)):
                    ##先判断板块整体涨跌幅是不是大于3
                    if Concept_Pct.loc[date, concept] >= 2.5:
                        if not self.judge_concept_pct(date, concept, Concept_Pct, middle_list):
                            continue
                        ##再判断板块是不是有超额##
                        if Concept_Pct.loc[date, concept] - self.Index_pct.loc[date, 'S_DQ_CLOSE'] >= 0.5:
                            ##再判断当天个股涨幅是否达到要求##
                            concept_stock = get_concept_values('Concept_StockList', concept, date, date).loc[date]
                            concept_stock = concept_stock[concept_stock == True].index.to_list()
                            concept_stock = list(set(concept_stock).intersection(
                                set(stock_pool.loc[date][stock_pool.loc[date] == True].index.to_list())))
                            ######获取前30%个股的涨幅########
                            stock_pct_today = Stock_Pct.loc[date, concept_stock]  ##当天该概念:去掉ST，全部个股的涨跌幅###
                            stock_pct_today = stock_pct_today.sort_values(ascending=False).iloc[
                                              :int(round(len(stock_pct_today) * 0.3, ))]
                            ######前30%个股平均涨幅大于5%，且至少有1只个股涨停####
                            if ((stock_pct_today.mean() >= 4) & (
                                    Limit_stock.loc[date, stock_pct_today.index].sum() >= 1)):
                                #######板块内近20天累计最高需要大于1扳，或者当日涨停数量########
                                stock_pct_today = (
                                    Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock])
                                if (stock_pct_today).sum().sum() > 1:
                                    Active_Concept.loc[date, concept] = True
                elif (Num > 30):
                    ##先判断板块整体涨跌幅是不是大于1.5
                    if Concept_Pct.loc[date, concept] > 1.5:
                        if not self.judge_concept_pct(date, concept, Concept_Pct, big_list):
                            continue
                        ##再判断板块是不是有超额##
                        if Concept_Pct.loc[date, concept] - self.Index_pct.loc[date, 'S_DQ_CLOSE'] >= 0:
                            ##再判断当天个股涨幅是否达到要求##
                            concept_stock = get_concept_values('Concept_StockList', concept, date, date).loc[date]
                            concept_stock = concept_stock[concept_stock == True].index.to_list()
                            concept_stock = list(set(concept_stock).intersection(
                                set(stock_pool.loc[date][stock_pool.loc[date] == True].index.to_list())))
                            ######获取前30%个股的涨幅########
                            stock_pct_today = Stock_Pct.loc[date, concept_stock]  ##当天该概念:去掉ST，全部个股的涨跌幅###
                            stock_pct_today = stock_pct_today.sort_values(ascending=False).iloc[
                                              :int(round(len(stock_pct_today) * 0.2, ))]
                            ######前30%个股平均涨幅大于4%，且至少有2只个股涨停####
                            if ((stock_pct_today.mean() >= 4) & (
                                    Limit_stock.loc[date, stock_pct_today.index].sum() >= 1)):
                                #######板块内近20天累计最高一板不放进来########
                                stock_pct_today = (
                                    Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock])
                                if (stock_pct_today).sum().sum() > 2:
                                    Active_Concept.loc[date, concept] = True
            return Active_Concept

        Active_concept = []
        for concept in tqdm(concept_list):
            Result = Cal_Concept_Active(concept)
            Active_concept.append(Result)
        Active_concept = pd.concat(Active_concept, axis=1)
        #########1、选概念板块日间筛选：只要有一天活跃过############
        Active_concept = Active_concept.rolling(10).sum() >= 1
        #######对于每一个概念板块：如果纳入日期小于该日期，则该板块变为False#######
        Concept_Choice_Date = ConceptApi.Get_Concept_Time(Active_concept.columns.to_list())
        Concept_Update_time = pd.DataFrame(False, index=Active_concept.index, columns=Active_concept.columns)
        for concept in Active_concept.columns:
            concept_start_date = Concept_Choice_Date.loc[concept, 'S_INFO_LISTDATE']
            concept_end_date = Concept_Choice_Date.loc[concept, 'EXPIRE_DATE']
            Concept_Update_time.loc[concept_start_date:concept_end_date, concept] = True

        Active_concept = (Active_concept & Concept_Update_time)
        Active_concept = Active_concept[Active_concept.sum()[Active_concept.sum() > 0].index]
        self.Active_concept = Active_concept  # 活跃板块
        self.Active_concept.to_hdf(save_path + 'Active_concept.h5', key='Active_concept', format='t') # 每天的活跃概念
        print('Active_concept储存完成')

        Active_concept = pd.read_hdf(save_path + 'Active_concept.h5', key='Active_concept')
        self.Active_concept = Active_concept

        #####获取板块内的所有个股#########
        begin_date = Active_concept.index[0]
        stop_date = Active_concept.index[-1]
        Active_Stock = pd.DataFrame(False, index=self.date_list, columns=self.stock_pool.columns)

        stk_list = Active_Stock.columns.tolist()
        pct_chg = getData.get_daily_1factor('pct_chg', date_list=self.date_list, code_list=stk_list)
        pct_chg_judge = pct_chg > 0

        concept_pct = get_basic_values(factor='Concept_Pct', start_date=begin_date, end_date=stop_date)
        for concept in tqdm(Active_concept.columns):
            concept_choice = Active_concept[concept]
            concept_stock = get_concept_values('Concept_StockList', concept, begin_date, stop_date)
            concept_stock.loc[concept_choice[concept_choice == False].index] = False
            tmp_concept_pct = concept_pct[concept]
            concept_alpha = pct_chg.sub(tmp_concept_pct, axis=0)
            concept_alpha_judge = concept_alpha > 0
            # Active_Stock = (Active_Stock | concept_stock)

            # concept_stock计算
            # 个股涨跌幅大于0， 超额大于0
            res_concept_stock = concept_stock & pct_chg_judge
            res_concept_stock = res_concept_stock & concept_alpha_judge
            res_concept_stock.to_hdf(save_path + 'Active_stock.h5', key=concept, format='t') # 每一个概念里的active_stock


start_date = 20140101 # 最早可从20140101开始算起
end_date = 20201231
sd = Save_Data(start_date, end_date)
sd.get_Active_concept(save_path='/data/user/fengchi/首阴反包_WIND全A/')