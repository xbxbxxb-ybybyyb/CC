"""
coding: utf-8
CreateDate: 2023/8/4 13:31
Location: HTSC
Author: ZhangWenhu
"""
import os
import copy
import pandas as pd
import numpy as np
from multifactor.IO import IO
import warnings


from Registration import *

warnings.filterwarnings("ignore")
def extract_thres(element, part):
    p = copy.deepcopy(element)
    if isinstance(p,  pd.Series):
        p = p.values
    p.sort()
    thres = p[-int(len(p) * part/100.0)]
    # import pdb; pdb.set_trace()
    if part<1e-8:
        thres = float('inf')
    elif part>99.99:
        thres = -float('inf')
    return thres


def My_LoadFiles(file_path):
    assert os.path.exists(file_path), '!!!! PATH: {} does not exist!!!!'.format(file_path)
    if file_path.endswith('.h5'):
        data_df = IO.read_data([20100101, 20301231], alt=file_path)
    elif file_path.endswith('.pkl'):
        data_df = pd.read_pickle(file_path)
    elif file_path.endswith('.csv'):
        data_df = pd.read_csv(open(file_path))
    else:
        raise NotImplementedError
    return data_df

def catch_IntervalNumber(end_date):
    for i in range(len(INTERVAL_END_DATE)):
        if end_date>INTERVAL_END_DATE[i]:
            continue
        else:
            return i+1
    raise NotImplementedError('end_date is out of bound in [INTERVAL_END_DATE]')

def process_attend_thres(signal_df, raw_columns, thres=Continuous_Thres,name='Unknown'):
    pred_names = ['_'.join([name,'prediction', str(thres_i)]) for thres_i in thres]

    if raw_columns=='pred_Reg':
        thres_hold=[ extract_thres(signal_df[raw_columns], part_i) for part_i in thres]
    else:
        thres_hold = thres

    # import pdb; pdb.set_trace()
    for thres_i, name_i in zip(thres_hold, pred_names):
        signal_df[name_i] = 1*(signal_df[raw_columns]>=thres_i)
    if raw_columns !='pred_Reg':
        rename_columns = [n+'_'+str(int(sum(signal_df[n])/signal_df.shape[0]*100))for n in pred_names]
        signal_df = signal_df.rename(columns=dict(zip(pred_names, rename_columns)))
        pred_names = rename_columns
    # print(name, thres, thres_hold)
    return signal_df[['datelist', 'stockID']+pred_names], pred_names


