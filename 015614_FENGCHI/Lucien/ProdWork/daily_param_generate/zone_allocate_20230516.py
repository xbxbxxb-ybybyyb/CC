import datetime, os
import json, shutil
import zipfile
import pandas as pd

def trans_json(date, flag, write_param_path, mock_list, zone_dict_shsz):
    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, bytes):
                    return str(obj, encoding='utf-8')
                return json.JSONEncoder.default(self, obj)
            except UnicodeDecodeError:
                pass
    param_path = r'/data/group/800463/xiely/daily/daily-param/%s-prod-O45-%s-new' % (date, flag)
    amt_cols = ['NL1目标金额', 'NL2目标金额', 'NL3目标金额', 'NL4目标金额', 'NL5目标金额', 'NewL1目标金额', 'NewL2目标金额', 'NewL3目标金额', 'NewL4目标金额', 'NewL5目标金额', 'NL1目标金额_add', 'NL2目标金额_add', 'NL3目标金额_add', 'NL4目标金额_add', 'NL5目标金额_add']
    for filename in os.listdir(param_path):
        with open(param_path + '/' + filename) as f:
            params = json.load(f)
        filename_new = filename
        if params['股票代码'] in mock_list:
            for ac in amt_cols:
                params[ac] = "1"
            params['单票持仓总规模上限'] = "50"
            params['新时点触发价格'] = "0"
            params['最大涨跌幅度'] = "-0.1"
            params['是否触发预热'] = "1"
            params['小单测试'] = "1"
            params['是否验证模式'] = "0"
            filename_new = filename.replace('.json', '') + '#'+zone_dict_shsz[params['股票代码']] + '.json'
            with open(write_param_path + '/' + filename_new, 'w', encoding='utf-8') as f:
                jsonObj = json.dumps(params, cls=MyEncoder, ensure_ascii=False, indent=2)
                f.write(jsonObj)

def generate_mock_zuhe_sh(sh_mock_param_df,date):
    zuhe_df = sh_mock_param_df.copy()
    zuhe_df.index.rename('证券代码',inplace=True)
    zuhe_df['买入交易账户'] = '2000000100'
    zuhe_df['卖出交易账户'] = '2000000100'
    zuhe_df['买入证券数量'] = '10000000'
    zuhe_df['卖出证券数量'] = zuhe_df['期初可用仓位']
    zuhe_df = zuhe_df[['买入交易账户','卖出交易账户','买入证券数量','卖出证券数量']]
    print(zuhe_df.shape)
    zuhe_commonPath = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-mock/'
    for filename in os.listdir(zuhe_commonPath):
        os.remove(os.path.join(zuhe_commonPath,filename))
    zuhe_df.to_excel(zuhe_commonPath + 'mock-O45组合-SH-'+date+'.xlsx',header=True, encoding='gbk')


def generate_mock_zuhe_sz(sz_mock_param_df,date):
    zuhe_df = sz_mock_param_df.copy()
    zuhe_df.index.rename('证券代码',inplace=True)
    zuhe_df['买入交易账户'] = '20000002'
    zuhe_df['卖出交易账户'] = '20000002'
    zuhe_df['买入证券数量'] = '10000000'
    zuhe_df['卖出证券数量'] = zuhe_df['期初可用仓位']
    zuhe_df = zuhe_df[['买入交易账户','卖出交易账户','买入证券数量','卖出证券数量']]
    print(zuhe_df.shape)
    zuhe_commonPath = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-mock/'
    zuhe_df.to_excel(zuhe_commonPath + 'mock-O45组合-SZ-'+date+'.xlsx',header=True, encoding='gbk')
       
def exec_train_json(date):
    factor_param = pd.read_pickle('/data/group/800463/param/factor_param/N_all_factor_zt_merge_v2212_%s.pkl' %date).reset_index('dt').drop('dt',axis=1)
    param_excel = pd.read_excel(r'/data/group/800463/param/param/param-%s-prod-O45.xlsx'%date)
    param_excel = param_excel[~((param_excel['saturn历史因子'].fillna('') != '') | (param_excel['ceres历史因子'].fillna('') != '') | (param_excel['sell历史因子'].fillna('') != '') | (param_excel['期初可用仓位']>0)| (param_excel['前一日是否收盘涨停']==1))]
    factor_param = factor_param.loc[param_excel['股票代码']]
    factor_param = factor_param.sort_values('Circu_Mkt', ascending=False)
    top_stock_list_sh = factor_param.loc[factor_param.index.str.endswith('.SH')].head(4).index.tolist()
    top_stock_list_sz = factor_param.loc[factor_param.index.str.endswith('.SZ')].head(4).index.tolist()
    pd.Series(top_stock_list_sh+top_stock_list_sz).to_excel(r'/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_sp_%s.xlsx'%date)
    zone_list_sh = ['302101','302103','302105','302106']
    zone_list_sz = ['302204','302205','302206','302207']
    zone_dict_sh = dict(zip(top_stock_list_sh, zone_list_sh))
    zone_dict_sz = dict(zip(top_stock_list_sz, zone_list_sz))
    zone_dict_shsz = dict(zone_dict_sh, **zone_dict_sz)

    write_param_path = r'/data/group/800463/xiely/daily/daily-param/%s-prod-O45-mock'%(date)
    if os.path.exists(write_param_path):
        shutil.rmtree(write_param_path)
    os.mkdir(write_param_path)
    
    trans_json(date, 'SH', write_param_path, top_stock_list_sh + top_stock_list_sz, zone_dict_shsz)
    trans_json(date, 'SZ', write_param_path, top_stock_list_sh + top_stock_list_sz, zone_dict_shsz)
    generate_mock_zuhe_sh(param_excel[param_excel['股票代码'].isin(top_stock_list_sh)].set_index('股票代码'), date)
    generate_mock_zuhe_sz(param_excel[param_excel['股票代码'].isin(top_stock_list_sz)].set_index('股票代码'), date)
    def zip_ya(start_dir):
        start_dir = start_dir  # 要压缩的文件夹路径
        file_news = start_dir + '.zip'  # 压缩后文件夹的名字
        z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
        for dir_path, dir_names, file_names in os.walk(start_dir):
            f_path = dir_path.replace(os.path.dirname(start_dir), '')  # 这一句很重要，不replace的话，就从根目录开始复制
            f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
            for filename in file_names:
                z.write(os.path.join(dir_path, filename), f_path + filename)
        z.close()
        return file_news
    zip_ya(write_param_path)

today = datetime.datetime.today().strftime('%Y%m%d')
exec_train_json(today)


