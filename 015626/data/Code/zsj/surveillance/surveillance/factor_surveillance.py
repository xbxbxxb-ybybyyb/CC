
#import sys
#sys.path.insert(0, '/path/to/application/app/folder')



"""    
# use example 
from multifactor.backtest.factor_surveillance import FactorSurveillance
from multifactor.backtest.factor_test import SingleFactorTest
from multifactor.backtest.factor_surveillance import read_pickle
import os


if __name__ == '__main__':
    sdate,edate = 20090101,20180720
    # if base data is saved 
    base_data = read_pickle('S:\\Quant\\backtest\\misc\\quant_data\\factor_test_hpr_10.pkl')
    sft = SingleFactorTest(sdate, edate, universe='alpha_universe', holding_period=10,provided_data=base_data)
    
    # if base data is not saved yet 
    #sft = SingleFactorTest(sdate, edate, universe='alpha_universe', holding_period=10)
    #base_data = sft.base_data
    #save_pickle(base_data,'S:\\Quant\\backtest\\misc\\quant_data\\factor_test_hpr_10.pkl')
    
    base_path = r'A:\zhisj\factor_status'
    factor_init = os.path.join(base_path,'factors.ini')
    fs = FactorSurveillance(sdate,
                             edate,
                             holding_period=10,
                             factor_init = factor_init,
                             base_path = base_path,
                             factor_min_size = 500,
                             easy_test = True,
                             provided_data = base_data)
    fs.prep()
    fs.batch_test()
    fs.collect_stats()
    
"""


import pandas as pd
import numpy as np
import os
from multifactor.backtest.hdf_walker import HDFWalker
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.backtest.factor_test import SingleFactorTest
from multifactor.backtest.survey_report_generator import generate_pdf
from multifactor.backtest.survey_utility import *
from multifactor.backtest.common_utility import *
from functools import partial
import datetime as dt
import pickle
import logging

