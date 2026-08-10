import pandas as pd
from multifactor.IO import IO
import datetime
from multifactor.utility.dt import *
from math import ceil


class HS300IndexWareHousing:

    def __init__(self, time, evaluate_result = False, start_time = None, end_time = None, old_index_stock_list=[]):
        self.time = time # 这一期的调仓时间
        self.evaluate_result = evaluate_result # 是否评估结果，在历史测试的时候用
        self.start_time = start_time # 考察期开始时间
        self.end_time = end_time # 考察期结束时间
        self.old_index_stock_list = old_index_stock_list # 目前的老指数样本

    # 获取考察期时间，以及停牌三个月的阈值时间
    def get_time_info(self, time):
        if time % 10 == 6:
            start_time = (time // 100 - 1) * 10000 + 501
            end_time = time // 100 * 10000 + 430
        elif time % 10 == 2:
            start_time = (time // 100 - 1) * 10000 + 1101
            end_time = time // 100 * 10000 + 1031
        else:
            print('请检查调仓时间是否为6月或是12月！')
        suspend_threshold_time = self.get_str_time(end_time - 300) # 停牌超过3个月的复牌要满三个月，这个是判断复牌是否满三个月的阈值时间
        return start_time, end_time, suspend_threshold_time

    # 获取昨天的时间，在读数据时使用，但是晚上运行时因为当天数据库更新的原因，如果读不出来数据请将时间手动改为今天日期
    def getYesterday(self):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        # return 20190904
        return int(str(yesterday)[:4] + str(yesterday)[5:7] + str(yesterday)[8:])

    # 转变日期格式 20180101 转变为 ‘2018-01-01’
    def get_str_time(self, mytime):
        return str(mytime)[:4] + '-' + str(mytime)[4:6] + '-' + str(mytime)[6:8]

    # 查找指定日期的指数成分股 返回list ， 获取老样本时使用
    def find_index_stock_by_time(self, time):
        tradeday = str(get_trading_date_range(time - 10, time)[-1])
        tradeday = int(tradeday[:4] + tradeday[5:7] + tradeday[8:10])
        df = IO.read_data(tradeday, alt='/data/group/800080/warehouse/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
        df = df.reset_index()
        return df[df.index_300 == True]['Ticker'].unique().tolist()

    # 获取数据
    def get_data(self):
        # 获取A股基本信息
        data1 = IO.read_data([20070101, self.end_time], columns=['amt', 'mkt_cap_ard', 'close'],
                             alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        data1 = data1.reset_index()
        data1 = data1.dropna(subset=['amt', 'mkt_cap_ard'])

        # 获取A股合计
        df3 = IO.read_data(self.getYesterday(),
                           columns=['dt', 'Ticker', 'CHANGE_DT', 'S_SHARE_TOTALA', 'FLOAT_B_SHR', 'FLOAT_H_SHR'],
                           alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCapitalization/AShareCapitalization.h5')
        df3 = df3.reset_index()

        df3 = df3.rename(columns={'dt': 'time'})

        # 转变时间格式
        def changetime(a):
            a = str(a)
            return a[:4] + '-' + a[4:6] + '-' + a[6:8]

        df3['dt'] = df3['CHANGE_DT'].apply(lambda x: changetime(x))

        def changetime2(a):
            return str(a)[:10]

        data1['dt'] = data1['dt'].apply(lambda x: changetime2(x))

        # 将以上两个表合并
        totaldata = pd.merge(data1, df3, on=['Ticker', 'dt'], how='left')
        totaldata['S_SHARE_TOTALA'] = totaldata.groupby('Ticker')['S_SHARE_TOTALA'].fillna(method='ffill')
        totaldata = totaldata[totaldata.dt >= self.get_str_time(self.start_time)]
        totaldata = totaldata[totaldata.dt <= self.get_str_time(self.end_time)]

        totaldata.drop(['time', 'CHANGE_DT', 'FLOAT_B_SHR', 'FLOAT_H_SHR'], axis=1, inplace=True)
        # 计算A股总市值，用close价格*A股股本数量
        totaldata['zongshizhi'] = totaldata.close * totaldata.S_SHARE_TOTALA
        totaldata.loc[totaldata['zongshizhi'].isnull(), 'zongshizhi'] = totaldata[totaldata['zongshizhi'].isnull()][
            'mkt_cap_ard']

        data = totaldata.rename(columns={'amt': 'S_DQ_AMOUNT', 'zongshizhi': 'S_VAL_MV'})
        data = data.reset_index()
        print('get_data', data.shape)
        return data

    # 样本空间会在考核区间最后一天的股票中产生
    def select_stock_in_finalday(self, data):
        time_last_day = data.iloc[-1]['dt']
        # 取出最后一天的股票列表，样本空间将从中取出，数据中不在此列表中的股票将被删掉
        final_stock_list = data[data.dt == time_last_day].Ticker.tolist()
        # 全部的股票
        total_stock_list = data.Ticker.unique().tolist()
        # 取差集 需要剔除的股票
        res_stock_list_lastday = list(set(total_stock_list) - set(final_stock_list))
        data = data[~data['Ticker'].isin(res_stock_list_lastday)]
        print('select_stock_in_finalday', data.shape)
        return data

    # 剔除重大事件股票 ST *ST 暂停上市
    def delete_ST(self, data):
        # 检测股票目前是否处于特殊处理状态
        def inST(time1, time2):
            time1 = float(str(time1)[:10])
            time2 = float(str(time2)[:10])
            new_time_last_day = float(str(data.iloc[-1]['dt'])[:10].replace('-', ''))
            if new_time_last_day >= time2:
                return False
            elif np.isnan(time2) and new_time_last_day >= time1:
                return True
            elif (new_time_last_day >= time1) and (new_time_last_day <= time2):
                return True
            else:
                return False

        # 读取A股重大事件表，了解A股特别处理信息
        stock_AShareST = IO.read_data(self.getYesterday(), alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5')

        stock_AShareST['isST'] = stock_AShareST.apply(lambda x: inST(x.ENTRY_DT, x.REMOVE_DT), axis=1)
        stock_AShareST = stock_AShareST.reset_index()
        STstock_list = stock_AShareST[stock_AShareST.isST == True].Ticker.tolist()
        final_stock_list = data[data.dt == str(data.iloc[-1]['dt'])[:10]].Ticker.tolist()
        delete_STstock_list = list(set(STstock_list) & set(final_stock_list))
        data = data.drop(data.loc[(data['Ticker'].isin(delete_STstock_list))].index)
        print('delete_ST', data.shape)
        return data

    # 上市不满三年的创业板股票要删掉
    def select_GEM_stock(self, data):
        # 检测是否为创业板股票
        def isGEM_func(stock_code):
            if stock_code[:3] == '300':
                return True
            else:
                return False

        data['isGEM'] = data['Ticker'].apply(lambda x: isGEM_func(x))
        # 创业板股票列表
        GEMstock_list = data[data.isGEM == True].Ticker.unique().tolist()

        global stock_description
        # 读取A股基本信息表 获取每支股票上市时间
        stock_description = IO.read_data(self.getYesterday(),
                                         alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')

        # 挑选出目前所有创业板股票信息 包括股票代码 所属板块 上市日期
        stock_description = stock_description.reset_index()
        GEMstock_description = stock_description[stock_description.S_INFO_LISTBOARD == 434001000]
        GEMstock_description = GEMstock_description[['Ticker', 'S_INFO_LISTBOARD', 'S_INFO_LISTDATE']]

        # 得到样本空间内所有创业板股票上市时间信息
        # GEMstock_description = GEMstock_description.drop(GEMstock_description.loc[(~GEMstock_description['Ticker'].isin(GEMstock_list))].index)
        GEMstock_description = GEMstock_description[GEMstock_description.Ticker.isin(GEMstock_list)]
        # 创业板需要上市三年
        time_last_day = float(str(data.iloc[-1]['dt'])[:10].replace('-', ''))
        GEM_time_sign = time_last_day - 30000

        # 不满三年的创业板股票列表后续删除    等等要删掉
        delete_GEMstock = GEMstock_description[
            GEMstock_description.S_INFO_LISTDATE > GEM_time_sign].Ticker.unique().tolist()

        data = data.drop(data.loc[(data['Ticker'].isin(delete_GEMstock))].index)
        print('select_GEM_stock', data.shape)
        return data

    # 对于非创业板股票要上市满三个月，否则上市以来日均市值要在所有非创业板股票中排前30名
    def select_noGEM_stock(self, data):
        # 样本空间内非创业板股票列表
        no_GEMstock_list = data[data.isGEM == False].Ticker.unique().tolist()

        # 所有A股中非创业板股票
        no_GEMstock_description = stock_description[stock_description.S_INFO_LISTBOARD != 434001000]

        # 非创业板股票要上市超过一个季度，除非一些特殊情况，找出一个季度前的时间节点，
        # 因都在年中进行考核，不会出现一个季度前需要计算到上一年的情况，因此这里没有考虑月份进位
        time_last_day = float(str(data.iloc[-1]['dt'])[:10].replace('-', ''))

        if self.end_time % 10 == 6:
            no_GEM_time_sign = self.end_time - 229
        else:
            no_GEM_time_sign = self.end_time - 230

        # 得到样本空间内所有   非创业板   股票上市时间信息
        # no_GEMstock_description = no_GEMstock_description.drop(no_GEMstock_description.loc[(~no_GEMstock_description['Ticker'].isin(no_GEMstock_list))].index)
        no_GEMstock_description = no_GEMstock_description[no_GEMstock_description['Ticker'].isin(no_GEMstock_list)]
        no_GEMstock_description = no_GEMstock_description[['Ticker', 'S_INFO_LISTBOARD', 'S_INFO_LISTDATE']]

        # 上市不满一个季度的 非创业板股票列表后续做特殊处理
        delete_no_GEMstock = no_GEMstock_description[
            no_GEMstock_description.S_INFO_LISTDATE > no_GEM_time_sign].Ticker.unique().tolist()

        # 目前样本空间内非创业板股票
        no_GEM_stock_data = data[data.isGEM == False]

        data.drop(['isGEM'], axis=1, inplace=True)

        # 非创业板股票的日均总市值
        no_GEM_stock_data = no_GEM_stock_data[no_GEM_stock_data.S_DQ_AMOUNT != 0]
        no_GEM_stock_daily_MarketCap = no_GEM_stock_data.groupby('Ticker')['S_VAL_MV'].mean().to_frame()

        # 获取前30名日均市值最高的非创业板股票
        top30_stock_daily_MarketCap_list = no_GEM_stock_daily_MarketCap.sort_values('S_VAL_MV', ascending=False)[
                                           :30].reset_index().Ticker.tolist()

        # 最终删掉上市既不满一个季度，又日均总市值不在非创业板股票前30名的股票
        final_delete_no_GEMstock = list(set(delete_no_GEMstock) - set(top30_stock_daily_MarketCap_list))

        data = data.drop(data.loc[(data['Ticker'].isin(final_delete_no_GEMstock))].index)
        print('select_noGEM_stock', data.shape)
        return data

    # 从基础数据里选出样本空间
    def get_Sample_Space(self, data):
        data = self.select_stock_in_finalday(data)
        data = self.delete_ST(data)
        data = self.select_GEM_stock(data)
        data = self.select_noGEM_stock(data)
        return data

    # 删除新股前三个交易日
    def drop_top3days_for_new_stock(self, data):
        # 寻找上市不满一年的股
        new_stock = data.groupby('Ticker').size().sort_values(ascending=False).to_frame()
        new_stock = new_stock.reset_index()
        new_stock.rename(columns={0: 'days'}, inplace=True)

        # 找出其中上市时间最长的股票，少于这个时间的为新股
        max_days = new_stock.iloc[0]['days']
        # 上市不满一年的股票
        new_stock_list = new_stock[new_stock.days < max_days].Ticker.tolist()

        # 删除掉每个新股前三个交易日的数据
        data = data.drop(data[(data.Ticker.isin(new_stock_list))].groupby('Ticker').head(3).index)
        return data

    # 日均成交额进行排序，获得下一步日均总市值排序的样本
    def sort_average_daily_turnover(self, data, drop1_old_out_samplespace_list):
        # 先将停牌的日子都删掉
        data_drop0 = data.drop(data[data.S_DQ_AMOUNT == 0].index)
        average_daily_turnover = data_drop0.groupby('Ticker')['S_DQ_AMOUNT', 'S_VAL_MV'].mean().reset_index()
        average_daily_turnover = average_daily_turnover.sort_values('S_DQ_AMOUNT', ascending=False).reset_index()
        top50_average_daily_turnover = average_daily_turnover[: average_daily_turnover.shape[0] // 2]
        top50_daily_turnover_list = top50_average_daily_turnover.Ticker.tolist()
        # 第二优先删除日均成交额排名后50%的老样本
        drop2_old_out_top50_daily_turnover_list = list(
            set(self.old_index_stock_list) - set(top50_daily_turnover_list) - set(drop1_old_out_samplespace_list))

        # 如果指数老样本日均成交金额在样本空间中排名前60%，则参与下一步总市值的排名
        top50_to_60_stock_list = average_daily_turnover[average_daily_turnover.shape[0] // 2: int(
            average_daily_turnover.shape[0] * 0.6)].Ticker.tolist()

        old_index_stock_in_top50_60_list = list(set(top50_to_60_stock_list) & set(self.old_index_stock_list))
        old_index_stock_in_top50_60_df = average_daily_turnover[
            average_daily_turnover.Ticker.isin(old_index_stock_in_top50_60_list)]
        top50_and60_average_daily_turnover = top50_average_daily_turnover.append(old_index_stock_in_top50_60_df)

        return top50_and60_average_daily_turnover, drop2_old_out_top50_daily_turnover_list, top50_daily_turnover_list

    # 总市值排序
    def sort_average_daily_mkt(self, top50_and60_average_daily_turnover, top50_daily_turnover_list):
        sort_average_daily_MarketCap = top50_and60_average_daily_turnover.sort_values('S_VAL_MV',
                                                                                      ascending=False).reset_index()

        # 排名在前240名的新股优先进入指数，排名在前360名的老样本优先保留
        top240_average_daily_MarketCap = sort_average_daily_MarketCap[: 240]
        top300_average_daily_MarketCap = sort_average_daily_MarketCap[: 300]
        top240_360_average_daily_MarketCap = sort_average_daily_MarketCap[240: 360]
        top240_300_average_daily_MarketCap = sort_average_daily_MarketCap[240: 300]
        out360_average_daily_MarketCap = sort_average_daily_MarketCap[360:]

        top360_average_daily_MarketCap = sort_average_daily_MarketCap[: 360]
        top360_new_stock_list = list(set(top360_average_daily_MarketCap.Ticker.tolist()) - set(self.old_index_stock_list))
        top240_360_new_stock_average_daily_MarketCap = top240_360_average_daily_MarketCap[
            ~top240_360_average_daily_MarketCap.Ticker.isin(self.old_index_stock_list)]

        allnew_stock_list = list(set(sort_average_daily_MarketCap.Ticker.tolist()) - set(self.old_index_stock_list))

        out360_old_stock_average_daily_MarketCap = out360_average_daily_MarketCap[
            out360_average_daily_MarketCap.Ticker.isin(self.old_index_stock_list)]
        top240_360_old_stock_average_daily_MarketCap = top240_360_average_daily_MarketCap[
            top240_360_average_daily_MarketCap.Ticker.isin(self.old_index_stock_list)]
        old_out_top360_MarketCap_list = list(
            set(sort_average_daily_MarketCap[360:].Ticker.tolist()) & set(self.old_index_stock_list))

        # 前240名保留 240~360之间的老样本 240~ 360之间的新样本 其他股票 应用缓冲区规则重新排序
        new_average_daily_MarketCap = top240_average_daily_MarketCap.append(
            top240_360_old_stock_average_daily_MarketCap).append(top240_360_new_stock_average_daily_MarketCap).append(
            out360_average_daily_MarketCap)

        # 删除总市值排名300名之后的违规的老样本
        drop3_old_out_top300_daily_MarketCap_list = list(
            set(self.old_index_stock_list) & set(sort_average_daily_MarketCap[300:].Ticker.tolist()))
        drop4_top50amt_out360mkt_list = list(
            set(top50_daily_turnover_list) & set(self.old_index_stock_list) & set(old_out_top360_MarketCap_list))

        return new_average_daily_MarketCap, drop3_old_out_top300_daily_MarketCap_list, drop4_top50amt_out360mkt_list, sort_average_daily_MarketCap

    # 剔除证监会处罚的公司
    def drop_illegality(self, drop3_old_out_top300_daily_MarketCap_list):
        asi = IO.read_data([self.start_time, self.end_time],
                           alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIllegality/AShareIllegality.h5')
        asi = asi.reset_index()

        def judge_Processor(str1):
            return 1 if str1.find('中国证券监督管理委员会') >= 0 else 0

        def judge_DISPOSAL_TYPE(str1):
            return 1 if str1.find('处罚') >= 0 or str1.find('其他') >= 0 else 0

        asi['judge_Processor'] = asi.PROCESSOR.apply(lambda x: judge_Processor(x))
        asi['judge_disposal'] = asi.DISPOSAL_TYPE.apply(lambda x: judge_DISPOSAL_TYPE(x))
        asi = asi[asi.judge_Processor == 1]
        asi = asi[asi.judge_disposal == 1]

        def judge_ILLEG_TYPE(str1):
            return 1 if str1.find('未及时披露公司重大事项') >= 0 or str1.find('信息披露虚假或严重误导性陈述') >= 0 else 0

        def judge_RELATION_TYPE(str1):
            return 1 if str1 == 458001000 else 0

        asi['judge_ILLEG_TYPE'] = asi.ILLEG_TYPE.apply(lambda x: judge_ILLEG_TYPE(x))
        asi['judge_RELATION_TYPE'] = asi.RELATION_TYPE.apply(lambda x: judge_RELATION_TYPE(x))
        asi = asi[asi.judge_ILLEG_TYPE == 1]
        asi = asi[asi.judge_RELATION_TYPE == 1]
        punish_stock_list = asi.Ticker.unique().tolist()
        drop3_old_out_top300_daily_MarketCap_list = asi[
            asi.Ticker.isin(drop3_old_out_top300_daily_MarketCap_list)].Ticker.unique().tolist()

        return punish_stock_list, drop3_old_out_top300_daily_MarketCap_list

    # 剔除财务亏损的公司
    def drop_loss_profit(self):
        if self.end_time % 1000 == 430:
            ascf = IO.read_data((self.end_time // 10000 - 1) * 10000 + 1231,
                                columns=['STATEMENT_TYPE', 'NET_PROFIT_AFTER_DED_NR_LP'],
                                alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5')
        else:
            ascf = IO.read_data((self.end_time // 10000) * 10000 + 630,
                                columns=['STATEMENT_TYPE', 'NET_PROFIT_AFTER_DED_NR_LP'],
                                alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5')
        ascf = ascf.reset_index()
        ascf = ascf[ascf.STATEMENT_TYPE == 408001000]
        ascf = ascf.dropna()
        loss_profit_stock_list = ascf[ascf.NET_PROFIT_AFTER_DED_NR_LP < 0].Ticker.unique().tolist()
        return loss_profit_stock_list

    # 剔除停牌的股票
    def drop_suspension(self, data, suspend_threshold_time):

        ticker_list = data[data.S_DQ_AMOUNT == 0].Ticker.unique().tolist()
        ticker_amt0_dict = {}
        for ticker in ticker_list:
            count = 0
            df = data[data.Ticker == ticker]
            finalday_amt0_days_dict = {}
            for index, row in df.iterrows():
                temp = df.loc[index].S_DQ_AMOUNT
                if temp == 0:
                    count = count + 1
                    finalday = df.loc[index]['dt']
                else:
                    if count > 10:
                        finalday_amt0_days_dict[finalday] = count
                    count = 0
            if count > 10:
                finalday_amt0_days_dict[df.iloc[-1]['dt']] = count
            if len(finalday_amt0_days_dict) > 0:
                ticker_amt0_dict[ticker] = finalday_amt0_days_dict

        new_amt0_list = list(set(ticker_amt0_dict.keys()) - set(self.old_index_stock_list))

        newset = set()
        for ticker in new_amt0_list:
            tempdict = ticker_amt0_dict[ticker]
            keys = tempdict.keys()
            for key in keys:
                #30
                if key == data.iloc[-1]['dt'] and tempdict[key] > 10:
                    newset.add(ticker)
                #60
                if key > suspend_threshold_time and tempdict[key] > 25:
                    newset.add(ticker)
                if tempdict[key] > 140:
                    newset.add(ticker)
        delete_new_suspension_list = list(newset)


        return delete_new_suspension_list


    # 汇总后剔除需要剔除的不符合规则的样本，得到最终的结果
    def get_bring_and_drop_list(self, new_average_daily_MarketCap, punish_stock_list,
                                loss_profit_stock_list, delete_new_suspension_list,
                                drop2_old_out_top50_daily_turnover_list, drop3_old_out_top300_daily_MarketCap_list,
                                drop4_top50amt_out360mkt_list, sort_average_daily_MarketCap):
        # 选出不符合规则的股票要删掉
        delete_bring_list = list(set(punish_stock_list) | set(loss_profit_stock_list) | set(delete_new_suspension_list))
        delete_bring_list = list(set(delete_bring_list) - set(self.old_index_stock_list))
        drop_this_list = []  # list(set(delete_old_suspension_list) | set(punish_old_stock_list)) # list(set(drop2_old_out_top50_daily_turnover_list) | set(drop3_old_out_top300_daily_MarketCap_list) | set(drop4_top50amt_out360mkt_list))

        # 在新的排序里删掉这些股票
        new_average_daily_MarketCap_delete_bring = new_average_daily_MarketCap[
            ~new_average_daily_MarketCap.Ticker.isin(delete_bring_list)]
        new_average_daily_MarketCap_delete_bring_drop = new_average_daily_MarketCap_delete_bring[
            ~new_average_daily_MarketCap_delete_bring.Ticker.isin(drop_this_list)]

        # 得到前300名作为新的指数成分股票
        new_top300_index = new_average_daily_MarketCap_delete_bring_drop[:300]
        new_top300_list = new_top300_index.Ticker.tolist()

        # 对调整限制30支做处理
        if (len(set(new_top300_list) - set(self.old_index_stock_list)) <= 30):
            new_bring_list = list(set(new_top300_list) - set(self.old_index_stock_list))
            new_drop_list = list(set(self.old_index_stock_list) - set(new_top300_list))
        else:
            new_stock_all_list = list(
                set(new_average_daily_MarketCap_delete_bring_drop.Ticker.tolist()) - set(self.old_index_stock_list))
            delete_size = len(new_stock_all_list) - 30
            delete_stock_list = new_average_daily_MarketCap_delete_bring_drop[
                new_average_daily_MarketCap_delete_bring_drop.Ticker.isin(new_stock_all_list)].tail(
                delete_size).Ticker.tolist()
            new_average_daily_MarketCap_delete_bring_drop_keep30 = new_average_daily_MarketCap_delete_bring_drop[
                ~new_average_daily_MarketCap_delete_bring_drop.Ticker.isin(delete_stock_list)]
            if (len(new_average_daily_MarketCap_delete_bring_drop_keep30) < 300):
                add_size = 300 - len(new_average_daily_MarketCap_delete_bring_drop_keep30)
                add_df = sort_average_daily_MarketCap[sort_average_daily_MarketCap.Ticker.isin(list(
                    set(self.old_index_stock_list) - set(
                        new_average_daily_MarketCap_delete_bring_drop_keep30.Ticker.tolist())))].head(add_size)
                new_average_daily_MarketCap_delete_bring_drop_keep30 = new_average_daily_MarketCap_delete_bring_drop_keep30.append(
                    add_df)

            new_top300_index_keep30 = new_average_daily_MarketCap_delete_bring_drop_keep30[:300]
            new_top300_list_keep30 = new_top300_index_keep30.Ticker.tolist()

            new_top300_list = new_top300_list_keep30
            new_bring_list = list(set(new_top300_list_keep30) - set(self.old_index_stock_list))
            new_drop_list = list(set(self.old_index_stock_list) - set(new_top300_list_keep30))
        return new_bring_list, new_drop_list, new_top300_list

    # 结果评估，与准确结果进行比较
    def evaluate(self, new_bring_list, new_drop_list, index_time):
        result_df = pd.read_excel('D:\\015626\\Desktop\\IndexWarehousing\\成份进出记录.xlsx')

        test_time = str(index_time)[:4] + '-' + str(index_time)[4:6]

        def find_result(time, state):
            if time.find(test_time) >= 0 and state == '纳入':
                return 1
            elif time.find(test_time) >= 0 and state == '剔除':
                return 2
            else:
                return 0

        result_df['result'] = result_df.apply(lambda x: find_result(x.日期, x.状态), axis=1)

        drop_df = result_df[result_df.result == 2]
        bring_df = result_df[result_df.result == 1]

        result_bring_stock_list = bring_df.代码.tolist()
        result_drop_stock_list = drop_df.代码.tolist()

        more_bring = list(set(new_bring_list) - set(result_bring_stock_list))
        less_bring = list(set(result_bring_stock_list) - set(new_bring_list))

        more_drop = list(set(new_drop_list) - set(result_drop_stock_list))
        less_drop = list(set(result_drop_stock_list) - set(new_drop_list))

        print('实际调整数量：', len(result_bring_stock_list))
        print('预测纳入数量：', len(new_bring_list))
        print('预测剔除数量：', len(new_drop_list))
        print()
        print('预测纳入准确：', len(set(result_bring_stock_list) & set(new_bring_list)))
        print('预测剔除准确：', len(set(result_drop_stock_list) & set(new_drop_list)))
        print()
        print('more bring：', more_bring)
        print('less bring：', less_bring)
        print()
        print('more drop：', more_drop)
        print('less drop：', less_drop)

    # 计算相关系数
    def impact_coefficient(self, data, index_stock_list, new_list):
        # 计算冲击系数
        data3 = IO.read_data(int(str(data.iloc[-1]['dt'])[:10].replace('-', '')),
                             columns=['free_float_shares', 'total_shares', 'mkt_cap_ard'],
                             alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        data3 = data3.reset_index()
        data3 = data3[data3.Ticker.isin(index_stock_list)]
        data3['true_ratio'] = data3.free_float_shares / data3.total_shares

        # 分级靠档规则
        def hierarchical_filing(a):
            if a <= 0.15:
                return ceil(a * 100) / 100
            elif a <= 0.2:
                return 0.2
            elif a <= 0.3:
                return 0.3
            elif a <= 0.4:
                return 0.4
            elif a <= 0.5:
                return 0.5
            elif a <= 0.6:
                return 0.6
            elif a <= 0.7:
                return 0.7
            elif a <= 0.8:
                return 0.8
            else:
                return 1

        data3['hiera_ratio'] = data3.true_ratio.apply(lambda x: hierarchical_filing(x))
        data3['free_mkt_cap_ard'] = data3.mkt_cap_ard * data3.hiera_ratio
        all_free_mkt_cap_ard_sum = data3.free_mkt_cap_ard.sum()
        data3['free_mkt_ratio'] = data3.free_mkt_cap_ard / all_free_mkt_cap_ard_sum

        # data4 选出最近三个月的数据
        data4 = data[data.dt > self.get_str_time(self.end_time - 300)]
        data4 = data4[data4.S_DQ_AMOUNT != 0]
        # data7 删选出成分股最近三个月的数据
        data7 = data4[data4.Ticker.isin(index_stock_list)]
        data7 = data7.groupby('Ticker')['S_DQ_AMOUNT'].mean().to_frame()
        data7 = data7.reset_index()

        # 删选出Ticker以及对应的自由流通比例
        data5 = data3[['Ticker', 'free_mkt_ratio']]
        # 将自由流通比例与日均成交额放在一个dataframe中
        data6 = pd.merge(data7, data5)

        data6['coefficient'] = (data6.free_mkt_ratio / (data6.S_DQ_AMOUNT * 1000)) * 100000000 * 1500

        # 删选出所需股票以及对应的冲击系数
        coe_df = data6[data6.Ticker.isin(new_list)]
        ticker_list = coe_df.Ticker.tolist()
        coe_list = coe_df.coefficient.tolist()

        coe_dict = {}
        for i in range(len(ticker_list)):
            coe_dict[ticker_list[i]] = round(coe_list[i], 2)

        return coe_dict

    def get_result(self):
        print('calculate start and end time')
        self.start_time, self.end_time, suspend_threshold_time = self.get_time_info(self.time)

        self.old_index_stock_list = self.find_index_stock_by_time(self.end_time)
        print('prepare to read data...')
        data = self.get_data()
        print('finish reading data')
        data = self.get_Sample_Space(data)
        print('get sample space')
        # 优先剔除不在样本空间内的老样本
        drop1_old_out_samplespace_list = list(set(self.old_index_stock_list) - set(data.Ticker.tolist()))

        print('drop top 3 lines of new stock')
        data = self.drop_top3days_for_new_stock(data)

        print('sort data by average_daily_turnover')
        top50_and60_average_daily_turnover, drop2_old_out_top50_daily_turnover_list, top50_daily_turnover_list = self.sort_average_daily_turnover(
            data, drop1_old_out_samplespace_list)
        print('sort data by average_daily_MarketCap')
        new_average_daily_MarketCap, drop3_old_out_top300_daily_MarketCap_list, drop4_top50amt_out360mkt_list, sort_average_daily_MarketCap = \
            self.sort_average_daily_mkt(
            top50_and60_average_daily_turnover, top50_daily_turnover_list)

        print('drop stock which was illegal')
        punish_stock_list, drop3_old_out_top300_daily_MarketCap_list = self.drop_illegality(drop3_old_out_top300_daily_MarketCap_list)
        print('drop stock with loss profit')
        loss_profit_stock_list = self.drop_loss_profit()
        print('drop stock with suspension')
        delete_new_suspension_list =self.drop_suspension(data, suspend_threshold_time)

        print('get new bring and drop list..')
        new_bring_list, new_drop_list, new_top300_list = self.get_bring_and_drop_list(new_average_daily_MarketCap, punish_stock_list, loss_profit_stock_list,
                                                                delete_new_suspension_list,
                                                                drop2_old_out_top50_daily_turnover_list,
                                                                drop3_old_out_top300_daily_MarketCap_list,
                                                                drop4_top50amt_out360mkt_list,
                                                                sort_average_daily_MarketCap)

        new_bring_coe_dict = self.impact_coefficient(data, new_top300_list, new_bring_list)
        new_drop_coe_dict = self.impact_coefficient(data, self.old_index_stock_list, new_drop_list)

        print()
        print('预测纳入的样本及冲击系数')
        for key in new_bring_coe_dict.keys():
            print(key, new_bring_coe_dict[key])
        print()
        print('预测剔除的样本及冲击系数')
        for key in new_drop_coe_dict.keys():
            print(key, new_drop_coe_dict[key])

        if self.evaluate_result:
            self.evaluate(new_bring_list, new_drop_list, self.time)

        return new_bring_list, new_drop_list, new_bring_coe_dict, new_drop_coe_dict, new_top300_list


# time_list = [201906, 201812, 201806, 201712, 201706, 201612, 201606]
# time_list = [201612, 201606, 201512, 201506]201906, 201812, 201806, 201712, 201706, 201612, 201606
# time_list.reverse()
# for mytime in time_list:
print('*******************************************  ', 202012,'  *********************************************')

hs300 = HS300IndexWareHousing(202006)
new_bring_list, new_drop_list, _, _, _ = hs300.get_result()

print('预测纳入的样本：', new_bring_list)
print(len(new_bring_list))
print('预测剔除的样本：', new_drop_list)
print(len(new_drop_list))

