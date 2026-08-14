"""
coding: utf-8
CreateDate: 2023/8/4 13:44
Location: HTSC
Author: ZhangWenhu
"""

TOTAL_STRATEGY_NAME ={'Buy':['JupiterN','Europa','Metis','Saturn'],
                      'Sell':['JupiterNSell','JupiterZSell','JupiterNSell_pct5']}

INTERVAL_END_DATE = [20201231, 20210630, 20211231]

Continuous_Thres=[0,20,25,30,35,40,45,50]
Discreted_Thres=[1,2,3,4,5,6]


JupiterN_Config={
    'profit_file': '/data/group/800463/sunss/profit/jupiter/20230810/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5',
    'signal_Q1':'/data/group/800463/wangj/save_files/Jupiter_v9/Jupiter_out_testfit_v9_fac_20221220_maxbeta_final_noroll_merge6models_20230116.csv',
    'signal_Q2':'/data/group/800463/wangj/save_files/Jupiter_v9/Jupiter_realout_testfit_v9_fac_20221220_maxbeta_final_noroll_merge6models_20230116.csv',
    'signal_Q3':'/data/group/800463/wangj/save_files/Jupiter_v9/Jupiter_realrealout_testfit_v9_fac_20221220_maxbeta_final_noroll_merge6models_20230116.csv',
    'voting': {'thres': 4, 'voter_num':6,'voter_columns':['vote_sum_pred']},
    'pct_name':'pct',
    'cost_pct':0.002,
}

Europa_Config={
    'profit_file': '/data/group/800463/sunss/profit/europa/20230810/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5',
    'signal_Q1':'/data/group/800463/wangj/save_files/Europa_v3/Europa_out_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv',
    'signal_Q2': '/data/group/800463/wangj/save_files/Europa_v3/Europa_realout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv',
    'signal_Q3': '/data/group/800463/wangj/save_files/Europa_v3/Europa_realrealout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv',
    'voting': {'thres': 3, 'voter_num':6,'voter_columns':['vote_sum_pred']},
    'pct_name': 'pct',

    'cost_pct':0.002,
}

Metis_Config={
    'profit_file': '/data/group/800463/sunss/metis/20230805/profit/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5',
    'pct_name': 'pct',
    'cost_pct':0.002,
}

Saturn_Config={
    'profit_file': '/data/group/800463/project/project2_prod/factor_bank/all_factor_20220712/filter_v2/profit/p2_profit_0.25_0.10_500_1500_20160101_20211231.h5',
    'signal_Q1':'/data/group/800463/wangj/save_files/SaturnS1_v6/signal/SaturnS1_out_20191001_20200701_20201231_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv',
    'signal_Q2':'/data/group/800463/wangj/save_files/SaturnS1_v6/signal/SaturnS1_out_20200401_20210101_20210630_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv',
    'signal_Q3':'/data/group/800463/wangj/save_files/SaturnS1_v6/signal/SaturnS1_out_20201001_20210701_20211231_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv',
    'voting':{'thres':3,'voter_num':6,'voter_columns':[]},
    'pct_name': 'pct',
    'cost_pct':0.004,
}

JupiterNSell_Config={
    'profit_file':'/data/group/800463/sunss/profit/sell/20230810/Sell_pct_0.10_800_190_SH300_SZ30.pkl',
    'signal_Q1': '/data/group/800463/wangj/save_files/Europa_v3/sell/sell12_out_combine_europabuySignal_maxbeta_merge6models_eur.csv',
    'signal_Q2': '/data/group/800463/wangj/save_files/Europa_v3/sell/sell12_realout_combine_europabuySignal_maxbeta_merge6models_eur.csv',
    'signal_Q3': '/data/group/800463/wangj/save_files/Europa_v3/sell/sell12_realrealout_combine_europabuySignal_maxbeta_merge6models_eur.csv',
    'voting':{'thres':4,'voter_num':6,'voter_columns':['vote_sum_pred']},
    'pct_name': 'label_diff_pct',
    'cost_pct':0.0,

}

JupiterZSell_Config={
    'profit_file': '/data/group/800463/wangj/save_files/Europa_v3/sell/jupiterZ/Europa_with_JupiterZ_profitdata_foreur_SH300_SZ30.pkl',
    'pct_name': 'pct',
    'cost_pct':0.0,

}

Sapphire1_Config={
    'profit_file':'//data/group/800463/sunss/profit/sapphire/20230810/Sell_sapphire1_0.15_2000_300_SH250_SZ20.h5',
    'pct_name': 'label_diff_pct',
    'cost_pct':0.000,
}

Sapphire2_Config={
    'profit_file':'/data/group/800463/sunss/profit/sapphire/20230810/Sell_sapphire2_0.15_2000_300_SH250_SZ20.h5',
    'pct_name': 'label_diff_pct',
    'cost_pct':0.000,
}

Sapphire3_Config={
    'profit_file':'/data/group/800463/sunss/profit/sapphire/20230810/Sell_sapphire3_0.15_2000_300_SH250_SZ20.h5',
    'pct_name': 'label_diff_pct',
    'cost_pct':0.000,
}