# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 14:49:59 2018

@author: 012315
"""
from scipy import linalg
import scipy.optimize as optimize


################################################################################################################
"""Max ICIR for static weight"""

from sklearn.covariance import ledoit_wolf, OAS, ShrunkCovariance, GraphLassoCV,empirical_covariance


def calc_covariance(X,cov_type='shrink'):
    """covariance matrix esitmation
    cov_type: sample, shrink, graph_lasso,oas
    X: shape (n_samples, n_features) - date*stock
    # request full length
    """
    if type(X) == pd.DataFrame:
        x_mat = X.values
        col_list = X.columns.tolist()
    else:
        x_mat = X
    num = x_mat.shape[1]
    mask = np.isfinite(np.sum(x_mat,axis=0))
    x_use = x_mat[:,mask]
    cov_mat = np.zeros([num,num])
    cov_mat[:] = np.nan
    mask_cov = np.zeros([num,num])
    mask_cov[:,~mask] = np.nan
    mask_cov[~mask,:] = np.nan
    mask_cov_final = np.isfinite(mask_cov)
    if x_use.shape[1]>1:
        if cov_type =='shrink':
            cov, shrinkage = ledoit_wolf(x_use)
        elif cov_type == 'graph_lasso':
            graph_lasso = GraphLassoCV().fit(x_use)
            cov = graph_lasso.covariance_
        elif cov_type == 'sample':
            cov = empirical_covariance(x_use)
        elif cov_type =='oas':
            cov = OAS().fit(x_use).covariance_ 
        cov_mat[mask_cov_final] = cov.flatten()
        if type(X) == pd.DataFrame:
            cov_mat = pd.DataFrame(cov_mat,index=col_list,columns=col_list)
    else:
        cov_mat[:] = np.nan
    return cov_mat




def calc_covariance_roll(X,roll_win,cov_type='shrink'):
    print ('cov_type=%s'%(cov_type))
    date_list,col_list = list(X.index),list(X.columns)
    date_num,col_num = len(date_list),len(col_list)
    rebal_num = date_num - roll_win
    cov_matr = np.zeros([date_num*col_num,col_num])
    cov_matr[:] = np.nan
    X_mat = X.values
    for i in range(rebal_num):
        cov_start,cov_end = i*col_num,(i+1)*col_num
        cov_matr[cov_start:cov_end,:] = calc_covariance(X_mat[i:i+roll_win,:],cov_type)
    index_tuple = [np.repeat(date_list,len(col_list)),col_list*len(date_list)]
    mi_index = pd.MultiIndex.from_tuples(list(zip(*index_tuple)),names=['dt', None])         
    cov_roll = pd.DataFrame(cov_matr,columns=col_list,index=mi_index)
    return cov_roll

def factor_sign_flip(factor_tank,holding_period_ret):
    fac_list = list(factor_tank.keys())
    factor_tank_positive = {}
    flip_list = []
    ic_list = []
    print ('Calculating IC')
    for fac in fac_list:
        ic_mean = factor_tank[fac].corrwith(holding_period_ret,axis=1).mean()
        ic_list.append(ic_mean)
        if ic_mean<0:
            factor_tank_positive[fac] = -1 * factor_tank[fac]
            flip_list.append(fac)
        else:
            factor_tank_positive[fac] = factor_tank[fac]
    ic_df = pd.DataFrame(ic_list,index = fac_list)
    print ('factor list flipped:%s'%str(flip_list))
    print (ic_df)
    return factor_tank_positive

def factor_combine_max_ICIR(factor_tank,holding_period_ret,ctype='join',test_year=None,must_have=None,min_fac=1,min_weight=0,plot=True,solve_type='optimize'):
    """
    # use example
    combine_tank = dict((name,eval(name)) for name in ['holistic_value_neu_ind','roe_neu_ind_size'])
    factor_icir,IC_stats,IC_ts = factor_combine_max_ICIR(combine_tank,holding_period_ret,ctype='join')
    IC_tank['factor_icir']  = IC_test(factor_icir,holding_period_ret,holding_period)
    """
    pd.options.display.float_format = '{:,.3f}'.format
    fac_list = list(factor_tank.keys())
    print ('-'*20+' Factor Combine '+'-'*20)
    print ('Combine List: ',str(fac_list))
    IC_ts_single = pd.DataFrame()
    
    print ('Calculating IC')
    for fac in factor_tank:
        IC_ts_single[fac] = factor_tank[fac].corrwith(holding_period_ret,axis=1)

    start_ind = np.isfinite(IC_ts_single).sum(axis=1)==IC_ts_single.shape[1]
    IC_ts_single = IC_ts_single[start_ind] # chop for same starting date
    IC_mean,IC_cov = IC_ts_single.mean(),IC_ts_single.cov()
    year_min,year_max = IC_ts_single.index.year.min(),IC_ts_single.index.year.max()
    
    if test_year is not None:
        print ('Out of Sample Period: ',str(test_year),'-',str(max(IC_ts_single.index.year)))
        use_date = IC_ts_single.index.year<test_year
        last_date_idx = use_date.cumsum().argmax()
        IC_ts_single_train = IC_ts_single[use_date]
        IC_mean,IC_cov = IC_ts_single_train.mean(),IC_ts_single_train.cov()
        IC_ts_single_test = IC_ts_single[~use_date]
        IC_mean_test,IC_cov_test= IC_ts_single_test.mean(),IC_ts_single_test.cov()
    
    print ('\n1. Optimize for Max ICIR')
    IR_optimal,IC_weight_optimal = solve_weight(IC_mean,IC_cov,solve_type)
    weight_dict = dict(zip(list(factor_tank.keys()),IC_weight_optimal))
    
    print ('\n2. Factor Combine: '+ctype)
    if ctype=='join':
        factor_composite = weight_dict[fac_list[0]]*factor_tank[fac_list[0]]
        for fac in fac_list[1:]:
            factor_composite  = factor_composite + weight_dict[fac]*factor_tank[fac]
        factor_composite = NormWinsor(factor_composite)
    elif ctype=='union':
        factor_composite = factor_combine(factor_tank,weight_dict,must_have,min_fac,min_weight)
    IC_combine = pd.DataFrame(factor_composite.corrwith(holding_period_ret,axis=1),columns=['combine'])
    IC_ts = pd.concat([IC_combine,IC_ts_single],axis=1).loc[start_ind.index][start_ind]
    IC_stats = IC_stats_calc(IC_ts)
    
    IC_weight = pd.DataFrame([sum(IC_weight_optimal)]+IC_weight_optimal,index=['combine']+fac_list,columns=['weight'] )
    IC_stats_wgt = pd.concat([IC_stats,IC_weight.T],axis=0)
    
    if test_year is not None:
        IC_stats_train,IC_stats_test = IC_stats_calc(IC_ts[use_date]),IC_stats_calc(IC_ts[~use_date])
        IR_optimal_test,IC_weight_optimal_test = solve_weight(IC_mean_test,IC_cov_test,solve_type)
        IC_weight_test = pd.DataFrame([sum(IC_weight_optimal_test)]+IC_weight_optimal_test,index=['combine']+fac_list,columns=['weight'] )
        IC_stats_wgt_train = pd.concat([IC_stats_train,IC_weight.T],axis=0)
        IC_stats_wgt_test = pd.concat([IC_stats_test,IC_weight_test.T],axis=0)
        print ('\nTrain Peiord: ',str(year_min),'-',str(test_year-1))
        print (IC_stats_wgt_train.T.sort_values(by='weight',ascending=False))
        IC_stats_train = IC_stats_calc(IC_ts[use_date])
        print ('\nTest Peiord: ',str(test_year),'-',str(year_max))
        print (IC_stats_wgt_test.T.sort_values(by='weight',ascending=False))
        
    if plot:
        plt_name = 'IC Cummulative (Test Peiord: '+str(test_year)+'-'+str(year_max)+')' if test_year is not None else 'IC Cummulative'
        IC_ts.cumsum().plot(title = plt_name,figsize=[13,5])
        #plt.legend(bbox_to_anchor=(1,1), loc=5, borderaxespad=0.)
        #plt.show()
        if test_year is not None:
            plt.axvspan(IC_ts.index[last_date_idx],IC_ts.index[-1], color='b', alpha=0.1, lw=0)
        plt.show()
    IC_stats_wgt = IC_stats_wgt.T.sort_values(by='weight',ascending=False)
    print ('\n3. Optimized Result: ',str(year_min),'-',str(year_max)+'\n',IC_stats_wgt)
    print ('-'*60)
    return factor_composite,IC_stats_wgt,IC_ts


def max_icir_rolling(factor_tank,stock_close,holding_period,ic_win=20,weight_roll=None,solve_type='optimize',cov_type='sample',plot=True):
    #fac_comb_max_icir_roll = max_icir_rolling(factor_tank,stock_close,holding_period,ic_win=20,weight_roll=None,solve_type='optimize',cov_type='sample',plot=True)
    print ('-'*20,'rolling max icir','-'*20)
    print ('paramter set: ic_win=%d, weight_roll=%d, holding_period=%d'%(ic_win,1 if weight_roll is None else weight_roll,holding_period))
    print ('solve type = %s\ncov_type = %s'%(solve_type,cov_type)) #'equation'
    fac_list = list(factor_tank.keys())
    
    #fac_comb_max_icir_roll = max_icir_rolling(factor_tank,stock_close,holding_period,ic_win=20,weight_roll=None)
    holding_period_ret = stock_close.shift(-1*holding_period)/stock_close - 1
    dat_alg = align_data({'factor_tank':factor_tank,'holding_period_ret':holding_period_ret})    
    holding_period_ret,factor_tank = dat_alg['holding_period_ret'],dat_alg['factor_tank']
    print ('-'*20,'\ncalc ic')
    ic_df = batch_ic(holding_period_ret,factor_tank)
    print ('cacl rolling ic mean and ic covariance')
    ic_mean = ic_df.rolling(ic_win).mean()
    if cov_type=='sample':
        ic_cov = ic_df.rolling(ic_win).cov()
    else:
        ic_cov = calc_covariance_roll(ic_df,ic_win,cov_type)
    date_list = list(holding_period_ret.index)
    date_num,fac_num = len(date_list),len(fac_list)
    ir_list = np.zeros(date_num)
    weight_mat = np.zeros([date_num,fac_num])
    ic_mat = ic_mean.values
    ic_cov_mat = ic_cov.values
    rebal_num = date_num - holding_period
    print ('-'*20,'\nrolling optimize for %d days'%(rebal_num))
    print ('factor list:',str(fac_list))
    for idx in range(rebal_num):
        if idx%100==0:
            print (idx)#print ('block:%d-%d'%(idx,(idx+100)))
        idx_cov_start,idx_cov_end = idx*fac_num,(idx+1)*fac_num
        try:
            ir_list[idx+holding_period],weight_mat[idx+holding_period,:] = solve_weight(ic_mat[idx,:],ic_cov_mat[idx_cov_start:idx_cov_end,:],solve_type)
        except:
            continue
    #icir_in_sample = pd.DataFrame(ir_list,index=date_list)
    combine_weight = pd.DataFrame(weight_mat,index=date_list,columns=fac_list)
    print ('-'*20)
    fac_comb_max_icir_roll = factor_combine_regression(factor_tank,combine_weight,rolling_win=weight_roll,normalize=True,plot=plot)
    ic_df['combine'] = fac_comb_max_icir_roll.corrwith(holding_period_ret,axis=1)
    IC_stats = IC_stats_calc(ic_df)
    IC_weight_mean = pd.DataFrame(combine_weight.mean(axis=0),columns=['weight']).T
    IC_weight_mean = IC_weight_mean/IC_weight_mean.sum(axis=1).values[0]
    IC_weight_mean['combine'] = 1
    IC_stats_wgt = pd.concat([IC_stats,IC_weight_mean],axis=0)
    IC_stats_wgt = IC_stats_wgt.T.sort_values(by='weight',ascending=False)
    print ('rolling optimized result: ','\n',IC_stats_wgt)
    
    if plot:
        ic_df.cumsum().plot(title='ic cumsum',figsize=[11,3])
        plt.show()

    print ('-'*60)
    return fac_comb_max_icir_roll