class MultiEval_Tool:
    def __init__(self, target_strategy_dict:dict,date_range: list,savepath:str,total_strategy_names=TOTAL_STRATEGY_NAME ):
        self.target_csv = target_strategy_dict
        self.Contents = self.create_total_strategy_contents(target_strategy_dict, total_strategy_names)
        self.begin_date = int(date_range[0])
        self.end_date =  int(date_range[1])

        self.Interval_Number = catch_IntervalNumber(self.end_date)
        self.total_df = self.load_data_total(total_strategy_names)
        # self.total_df[~np.isnan(self.total_df['Sapphire1_prediction_45'])]
        #   self.total_df[~np.isnan(self.total_df['Sapphire2_prediction_50'])]
        # self.total_df[~np.isnan(self.total_df['Sapphire2_prediction_0'])][['Sapphire2_prediction_0','Sapphire1_prediction_0']]
        # import pdb;  pdb.set_trace()

    def create_total_strategy_contents(self, target_dict, total_names):
        visible_names = list(target_dict.keys())
        input_names = [k for k in visible_names if target_dict[k]!='vanilla']
        content_names = total_names['Buy'] + total_names['Sell']
        content_type = ['Buy']*len(total_names['Buy']) +  ['Sell']*len(total_names['Sell'])
        content_source=['vanilla']* len(content_names)

        content_data = {'strategy':content_names,'type':content_type,'signal':content_source}
        content_df = pd.DataFrame(content_data)
        content_df['thres_visible'] = content_df['strategy'].isin(visible_names)
        content_df.loc[content_df['strategy'].isin(input_names),'signal'] = np.array(['input']* len(input_names))
        content_df['signal_col'] = None
        return content_df.set_index('strategy')


    def load_data_total(self, strategy_name_total):
        total_df = pd.DataFrame()
        buy_df_list, sell_df_list = [],[]
        for s in strategy_name_total['Buy']:
            temp_df = self.load_data_single(s)
            buy_df_list.append(temp_df)
        buy_df = pd.concat(buy_df_list, axis=1)


        for s in strategy_name_total['Sell']:
            temp_df = self.load_data_single(s,'Sell')
            sell_df_list.append(temp_df)
        sell_df = pd.concat(sell_df_list, axis=1)
        sell_df = self.priority_process(sell_df)
        total =  pd.concat([buy_df,sell_df], axis=1)
        #### total[~np.isnan(total['Sapphire2_prediction_50'])]

        # import pdb; pdb.set_trace()

        return total

    def load_data_single(self,strategy_name_i, mode='Buy'):
        config = eval(strategy_name_i+'_Config')
        profit_sel, profit_columns = self.load_profit(strategy_name_i, config, mode)

        if self.Contents.loc[strategy_name_i]['signal'] =='vanilla':
            ### load vanilla online strategy, using discreted_attend_thres
            signal = My_LoadFiles(config['signal_Q{}'.format(self.Interval_Number)])
            raw_sig = config['voting']['voter_columns'][0]
            signal_sel = signal[['datelist', 'stockID'] + [raw_sig]]
            if self.Contents.loc[strategy_name_i]['thres_visible']:
                thres = Discreted_Thres
            else:
                thres = [ config['voting']['thres'] ]

        elif self.Contents.loc[strategy_name_i]['signal'] =='input':
            ### load developing strategy, using continuous_attend_thres
            signal = My_LoadFiles(self.target_csv[strategy_name_i])
            signal_sel = signal[['datelist', 'stockID', 'prediction', 'pred_Reg']]
            raw_sig='pred_Reg'
            thres = Continuous_Thres

        signal_attend_df, signal_columns = process_attend_thres(signal_sel, raw_sig, thres, strategy_name_i)
        signal_columns = signal_columns  ##

        signal_attend_df['dt'] = pd.to_datetime(signal_attend_df['datelist'], format='%Y%m%d')
        signal_attend_df['Ticker'] = signal_attend_df['stockID']
        signal_attend_df = signal_attend_df.set_index(['dt','Ticker'])
        single_model_df = signal_attend_df.join(profit_sel,how='inner')
        # print(single_model_df.shape, signal_attend_df.shape, profit_sel.shape, strategy_name_i)
        assert single_model_df.shape[0]==signal_attend_df.shape[0],'missing profit data {}, please trans <dt>/<datelist> of signal_data into <dt_last_zt_1_ts> manually !!!'.format(strategy_name_i)

        self.Contents.loc[strategy_name_i, 'signal_col'] = str(signal_columns)


        single_model_df = single_model_df.loc[(single_model_df['datelist']>=self.begin_date)&(single_model_df['datelist']<=self.end_date)]
        total_col = signal_columns+ profit_columns
        return single_model_df[total_col]

    def load_profit(self,strategy_name_i, config, mode='buy' ):
        profit = My_LoadFiles(config['profit_file'])

        ### 将卖出收益文件中，index dt由卖出时间转化为买入时间
        if mode=='Sell':
            profit = profit.reset_index()
            profit['dt'] = pd.to_datetime(profit['dt_last_zt_1_ts'])
            profit = profit.set_index(['dt', 'Ticker'])
        profit = profit[~np.isnan(profit[config['pct_name']])]
        profit['pct'] = profit[config['pct_name']] - config['cost_pct']
        profit_sel = profit[['buy_amt', 'pct']].rename(columns={'buy_amt': strategy_name_i + '_amt', 'pct': strategy_name_i + '_pct'})

        profit_col = [strategy_name_i+'_amt',strategy_name_i+'_pct']


        if 'pct_time' in profit.columns:
            profit_sel[strategy_name_i+'_pct_time'] = profit['pct_time']
            profit_col = profit_col+ [strategy_name_i+'_pct_time']

        # if mode == 'Sell':
        #     profit_sel['dt_last_zt_1_ts'] = profit['dt_last_zt_1_ts']
        #     profit_col+=['dt_last_zt_1_ts']
        return profit_sel, profit_col

    def priority_process(self, sell_df):

        if 'JupiterNSell' in self.Contents.index:
            sell_df['JupiterNSell_pct_time'] =93100000
        sell_names =self.Contents[self.Contents['type']=='Sell'].index.tolist()
        pct_col = [n+'_pct_time' for n in sell_names]
        pri_col = [n+'_priority' for n in sell_names]
        pri_data =sell_df[pct_col].rank(method='first',axis=1).fillna(99999)
        sell_df[pri_col] = pri_data
        # import pdb;  pdb.set_trace()
        return sell_df




if __name__ == "__main__":
    # date_range = ['2016-01-01', '2020-12-31'],
    # date_range = ['2016-01-01', '2021-06-30'],
    # date_range = ['2016-01-01', '2021-12-31'],

    date_range = [20191001, 20200331]
    target_s = {
        'Sapphire1': '/data/user/022325/Data/experiments/0814try_Sapphire1_Q1_XGB_Model_FSRS_Searching/search_results/test_learning_rate_0X02_n_estimators_800_.csv',
        'Sapphire2': "/data/user/022325/Data/experiments/0814try_Sapphire2_Q1_XGB_Model_FSRS_Searching/search_results/test_learning_rate_0X02_n_estimators_800_.csv",
        'Europa': 'vanilla'}
    save_p = '/home/appadmin/multi-eval'

    total_name = {'Buy': ['Europa','JupiterN'], 'Sell': ['JupiterNSell', 'Sapphire1','Sapphire2']}
    # total_name = {'Buy': ['Europa','JupiterN'], 'Sell': ['JupiterNSell']}


    tmp_tool = MultiEval_Tool(target_s, date_range,save_p, total_name)
    print('0000')
    # df = My_LoadFiles('/data/group/800463/wangj/save_files/Jupiter_v9/Jupiter_out_testfit_v9_fac_20221220_maxbeta_final_noroll_merge6models_20230116.csv')
    # df = My_LoadFiles( '/home/appadmin/multi-eval/Registration.py')
    import pdb; pdb.set_trace()