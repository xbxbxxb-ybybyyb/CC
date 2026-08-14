from SimiStock.Version1.SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.dataApi import getData
from SimiStock.Version1.SimiStockGenerator.enum import Hedge
from typing import List
from tqdm import tqdm

# 1、计算单日的板块中心性
class SimiMethodDemo(SimiMethodBase):
    def __init__(self, concept='SW1',use_time = 242):
        super().__init__(concept=concept)
        # TODO：此处定义其他内容
        self.use_time = use_time
        # 个股日频数据
        open_badj,close_badj,high_badj,low_badj = getData.get_daily_1factor('open_badj'),getData.get_daily_1factor('close_badj'),\
                                                  getData.get_daily_1factor('high_badj'),getData.get_daily_1factor('low_badj')
        self.open_badj,self.close_badj,self.high_badj,self.low_badj = open_badj,close_badj,high_badj,low_badj

        open,close,high,low = getData.get_daily_1factor('open'),getData.get_daily_1factor('close'),\
                              getData.get_daily_1factor('high'),getData.get_daily_1factor('low')
        pre_close = getData.get_daily_1factor('pre_close')
        pct_chg = getData.get_daily_1factor('pct_chg')

        self.open, self.close, self.high, self.low = open, close, high, low
        self.pre_close= pre_close
        self.pct_chg = pct_chg

    def get_simi_stock(self, stk_id, trade_date):
        ret_list = list()
        stk_list, stk_weight = self.simi_strategy(stk_id, trade_date, self.get_concept_list(stk_id, trade_date))
        for idx in range(1, 21):
            ret_list.append(Hedge(stk_id=int(stk_id), date=int(trade_date), hedge_list=stk_list[:idx], hedge_weight=stk_weight[:idx]))
        return ret_list

    def get_simi_stocks(self, stk_date_list: List[tuple]):
        ret_list = list()
        pbar = tqdm(range(len(stk_date_list)))
        for idx in pbar:
            stk_id, trade_date = stk_date_list[idx]
            pbar.set_description('并行生成中|%s|%s' % (int(stk_id), int(trade_date)))
            hedge = self.get_simi_stock(stk_id, trade_date)
            ret_list.extend(hedge)
        return ret_list

    # 1、计算简单的相关性
    def cal_corr(self,df,stk_id, trade_date, concept_list,use_time = 242):
        # 1、收益率相关性
        close = df.loc[:trade_date].iloc[-use_time:].fillna(method='ffill').fillna(0)
        corr_result = close[concept_list].corrwith(close[stk_id])
        corr_result = corr_result.sort_values(ascending=False).dropna()

        return corr_result

    # 计算最终相关性
    def simi_strategy(self, stk_id, trade_date, concept_list):
        #TODO: 此函数必须复写，并返回Hedge类型
        #stk_id,trade_date = 600111,20211231
        #concept_list = self.get_concept_list(stk_id, trade_date)
        ########################################### 相关性统计 #####################################################
        # 1、日收益率相关性
        pct_corr = self.cal_corr(self.pct_chg,stk_id, trade_date, concept_list,use_time = self.use_time)  #
        code_list = list(pct_corr.index[[1]])
        code_weight = [1]
        return code_list,code_weight


if __name__ == '__main__':
    self = SimiMethodDemo(concept='all_market')
    result = self.get_hedge_list()