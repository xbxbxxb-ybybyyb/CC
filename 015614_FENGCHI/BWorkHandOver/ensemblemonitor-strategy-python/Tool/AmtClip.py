import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading'])

import pandas as pd
from online_conf import path_for_930, vol_info_path,local_config_path,init_conf_path
from dataApi.getData import get_daily_1factor, trans_int2windcode
from dataApi.indName import sw_level2,sw2021_level2
from dataApi.tradeDate import get_pre_trade_date
import shutil
from dataApi.sendInfo import send_message,send_file
import os
import configparser


ind_list = {
    20210726: ['盐湖提锂', '锂电池'],
    20210802: ['盐湖提锂', '锂电池', '半导体及元件', '光刻胶', '第三代半导体'],
    20210811: [],
    20210817: ['盐湖提锂', '光刻胶', '锂电池', '半导体及元件', '第三代半导体'],
    20210907: ['盐湖提锂', '锂电池'],
    20210924: ['盐湖提锂', '锂电池', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '水泥'],
    20211012: ['盐湖提锂', '锂电池', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '水泥', '电力'],
    20211103: ['盐湖提锂', '锂电池', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '水泥', '电力', '国防军工'],
    20211104: ['CRO概念', '盐湖提锂', '锂电池', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '水泥', '电力', '国防军工'],
    20211111: ['盐湖提锂', '锂电池', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '储能'],
    20211122: ['盐湖提锂', '锂电池', '风电', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '储能'],
    20211125: ['盐湖提锂', '锂电池', '风电', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '钢铁', '有色冶炼加工', '储能', '元宇宙'],
    20211207: ['盐湖提锂', '锂电池', '风电', '基础化学', '化工新材料', '氟化工', '磷化工', '有机硅', '有色冶炼加工', '储能', '元宇宙', '汽车零部件', '风电'],
    20211216: ['锂电池', '风电', '氟化工', '磷化工', '有机硅', '储能', '元宇宙', '汽车零部件', '风电'],
    20211217: ['NFT概念', '锂电池', '风电', '氟化工', '磷化工', '有机硅', '储能', '元宇宙', '汽车零部件', '风电'],
    20220104: ['NFT概念', '锂电池', '氟化工', '磷化工', '有机硅', '元宇宙', '汽车零部件', '风电'],
    20220112: ['NFT概念', '锂电池', '氟化工', '磷化工', '有机硅', '元宇宙', '风电'],
    20220120: ['NFT概念', '锂电池', '氟化工', '磷化工', '有机硅', '元宇宙', '风电', '中药', '汽车零部件'],
    20220208: ['氢能源', '国防军工', 'NFT概念', '虚拟数字人', '元宇宙', '中药', '汽车零部件', '胎压监测', '预制菜', '计算机应用', '计算机设备'],
    20220211: ['氢能源', 'NFT概念', '虚拟数字人', '元宇宙', '中药', '汽车零部件', '胎压监测', '预制菜', '计算机应用', '计算机设备'],
    20220214: ['氢能源', 'NFT概念', '虚拟数字人', '元宇宙', '中药', '汽车零部件', '胎压监测', '预制菜', '计算机应用', '计算机设备', '数字货币'],
    20220217: ['氢能源', 'NFT概念', '虚拟数字人', '元宇宙', '中药', '汽车零部件', '胎压监测', '预制菜', '计算机应用', '计算机设备', '数字货币', '电力设备'],
    20220223: ['半导体及元件', 'HJT电池', '氢能源', '计算机设备', '虚拟数字人', 'CRO概念', '胎压监测', '汽车电子', '消费电子', '无人驾驶', '元宇宙', '国防军工',
               '数字货币', 'NFT概念', '预制菜', '汽车零部件', '光伏概念', '中药', '第三代半导体', '电力设备', '光刻胶', '锂电池', '储能', '计算机应用'],
    20220303: ['半导体及元件', 'HJT电池', 'CRO概念', '汽车电子', '国防军工', '数字货币', '光伏概念', '第三代半导体', '电力设备',
               '光刻胶', '锂电池', '储能', '盐湖提锂', '数据中心', '培育钻石', '杭州亚运会', '共同富裕示范区'],
    20220304: ['半导体及元件', 'HJT电池', 'CRO概念', '汽车电子', '国防军工', '数字货币', '光伏概念', '第三代半导体', '电力设备',
               '光刻胶', '锂电池', '储能', '盐湖提锂', '数据中心', '培育钻石', '杭州亚运会', '共同富裕示范区', '新冠治疗'],
    20220311: ['半导体及元件', 'HJT电池', 'CRO概念', '汽车电子', '光伏概念', '第三代半导体', '电力设备',
               '光刻胶', '锂电池', '储能', '盐湖提锂', '培育钻石', '杭州亚运会', '共同富裕示范区'],
    20220318: ['盐湖提锂'],
    20220321: ['盐湖提锂','东数西算（算力）','新冠检测'],
    20220322: ['盐湖提锂','东数西算（算力）','新冠检测','建筑节能','电子身份证'],
    20220323: ['盐湖提锂','东数西算（算力）','新冠检测','新冠治疗','建筑节能','电子身份证'],


}