class FactorSurveillance:
    
    def __init__(self,
                 sdate=None,
                 edate=None,
                 holding_period=10,
                 factor_init = 'factors.ini',
                 base_path = None,
                 universe = 'alpha_universe',
                 factor_min_size = 500,
                 easy_test = True,
                 provided_data = None,
                 analyst_name='',
                 ic_type = 'IC Neutralized',
                 transaction_cost = 0.002,
                 in_sample = None,
                 out_of_sample = None,
                 log_level ='INFO'  # log level
                 ):
        #table_name = 'WIND_AShareMoneyFlow'
        self.sdate = sdate
        self.edate = edate
        self.holding_period = holding_period
        self.factor_init = factor_init
        self.universe = universe
        self.factor_min_size = factor_min_size
        self.easy_test = easy_test
        self.provided_data = provided_data
        # create path
        self.analyst_name = analyst_name
        self.ic_type = ic_type
        self.transaction_cost = transaction_cost
        if base_path is None:
            self.base_path  = os.getcwd()

        else:
            self.base_path  = base_path

        """ file generator """        
        self.path_dict = generate_path(self.base_path,['factor_report','log'])
        self.path_dict['factor_summary_excel'] = os.path.join(self.base_path, 'factor_summary.xlsx')
        self.path_dict['factor_summary_pkl'] = os.path.join(self.base_path, 'factor_summary.pkl')
        current_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.path_dict['log_file'] = os.path.join(self.path_dict['log'], 
                                                  'FactorSurveillance_%s_%s.log'%(self.analyst_name,current_time))
        self.path_dict['analyst_factor_stats'] = os.path.join(self.base_path,'analyst_factor_stats.csv')        
        
        self.in_sample = in_sample
        self.out_of_sample = out_of_sample

        """ logger """
        self.logger = logging.getLogger('FactorSurveillance')
        self.log_level=log_level #'INFO'
        self.logger.setLevel(eval('logging.'+log_level.upper()))
        file_handler = logging.FileHandler(self.path_dict['log_file'], mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.info('*'*100)
        self.logger.info('**** Factor Surveillance Initiating ****')
        self.logger.info('test date: %s - %s'%(self.sdate,self.edate))
            
                
    def check_condition(self):
        
        self.logger.info('checking factor update condition')
        wlkr = HDFWalker(author='analyst',conf_path = self.factor_init,output_path=self.base_path)
        wlkr.walk()
    
        edate_dt = pd.Timestamp(dt.datetime.strptime(str(self.edate), '%Y%m%d'))
        factor_stats = pd.read_csv(self.path_dict['analyst_factor_stats'],index_col=0,parse_dates=[1,2])
        if len(factor_stats)==0:
            self.logger.warning('Exit: No factor found')
            raise Exception
            
        factor_stats = factor_stats.sort_values('last date',ascending=False)
        filter_cond = factor_stats['last date']>=edate_dt
        self.factor_update = factor_stats[filter_cond]
        
        if len(self.factor_update)==0:
            self.logger.warning('Exit: No factor with last date:%d'%self.edate)
            raise Exception
        self.logger.info('factor check done --- %d/%d valid factors'%(len(self.factor_update),len(factor_stats)))



    def load_data(self):
        if self.provided_data is not None:
            self.sft = SingleFactorTest(self.sdate,self.edate,provided_data=self.provided_data,
                                        universe=self.universe,holding_period=self.holding_period,
                                        transaction_cost = self.transaction_cost)
        else:
            self.logger.info('loading single factor test data')
            self.sft = SingleFactorTest(self.sdate,self.edate,
                                        universe=self.universe,holding_period=self.holding_period,
                                        transaction_cost = self.transaction_cost)
        return
    
    def prep(self):
        # check condition
        self.check_condition()
        self.load_data()
                    
    
    def batch_test(self):
        factor_list = self.factor_update.index.tolist()
        fac_num = len(factor_list)
        parallel = True
        if not parallel:
            for fac_name in factor_list:
                fac_path = self.factor_update.loc[fac_name,'path']            
                self.logger.info('*** %d/%d - %s ***'%(factor_list.index(fac_name)+1,fac_num,fac_name))
                try:
                    test_fac = IO.read_data([self.sdate,self.edate],alt = fac_path)
                except:
                    self.logger.warning('read factor h5 error: %s'%fac_path)
                try:
                    self.sft.load_factor(factor_data=test_fac,name=fac_name)
                    self.sft.shoot(result_folder=self.path_dict['factor_report'])   # call function 
                except:
                    self.logger.warning('test fail:%s'%fac_name)
        else:
            func = factor_read_test
            iter_list = self.factor_update['path'].values.tolist()
            multiprocess_wrapper(func,iter_list,logger=self.logger,sft=self.sft,sdate=self.sdate,edate=self.edate,result_folder=self.path_dict['factor_report'])    


    
    def collect_stats(self):
        self.logger.info('collecting stats')
        edate_dt = pd.Timestamp(dt.datetime.strptime(str(self.edate), '%Y%m%d'))
        factor_stats = pd.read_csv(os.path.join(self.base_path,'analyst_factor_stats.csv'),index_col=0,parse_dates=[1,2])
        factor_stats = factor_stats.sort_values('last date',ascending=False)
        filter_cond = factor_stats['last date']>=edate_dt
        self.factor_update = factor_stats[filter_cond]
        factor_name_list = self.factor_update.index.tolist()
        self.logger.info('fecth single factor test result')

        got_ind = False
        output_name_list =['ic_ts','max_q_ts','max_q_ts_after_cost','bucket_ic_30','stock_count','factor_sign']
        #output_dict = func_parallel_v2(func2,input_list2,output_name_list=['max_q','ic','stock_count'],concat_axis=1,max_workers=10)
        try:
            self.logger.info('try from pickle')
            input_list = [os.path.join(self.path_dict['factor_report'],factor_name,'FactorBacktest_'+factor_name+'.pkl') for factor_name in factor_name_list]
            func = partial(extract_pickle,ic_type=self.ic_type)
            output_dict = func_parallel(func,input_list,output_name_list=output_name_list,concat_axis=1,max_workers=10)
            got_ind = True
        except:
            try:
                self.logger.info('try from excel')
                input_list = [os.path.join(self.path_dict['factor_report'],factor_name,'FactorBacktest_'+factor_name+'.xlsx') for factor_name in factor_name_list]
                func = partial(extract_excel,ic_type=self.ic_type)
                output_dict = func_parallel(func,input_list,output_name_list=output_name_list,concat_axis=1,max_workers=10)
                got_ind = True
            except:
                self.logger.warning('failed to fetch result from pickle and excel')
                raise Exception
        if got_ind:
            self.logger.info('done with fetch result from pickle\excel')
                
        max_q_df,ic_ts_df,stock_count_df = output_dict['max_q_ts'],output_dict['ic_ts'],output_dict['stock_count']
        max_q_after_cost_df, bucket_ic_30_df = output_dict['max_q_ts_after_cost'],output_dict['bucket_ic_30']
        factor_sign = output_dict['factor_sign'].T
        # drop duplicates
        max_q_df = max_q_df.T.groupby(level=0).first().T
        ic_ts_df = ic_ts_df.T.groupby(level=0).first().T
        max_q_stats = calc_seg_performance(max_q_df)
        max_q_stats_by_year = max_q_df.groupby(max_q_df.index.year).apply(calc_seg_performance)
        ic_stats = calc_ic_performance(ic_ts_df)
        ic_stats_by_year = ic_ts_df.groupby(ic_ts_df.index.year).apply(calc_ic_performance)
        
        max_q_sort_measure = 'excess_ret'
        trail_list = [5,10,20,60,120,240]
        show_top_num_per_time = 20

        max_q_stats_by_year.index.names = ['dt', 'year']
        ic_stats_by_year.index.names = ['dt', 'year']
        max_q_stats_by_year_sorted = max_q_stats_by_year.reset_index().sort_values(['dt',max_q_sort_measure],ascending=False).set_index(['dt','year'])
        max_q_stats_by_year_top = max_q_stats_by_year_sorted.groupby('dt').head(show_top_num_per_time)
        trail_max_q = calc_trailing_stats(max_q_df,trail_list=trail_list,show_type='sum',skip_tail=self.holding_period) 
        trail_ic = calc_trailing_stats(ic_ts_df,trail_list=[5,10,20,60,120,240],show_type='mean',skip_tail=self.holding_period) 
        
        max_q_per_month = get_top_by_time(max_q_df,top_num=show_top_num_per_time,sample_freq='M',agg='sum',index_reformat=True)
        max_q_per_year = get_top_by_time(max_q_df,top_num=show_top_num_per_time,sample_freq='A',agg='sum',index_reformat=True)
        ic_per_month = get_top_by_time(ic_ts_df,top_num=show_top_num_per_time,sample_freq='M',agg='mean',index_reformat=True)
        ic_per_year = get_top_by_time(ic_ts_df,top_num=show_top_num_per_time,sample_freq='A',agg='mean',index_reformat=True)
        
        max_q_per_month_total = get_top_by_time(max_q_df,top_num=None,sample_freq='M',agg='sum',index_reformat=True)
        max_q_monthly = max_q_per_month_total['score'].unstack()
        ic_per_month_total = get_top_by_time(ic_ts_df,top_num=None,sample_freq='M',agg='mean',index_reformat=True)
        ic_monthly = ic_per_month_total['score'].unstack()
        
        factor_count_ts = np.isfinite(max_q_df).sum(axis=1)
        
        max_q_cut_list = [-0.15] + [round(-0.05+0.025*i,3) for i in range(5)] + [0.15] 
        ic_cut_list = [-0.2] + [round(-0.05+0.025*i,3) for i in range(5)] + [0.2] 
        max_q_ret_dist_pct = get_dist_pct(max_q_monthly,range_list=max_q_cut_list)
        ic_dist_pct = get_dist_pct(ic_monthly,range_list=ic_cut_list)
        
        positive_excess_ret_roll = (max_q_df.resample('M').mean()>0).sum(axis=1)
        positive_excess_ret_roll = positive_excess_ret_roll.reset_index()
        positive_excess_ret_roll.columns=['dt','# of factor with positive return']
        positive_excess_ret_roll['dt'] = [datetime.datetime.strftime(i,'%Y-%m') for i in positive_excess_ret_roll['dt']]
        positive_excess_ret_roll = positive_excess_ret_roll.set_index('dt').reindex(max_q_ret_dist_pct.index)
        
        # calc factor correlation
        max_q_corr = pairwise_correlation(max_q_df,method='pearson',min_pct=0.5,remove_diag=True)
        ic_corr = pairwise_correlation(ic_ts_df,method='pearson',min_pct=0.5,remove_diag=True)
        
        ic_summary = ic_stats.describe().drop('std',axis=0)
        max_q_summary = max_q_stats.describe().drop('std',axis=0)
        
        # correlation 
        correlation_stats = pd.concat([max_q_corr.mean().describe(),ic_corr.mean().describe()],axis=1)
        correlation_stats.columns = ['Excess Return','IC']
        
        ic_mean,icir_mean = ic_stats['ic_mean'].mean(),ic_stats['icir'].mean()
        er_mean,ir_mean = max_q_stats['excess_ret'].mean(),max_q_stats['info_ratio'].mean()
        #analyst = 'zhisj'
        val_list = [self.analyst_name,'%d-%d'%(self.sdate,self.edate),len(ic_ts_df.columns),ic_mean,icir_mean,er_mean,ir_mean]
        key_list = ['Analyst','Period','Count','IC','ICIR','ER','IR']
        summary = pd.DataFrame(val_list,index=key_list,columns=['summary_stats'])

        factor_path_directory = pd.read_csv(os.path.join(self.base_path,'analyst_factor_stats.csv'),index_col=0,parse_dates=[1,2])
        factor_path_directory = factor_path_directory.sort_values('last date',ascending=False)
        
        self.output_dict = {'summary':summary,'path':factor_path_directory,'max_q_summary':max_q_summary,'ic_summary':ic_summary,
                            'correlation_stats':correlation_stats,
                            'ic_corr':ic_corr,
                            'max_q_corr':max_q_corr,'positive_excess_ret_roll':positive_excess_ret_roll,'ic_dist_pct':ic_dist_pct,
                            'max_q_ret_dist_pct':max_q_ret_dist_pct,'factor_count_ts':factor_count_ts,
                            'ic_per_year':ic_per_year,'ic_per_month':ic_per_month,
                            'max_q_per_year':max_q_per_year,'max_q_per_month':max_q_per_month,
                            'trail_ic':trail_ic,'trail_max_q':trail_max_q,
                            'max_q_stats_by_year_top':max_q_stats_by_year_top,
                            'max_q_stats':max_q_stats,'ic_stats':ic_stats,'max_q_stats_by_year':max_q_stats_by_year,
                            'ic_stats_by_year':ic_stats_by_year,'max_q_df':max_q_df,'ic_ts_df':ic_ts_df,
                            'stock_count_df':stock_count_df,'max_q_after_cost_df':max_q_after_cost_df, 
                            'bucket_ic_30_df':bucket_ic_30_df,
                            'factor_sign':factor_sign
                            }
        
        if self.in_sample is not None and self.out_of_sample is not None:
            self.logger.info('evaluting factors for in sample and out of sample')
            factor_score_in,factor_score_ots = evaluate_factor(self.output_dict,self.in_sample,self.out_of_sample)
            self.output_dict['factor_score_in_sample'] = factor_score_in
            self.output_dict['factor_score_out_of_sample'] = factor_score_ots
            
        self.logger.info('saving collected stats to:%s'%self.path_dict['factor_summary_excel'])
        excel_saver(self.output_dict, self.path_dict['factor_summary_excel'])
        save_pickle(self.output_dict, self.path_dict['factor_summary_pkl'])
        self.logger.info('generating pdf')
        generate_pdf(excel_name=self.path_dict['factor_summary_excel'],output_folder=self.base_path)
        self.logger.info('***** all done ******')
        return     
    

    

def rank_factor(base_path,analyst_list):
    print ('loading')
    excel_path = os.path.join(base_path,'factor_score_ranking.xlsx')
    file_dict = {name:os.path.join(base_path,name,'factor_summary.pkl') for name in analyst_list}
    fac_sum_dict = {name:read_pickle(file_dict[name]) for name in file_dict}
    #collect_list = ['summary','factor_score_in_sample','factor_score_out_of_sample','stock_count_df']
    _summary,_fs_in,_fs_out,_stk_count = [],[],[],[]
    for name in analyst_list:
        print (name)
        _summary.append(fac_sum_dict[name]['summary'])

        fsi = fac_sum_dict[name]['factor_score_in_sample']
        fsi = fsi.dropna(how='any')
        fsi['analyst'] = name
        #fsi['return2mdd'] = -fsi['return2mdd']

        fso = fac_sum_dict[name]['factor_score_out_of_sample']
        fso = fso.dropna(how='any')
        fso['analyst'] = name
        #fso['return2mdd'] = -fso['return2mdd']

        fac_list = set(fsi.index).intersection(set(fso.index))
        fsi = fsi.reindex(fac_list)
        fso = fso.reindex(fac_list)
        
        _fs_in.append(fsi)
        _fs_out.append(fso)
        
        stkc = fac_sum_dict[name]['stock_count_df']
        stkc = pd.DataFrame(stkc.mean(),columns =['stock_count']).applymap(lambda x : int(x))
        stkc['analyst'] = name
        _stk_count.append(stkc)
        
    summary = pd.concat(_summary,axis=1)
    summary.columns = analyst_list
    
    factor_score_in_sample = pd.concat(_fs_in,axis=0)
    factor_score_out_of_sample = pd.concat(_fs_out,axis=0)
    
    factor_score_in_sample['return2mdd'] = -1 * factor_score_in_sample['return2mdd'].values
    factor_score_in_sample = factor_score_in_sample.sort_values('excess_ret_after_cost',ascending=False)
    
    factor_score_out_of_sample['return2mdd'] = -1 * factor_score_out_of_sample['return2mdd'].values
    factor_score_out_of_sample = factor_score_out_of_sample.sort_values('excess_ret_after_cost',ascending=False)
    
    stock_count = pd.concat(_stk_count,axis=0)

    rank_measure = [i for i in factor_score_in_sample.columns if i not in ['analyst']]

    factor_score_in_sample_rank = factor_score_in_sample[rank_measure].rank(axis=0,pct=True,ascending=False)
    factor_score_in_sample_rank['analyst'] = factor_score_in_sample['analyst']
    factor_score_in_sample_rank = factor_score_in_sample_rank.sort_values('excess_ret_after_cost',ascending=True)

    factor_score_out_of_sample_rank = factor_score_out_of_sample[rank_measure].rank(axis=0,pct=True,ascending=False)
    factor_score_out_of_sample_rank['analyst'] = factor_score_out_of_sample['analyst']
    factor_score_out_of_sample_rank = factor_score_out_of_sample_rank.sort_values('excess_ret_after_cost',ascending=True)
    
    factor_score = pd.concat([factor_score_in_sample_rank.mean(axis=1),factor_score_out_of_sample_rank.mean(axis=1)],axis=1)
    factor_score.columns = ['in sample','out of sample']
    factor_score['overall'] = factor_score.mean(axis=1)
    factor_score = factor_score.sort_values('overall')
    factor_score = pd.concat([factor_score,factor_score_in_sample[['analyst']]],axis=1)
    
    score_ots_analyst = factor_score_out_of_sample.groupby('analyst').mean()
    score_ots_analyst = score_ots_analyst.sort_values('excess_ret_after_cost',ascending=False)
    score_ots_analyst = score_ots_analyst.append(pd.DataFrame(factor_score_out_of_sample.mean(),columns=['overall']).T)

    score_is_analyst = factor_score_in_sample.groupby('analyst').mean()
    score_is_analyst = score_is_analyst.sort_values('excess_ret_after_cost',ascending=False)
    score_is_analyst = score_is_analyst.append(pd.DataFrame(factor_score_in_sample.mean(),columns=['overall']).T)
    
    collect_dict = {'summary':summary,
                    'factor_score_in_sample':factor_score_in_sample,
                    'factor_score_out_of_sample':factor_score_out_of_sample,
                    'stock_count':stock_count,
                    'factor_score_in_sample_rank':factor_score_in_sample_rank,
                    'factor_score_out_of_sample_rank':factor_score_out_of_sample_rank,
                    'factor_score':factor_score,
                    'score_is_analyst':score_is_analyst,
                    'score_ots_analyst':score_ots_analyst}
    
    excel_saver(collect_dict, excel_path)
    
    return


def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict