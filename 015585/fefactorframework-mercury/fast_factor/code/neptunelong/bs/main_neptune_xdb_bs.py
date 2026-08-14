import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.neptune.bs.function_factor_xdb_bs import *
from itertools import product
import copy

dic_property = {
    'monetarycap': f_pro_monetarycap,
    'acctrcv': f_pro_acctrcv,
    'prepay': f_pro_prepay,
    'othrcv': f_pro_othrcv,
    'inventories': f_pro_inventories,
    'totcurassets': f_pro_totcurassets,
    'longtermeqyinvest': f_pro_longtermeqyinvest,
    'fixassets': f_pro_fixassets,
    'intangassets': f_pro_intangassets,
    'deferredtaxassets': f_pro_deferredtaxassets,
    'totnoncurassets': f_pro_totnoncurassets,
    'totassets': f_pro_totassets,
    'stborrow': f_pro_stborrow,
    'acctpayable': f_pro_acctpayable,
    'emplbenpayable': f_pro_emplbenpayable,
    'taxessurchargespayable': f_pro_taxessurchargespayable,
    'totcurliab': f_pro_totcurliab,
    'totnoncurliab': f_pro_totnoncurliab,
    'totliab': f_pro_totliab,
    'caprsrv': f_pro_caprsrv,
    'surplusrsrv': f_pro_surplusrsrv,
    'undistributedprofit': f_pro_undistributedprofit,
    'totshrhldreqyexclminint': f_pro_totshrhldreqyexclminint,
    'totshrhldreqyinclminint': f_pro_totshrhldreqyinclminint,
    'totliabshrhldreqy': f_pro_totliabshrhldreqy,
    'accountsreceivablebill': f_pro_accountsreceivablebill,
    'accountspayable': f_pro_accountspayable,
    'othrcvtot': f_pro_othrcvtot,
    'stmbstot': f_pro_stmbstot,
    'othpayabletot': f_pro_othpayabletot,
    # 组合类
    'ldbl': f_pro_ldbl, # 流动比率
    'sdbl': f_pro_sdbl,
    'fzqybl': f_pro_fzqybl,
    'zcggl': f_pro_zcggl,
    'gdqybl': f_pro_gdqybl,
    'gdzcbl': f_pro_gdzcbl,
    'wxzcbl': f_pro_wxzcbl,
    'zbgjbl': f_pro_zbgjbl,
    'lcsybl': f_pro_lcsybl,
               }
col_filter = ['ANN_DT','report_period','MDDate','STATEMENT_TYPE',
              'MONETARY_CAP','ACCT_RCV','OTH_RCV','PREPAY',
              'INVENTORIES','TOT_CUR_ASSETS','LONG_TERM_EQY_INVEST','FIX_ASSETS','INTANG_ASSETS','DEFERRED_TAX_ASSETS','TOT_NON_CUR_ASSETS',
              'TOT_ASSETS','ST_BORROW','ACCT_PAYABLE','EMPL_BEN_PAYABLE','TAXES_SURCHARGES_PAYABLE','TOT_CUR_LIAB','TOT_NON_CUR_LIAB','TOT_LIAB',
              'CAP_RSRV','SURPLUS_RSRV','UNDISTRIBUTED_PROFIT','TOT_SHRHLDR_EQY_EXCL_MIN_INT','TOT_SHRHLDR_EQY_INCL_MIN_INT',
              'TOT_LIAB_SHRHLDR_EQY','ACCOUNTS_RECEIVABLE_BILL','ACCOUNTS_PAYABLE','OTH_RCV_TOT','STM_BS_TOT','OTH_PAYABLE_TOT',]
dic_season = {
    'cum':f_t_kind_cum, # 累计值，直接取原始值
    'single':f_t_kind_single, # 单季度值，先全部变为单季度值
    'single1':f_t_kind_single1, # 单季度值，不额外处理一季度
    'ratiocum':f_t_kind_ratiocum, # 累计值同比
    'ratiosingle':f_t_kind_ratiosingle, # 单季度同比
                }
rolling_list = [4,8,12]
dic_calc = {
            'max':f_calc_max,
            'min':f_calc_min,
            'avg':f_calc_avg,
            'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            'change':f_calc_change,
            'm2m':f_calc_m2m,
            'std':f_calc_std
           }
# 计算
list_del = []
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250428_xdb_balancesheet_cs/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250512_xdb_balancesheet_cs/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250516_xdb_balancesheet_cs/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
#
strategy = 'neptune'
for season, rolling_day, property \
        in product(dic_season, rolling_list, dic_property):
    list_class = []
    for calc_i in dic_calc:
        # if (cancel_kind3_i == '0') & (cancel_type3_i == 'smaller'):
        #     continue  # 剔除“小于全部价格”的因子
        factor_name_final = f'{season}_{rolling_day}_{property}_{calc_i}'
        factor_need_column = dic_pro_column[property]
        if factor_name_final in list_del:
            continue
        print(factor_name_final)
        generate_class_code = '''
class factor_{}(BaseFactor):
    strategy_name = "neptune"
    factor_name = factor_name_final
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "test"  # 因子逻辑解释
    zcz_adjusted = "是"  # 是否针对注册制调整：是/否
    logic_type = "test"  # 逻辑类别
    low_cost = "是"  # 是否低耗时
        '''.format(factor_name_final)
        exec(generate_class_code)
        t_day_data = []
        xdb_data = [
            {
       'name': 'xdb_balancesheet_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 18 # 回看日期，N为往前回看1~N天
            }
        ]
        exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
        exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
        exec('factor_{}.calc_i = calc_i'.format(factor_name_final))
        exec('factor_{}.need_column = factor_need_column'.format(factor_name_final))
        def pre_calculate_T_N_data(self, database):
            if database["skip"] == True:
                database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                return database
            else:
                fin_df = database['xdb_balancesheet_cs']
                def get_report_period(x):
                    month = x[4:6]
                    if month == '03':
                        return 1
                    elif month == '06':
                        return 2
                    elif month == '09':
                        return 3
                    elif month == '12':
                        return 4
                    else:
                        return 5
                fin_df['report_period'] = fin_df['MDDate'].apply(get_report_period)
                fin_df = fin_df[col_filter]
                #
                if season == 'cum':
                    fin_df1 = dic_season[season](fin_df)
                else:
                    fin_df1 = dic_season[season](fin_df, self.need_column)
                fin_df2 = dic_property[property](fin_df1)
                fin_df3 = fin_df2.groupby(['dt','Ticker'])['factor'].apply(lambda x : dic_calc[self.calc_i](x.tail(rolling_day))).to_frame(name = self.factor_name)
                database['pre_T_N'] = fin_df3[[self.factor_name]]  # cs要返回df
                return database
        def prepare_T_data(self, database):
            if database["skip"] == True:
                return database
            else:
                return database
        def calculate(self, database):
            if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
                return pd.Series({self.factor_name: np.nan})
            else:
                res1 = database['pre_T_N']
                return res1
        exec('factor_{}.pre_calculate_T_N_data = copy.deepcopy(pre_calculate_T_N_data)'.format(factor_name_final))
        exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
        exec('factor_{}.calculate = calculate'.format(factor_name_final))
        exec('list_class.append(copy.deepcopy(factor_{}))'.format(factor_name_final))
    # raise
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20160101, end_date=20191231, strategy=strategy,
                         output_dir=f"/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/{strategy}/20250526_xdb_balancesheet_cs/",
                         options={
                             "calc.num_cpus": 24,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": True,
                             'report':False,
                             'mode': RunMode.research},class_list_out=list_class)
        # for factor_class in list_class:
        #     i = factor_class.factor_name
        #     print(i)
        #     print('score:', check_res[i + '_' + strategy]['check_score_res'].loc['score','tot_score'])
        #     print('IC:',check_res[i + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])