sw_ind_list = {
    20211013: [610201, 610303, 610304],
    20211207: [610201, 610303, 610304, 610204, 610203, 610305],
    20211208: [610201, 610303, 610304, 610204, 610203, 610305, 612801, 612803],
    20211216: [612801, 612803],
    20220208: [],
    20220223: [611502, 610803],
    20220303: [611502, 610803, 611504],
    20220304: [611502, 610803],
    20220310: [],

}
"""
影视院线、煤炭开采、电池
"""
sw2021_ind_list = {
    20220217: [464610],
    20220303: [464610, 467206],
    20220310: [464610, 467206, 464609, 466103, 467401, 466502],
    20220311: [467206, 464609, 466103, 467401,464610],
    20220318: [463702,467206,467401,466307],
    20220322: [463702,467206,467401,466307,467401],
    20220325: [463702,467206,467401,466307,467401,467302],
}
# paths = ['/data/group/800442/800319/zxf/','/data/group/800442/800319/Afengchi/概念板块同花顺/']
paths = ['/data/group/800442/800319/Afengchi/概念板块同花顺/']
def get_restrict_factor_list(today,extra_stk_list=[]):
    target_date = list(filter(lambda x: x < today, ind_list.keys()))
    if target_date:
        target_date = max(target_date)
        ind_list_ = ind_list[target_date]
    else:
        send_file(['015664'], '无减半股票')
        ind_list_ = []
    # send_message(['015664'], f'{today}减半行业{ind_list_}')

    ind_infos = {}
    left_ind = set(ind_list_)
    for path in paths:
        if not left_ind:
            break
        file_list = sorted(list(filter(lambda x: x.endswith('.json') and x.startswith('概念板块同花顺'), os.listdir(path))))
        file_list = list(filter(lambda x: x < f'概念板块同花顺{today}.json', file_list))
        ind_info = pd.read_json(f'{path}{file_list[-1]}', typ=dict)
        inter = set(left_ind).intersection(set(ind_info.keys()))
        left_ind = set(left_ind) - set(ind_info.keys())
        ind_infos.update({x:ind_info[x] for x in inter})
    for ind in left_ind:
        if os.path.exists(f'{local_config_path}/extra_restrict_list/{ind}.xlsx'):
            res = pd.read_excel(f'{local_config_path}/extra_restrict_list/{ind}.xlsx',index_col=0)
            ind_infos[ind] = dict(res['简称'])
            left_ind = left_ind - set([ind])
    if left_ind:
        send_message(['015664'],f'{today}未找到行业 {left_ind}')
    send_message(['015664'],f'{today}减半行业 {ind_infos.keys()}')

    target_stk = set()
    for ind in ind_list_:
        if ind in left_ind:
            continue
        target_stk = target_stk.union(ind_infos[ind])
    target_stk = target_stk.union(set(extra_stk_list))
    if today == 20210806:
        target_stk = target_stk - set(['601636.SH', '300014.SZ', '300712.SZ', '002108.SZ', '002407.SZ', '002335.SZ', '002140.SZ', '000009.SZ', '002760.SZ', '002738.SZ'])
    if today == 20210809:
        target_stk = target_stk - set(['300014.SZ', '300712.SZ', '601636.SH'])
    if today == 20210810:
        target_stk = target_stk - set(['601636.SH'])
    return target_stk,ind_list_

