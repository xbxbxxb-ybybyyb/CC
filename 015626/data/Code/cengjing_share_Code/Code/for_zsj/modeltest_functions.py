def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

def get_open_amt(ticker = '000906'):
    data = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_'+ticker+'.pkl',compression='gzip')
    amt = data.xs(int(ticker),level=1)[['minute','amt']]
    amt_df = amt.reset_index().set_index(['dt','minute'])['amt'].unstack()
    amt_df = amt_df/1e8
    amt_sum = amt_df.cumsum(axis=1)
    mnew = amt_sum[925]
    mnew = mnew.reset_index()
    mnew['dt'] = mnew['dt'].apply(lambda x:pd.Timestamp(str(x)))
    mnew = mnew.set_index('dt')
    return mnew

def change_sig(sigpath, adj):
    open_amt = get_open_amt('000906')
    open_amt_norm = rolling_normalize(open_amt,60)*adj + 1
    open_amt_norm.columns = ['open_amt_norm']
    
    sig = pd.read_hdf(sigpath)*2-1
    sig.name = 'test'
    sig = pd.DataFrame(sig)

    sig1 = pd.concat([sig,open_amt_norm],axis=1)
    sig1 = sig1.sort_index()
    sig1['open_amt_norm']=sig1['open_amt_norm'].fillna(method='pad')
    sig1= sig1[sig1.index.hour!=0]

    sig_adj=(sig1['open_amt_norm']*sig1['test']).to_frame()
    sig_adj.columns = [sigpath.split('/')[-1][:-3]]
    return sig_adj





save_root_path = '/data/user/015626/data/share/factor/back_test/IC_ts/20201202_changesig/'
sigrootpath = '/data/user/012315/share/ts/strategy/minute/res_20201201/ic/'

pos_dict = {(0, 0.4): (0.0, 0.0),
                 (0.4, 0.5): (0.0, 0.2/3),
                 (0.5, 0.6): (0.2/3, 0.4/3),
                 (0.6, 0.7): (0.4/3, 0.6/3),
                 (0.7, 0.8): (0.6/3, 0.8/3),
                 (0.8, 0.9): (0.8/3, 1.0/3),
                 (0.9, 2.1): (1.0/3, 1.0/3)}

            
def get_change_sig_result(para):
    sigtype = para[0]
    adj = para[1]
    h5 = para[2]
    
    sigpath = os.path.join(sigrootpath, sigtype)
    
    
    factor_path = os.path.join(sigpath, h5)
    print(factor_path)

    factor = change_sig(factor_path, adj)

    name_prefix = 'start_20200701'
    save_path = os.path.join(save_root_path, sigtype + '_' + str(adj), name_prefix, h5[:-3])
    TS_BACK_TEST(factor.loc['20200701':],price_kind='twap',ticker='IC.CFE', slippage=0.6, initial_cash=50000000, save_path = save_path, name_prefix = name_prefix,
              pos_dict=pos_dict, capital_use_rate = 1,stop_loss = -0.005).back_test()

    name_prefix = '20200401_20201127'
    save_path = os.path.join(save_root_path, sigtype + '_' + str(adj), name_prefix, h5[:-3])
    TS_BACK_TEST(factor.loc['20200401':'20201127'],price_kind='twap',ticker='IC.CFE', slippage=0.6, initial_cash=50000000, save_path = save_path, name_prefix = name_prefix,
              pos_dict=pos_dict, capital_use_rate = 1,stop_loss = -0.005).back_test()

#     name_prefix = '20150601_20200401'
#     save_path = os.path.join(save_root_path, sigtype + '_' + str(adj), name_prefix, h5[:-3])
#     TS_BACK_TEST(factor.loc['20150601':'20200401'],price_kind='twap',ticker='IF.CFE', slippage=0.4, initial_cash=50000000, save_path = save_path, name_prefix = name_prefix,
#               pos_dict=pos_dict, capital_use_rate = 1,stop_loss = -0.005).back_test()

    name_prefix = '20170101_20200401'
    save_path = os.path.join(save_root_path, sigtype + '_' + str(adj), name_prefix, h5[:-3])
    TS_BACK_TEST(factor.loc['20170101':'20200401'],price_kind='twap',ticker='IC.CFE', slippage=0.6, initial_cash=50000000, save_path = save_path, name_prefix = name_prefix,
              pos_dict=pos_dict, capital_use_rate = 1,stop_loss = -0.005).back_test()
        
sigtypelist = ['base_prod','base_prod_nd']
adjlist = [0.5]

paralist = []
for x in sigtypelist:
    for y in adjlist:
        for z in os.listdir(os.path.join(sigrootpath, x)):
            paralist.append([x, y, z])
        
from multiprocessing import Pool

with Pool(23) as pool:
    pool.map(get_change_sig_result, paralist)
    



# 以下为整理所有结果
import glob
# save_root_path = '/data/user/015626/data/share/factor/back_test/IC_ts/20201201_changesig/'
for sigtype in os.listdir(save_root_path):
    for startdate in os.listdir(os.path.join(save_root_path, sigtype)):
        spath = os.path.join(save_root_path, sigtype, startdate)
        
        pathlist = glob.glob(spath+'/*/*results.csv')
        resultlist = []
        for path in pathlist:
            d = pd.read_csv(path, index_col = 0, encoding='gbk')
            d.columns = [path.split('/')[-2] + '_'+path.split('/')[-4].split('_')[-1]]
            resultlist.append(d)
        results = pd.concat(resultlist, axis = 1)
        results.to_csv(os.path.join(spath, spath.split('/')[-1]+'all_model_results.csv'), encoding='gbk')
        
        pathlist = glob.glob(spath+'/*/*daily_return.csv')
        dflist = []
        for path in pathlist:
            d = pd.read_csv(path, index_col = 0)
            d = d[['daily_return']]
            d.columns = [path.split('/')[-2] + '_'+path.split('/')[-4].split('_')[-1]]
            dflist.append(d.cumsum())
        results = pd.concat(dflist, axis = 1)
        results.to_csv(os.path.join(spath, spath.split('/')[-1]+ 'all_model_daily_pnl.csv'))
        
        results.plot(figsize=(20,10), grid = True)
        plt.savefig(os.path.join(spath, spath.split('/')[-1]+ 'all_model_daily_pnl.png'))