def calc_halved_vol(today,replace=False,extra_stk_list=[],target_stk=None,send_msg=False):
    if target_stk is None:
        target_stk,ind_list_ = get_restrict_factor_list(today,extra_stk_list=extra_stk_list)
    elif not (isinstance(target_stk,list) or isinstance(target_stk,set)):
        raise Exception('target stk wrong type')


    date = get_pre_trade_date(today)
    conf = configparser.ConfigParser()
    conf.read(f'{init_conf_path}{today}.ini')
    strategy_init = dict(conf['strategy_init'])
    strategy_init_930 = pd.read_pickle(f'{path_for_930}{today}/StrategyIn/init{today}.pkl')

    target_amt_fix = float(strategy_init['per_amt']) * 0.5
    target_amt_930 = float(strategy_init_930['per_amt']) * 0.5

    if not os.path.exists(f'{vol_info_path}{date}_backup.pkl'):
        shutil.copy(f'{vol_info_path}{date}.pkl', f'{vol_info_path}{date}_backup.pkl')
    if not os.path.exists(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl'):
        shutil.copy(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}.pkl',
                    f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl')
    vol = pd.read_pickle(f'{vol_info_path}{date}_backup.pkl')
    vol_930 = pd.read_pickle(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl')

    if set(vol_930.index) != set(vol.columns):
        send_message(['015664'], 'vol930 和 vol 股票列表不一致')

    involved_stk = list(target_stk.intersection(vol.columns))

    adj_factor = get_daily_1factor('adjfactor', date_list=[date]).loc[date]
    close = get_daily_1factor('close', date_list=[date]).loc[date]
    close.index = close.index.map(trans_int2windcode)
    adj_factor.index = adj_factor.index.map(trans_int2windcode)
    close = pd.Series(close.tolist(), index=close.index)
    adj_factor = pd.Series(adj_factor.tolist(), index=adj_factor.index)

    target_vol_fix = (target_amt_fix / close / adj_factor).loc[involved_stk] * 10
    target_vol_930 = (target_amt_930 / close).loc[involved_stk] * 10
    target_vol_930.index.names = vol_930.index.names
    target_vol_fix.index.names = vol.index.names

    send_message(['015664'], f'930 Target:\n{(target_vol_930 // 100 * 100 * close.loc[target_vol_930.index] * 0.1).max().max()}')
    send_message(['015664'], f'FIX Target:\n{(target_vol_fix * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1).max().max()}')

    send_message(['015664'], f'930 before: {(vol_930.loc[target_vol_930.index] // 100 * 100 * close.loc[target_vol_930.index] * 0.1).max().max()}')
    send_message(['015664'], f'Fix before: {(vol[target_vol_fix.index] * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1).max().max()}')

    vol_930.loc[target_vol_930.index] = target_vol_930
    for bar in vol.index:
        vol.loc[bar, target_vol_fix.index] = target_vol_fix

    send_message(['015664'], f'930 after: {(vol_930.loc[target_vol_930.index] // 100 * 100 * close.loc[target_vol_930.index] * 0.1).max().max()}')
    send_message(['015664'], f'Fix after: {(vol[target_vol_fix.index] * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1).max().max()}')
    if replace:
        pd.to_pickle(vol, f'{vol_info_path}{date}.pkl')
        pd.to_pickle(vol_930, f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}.pkl')
        print(vol_info_path)
        print(f'{path_for_930}{get_pre_trade_date(date, -1)}/')

        # send_message(['015664'], f'{target_vol_fix.index.tolist()}成功改变下单上限')
    return vol,vol_930,target_stk

def get_halved_profit_detail(today,out=False):
    target_stk = pd.read_pickle(f'{local_config_path}half_stk/{today}.pkl')
    detail_930 = pd.read_excel(f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}.xlsx',index_col=0)
    inter_stk = list(set(detail_930.index).intersection(target_stk))
    halved_detail_930 = detail_930.loc[inter_stk]
    fix_detail = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx',sheet_name='收益明细')
    halved_fix_detail = fix_detail[fix_detail['证券代码'].isin(target_stk)]

    if out:
        halved_fix_detail.to_excel(f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}_减半板块.xlsx')
        halved_detail_930.to_excel(f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}_减半板块.xlsx')


        send_file(['015664'],f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}_减半板块.xlsx')
        send_file(['015664'],f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}_减半板块.xlsx')
    return halved_fix_detail,halved_detail_930

def get_haved_detail(start,end):
    from dataApi.tradeDate import get_date_range
    detail_fix, detail_930 = {}, {}

    for date in get_date_range(start, end):
        detail_fix[date], detail_930[date] = get_halved_profit_detail(date)
    stat = {
        'fix_减半股票费后收益': {x: detail_fix[x]['费后收益'].sum() for x in detail_fix},
        '930_减半股票费后收益': {x: detail_930[x]['费后收益'].sum() for x in detail_930},
        'fix_减半股票数量': {x: len(set(detail_fix[x]['证券代码'])) for x in detail_fix},
        '930_减半股票数量': {x: len(set(detail_930[x].index)) for x in detail_930}
    }
    stat = pd.DataFrame(stat)
    out_file = f'/data/user/015664/AFuckingTrigger/实盘/统计减半股票当日收益_{start}_{end}.xlsx'
    with pd.ExcelWriter(out_file) as writer:
        stat.to_excel(writer, sheet_name='总览')
        for date in detail_fix:
            detail_fix[date].to_excel(writer, sheet_name=f'fix_{date}')
            detail_930[date].to_excel(writer, sheet_name=f'930_{date}')
    writer.close()
    send_file(['015664'], out_file)

if __name__ == '__main__':

    import datetime
    from dataApi.tradeDate import get_recent_trade_date
    today = 20220420#get_recent_trade_date()#int(datetime.date.today().strftime('%Y%m%d'))
    tommorrow = get_pre_trade_date(today,-1)

    if today>=20210804 and today<=20210811:
        extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx',index_col=0)
        extra_list = list(set(extra_list.index))
    elif today>=20210818 and today<20210913:
        extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx',index_col=0)
        extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
        extra_list = list(set(extra_list.index))
    elif today>=20210913 and today<20211103:
        extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx', index_col=0)
        extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
        extra_list = list(set(extra_list.index))

        sw2 = get_daily_1factor('SW2')
        target = sw2.iloc[-1]
        target = target[target == 610201].index
        target = target.map(trans_int2windcode).tolist()

        extra_list = set(extra_list).union(set(target))
    elif today>=20211103 and today<20211122:
        # extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx', index_col=0)
        # extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
        # extra_list = list(set(extra_list.index))
        extra_list = []
        sw2 = get_daily_1factor('SW2')
        target = sw2.iloc[-1]
        target = target[target == 610201].index
        target = target.map(trans_int2windcode).tolist()

        extra_list = set(extra_list).union(set(target))

    elif  today<20211217:
        extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx', index_col=0)
        extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
        extra_list = list(set(extra_list.index))
        send_message(['015664'],'减半光伏')
        # extra_list = []
    else:
        extra_list = []

    def get_sw_ind_extr(key,ind_lst,level_map):
        target_day = list(filter(lambda x : x<=today,list(ind_lst.keys())))
        target_day = max(target_day)
        sw2 = get_daily_1factor(key)
        sw2 = sw2.iloc[-1]
        sw2_extra = sw2[sw2.isin(ind_lst[target_day])].index.map(trans_int2windcode).tolist()
        sw_restrict_industry = ind_lst[target_day]  # [sw_level2[x] for x in sw_ind_list[target_day]]
        return sw2_extra,[level_map[x] for x in sw_restrict_industry],sw_restrict_industry
    sw2_ex,sw_ex_ind,ex_ind_code = get_sw_ind_extr('SW2',sw_ind_list,sw_level2)
    sw2_ex2021,sw_ex_ind2021,ex_ind_code2021 = get_sw_ind_extr('SW20212',sw2021_ind_list,sw2021_level2)

    extra_list = list(set(extra_list).union(sw2_ex).union(sw2_ex2021))
    send_message(['015664'],f'{tommorrow}SW2 {sw_ex_ind2021+sw_ex_ind}')


    stk_list,industry_list_THS = get_restrict_factor_list(tommorrow,extra_list)
    pd.to_pickle(stk_list, f'{local_config_path}half_stk/{tommorrow}.pkl')
    out_path = f'/data/group/800442/800319/restrict_industry/{today}/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    pd.to_pickle(industry_list_THS,f'{out_path}同花顺减半行业.pkl')
    pd.to_pickle(ex_ind_code+ex_ind_code2021,f'{out_path}申万二级减半行业.pkl')


    # calc_halved_vol(tommorrow, replace=True, extra_stk_list=[], target_stk=set(stk_list))




# today = 20210818
# if today>=20210804 and today<=20210811:
#     extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx',index_col=0)
#     extra_list = list(set(extra_list.index))
#     vol,vol_930,stk_list = calc_halved_vol(today,replace=True,extra_stk_list=extra_list)
#
# elif today>=20210818:
#     extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx',index_col=0)
#     extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
#     extra_list = list(set(extra_list.index))
#     vol, vol_930, stk_list = calc_halved_vol(today, replace=True, extra_stk_list=extra_list)
# else:
#     vol,vol_930,_ = calc_halved_vol(today,replace=True)

#
# extra_list = pd.read_excel(f'{local_config_path}restrict_list/20210803/光伏和稀土.xlsx',index_col=0)
# extra_list = extra_list[extra_list['概念板块'].eq('光伏')]
# extra_list = list(set(extra_list.index))
# vol, vol_930, stk_list = calc_halved_vol(today, replace=False, extra_stk_list=extra_list)
#
#

# tommorrow = get_pre_trade_date(tommorrow)

# target_stk = set(stk_list)#stk_list
# stk_930 = pd.read_pickle(f'{local_config_path}morning_model/val_sign/{tommorrow}.pkl')
# pre_holding = pd.read_pickle(f'{path_for_930}{get_pre_trade_date(tommorrow)}/StrategyOut/holding{get_pre_trade_date(tommorrow)}.pkl')
# target_stk.intersection(stk_930.index) - set(pre_holding.keys())
# code_list= pd.read_pickle(f'{local_config_path}code_list/{get_pre_trade_date(today)}.pkl')
# len(set(code_list).intersection(target_stk))

# today = 20211018

