# coding: utf-8
# Author：fengchi863
# Date ：2023/4/23 23:21

from xquant.factordata import FactorData

hfactor = FactorData()
import pandas as pd
from model_eval.modelEval_Tool import *
from multiprocessing import Pool
import time
import sys

model_indicator = 'Model'
pct_group_num = 10
def deal_preddata(path, viewcol, sel_data='all'):
    pred_df = pd.read_csv(open(path)).set_index(['Indexs'])#.query('jupiterN_signal>=3')
    pred_df['datelist'] = [int(i.split(' ')[1]) for i in pred_df.index.tolist()]
    pred_df['stockID'] = [i.split(' ')[0] for i in pred_df.index.tolist()]
    pred_df['Flag_SH'] = [1 if x.split('.')[-1] == 'SH' else 0 for x in pred_df['stockID'].tolist()]
    if sel_data == 'all':
        pass
    elif sel_data == 'SH':
        pred_df = pred_df.query('Flag_SH == 1')
    elif sel_data == 'SZ':
        pred_df = pred_df.query('Flag_SH == 0')
    pred_df = pred_df.reset_index()
    pred_df['Indexs'] = pred_df['stockID'].astype(str) + ' ' + pred_df['datelist'].astype(str)
    pred_df.set_index(['Indexs'], inplace=True)
    pred_df = pred_df[viewcol]
    return pred_df
# 计算模型重合度相关指标
def cal_crossmetrics(rawdata):
    rawdata.rename(columns={'盈亏金额(扣除成本)': 'label_profit_cost', '收益率(扣除成本)': 'label_pct_cost'}, inplace=True)
    data = rawdata[list(set(rawdata.filter(regex='Model').columns.tolist()) - set(
        rawdata.filter(regex='proba1').columns.tolist()))]
    #data = rawdata.filter(regex='Model')
    '''if len(data)== 0:
        data = rawdata.filter(regex='_pred')'''
    result_num = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    result_ratio = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())

    result_profit = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    result_profit_ratio = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    result_pct = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    for col1 in data.columns.tolist():
        for col2 in data.columns.tolist():
            tempdata = data[[col1, col2]]
            result_num.loc[col1, col2] = tempdata.query(col1 + '==1 and ' + col2 + '==1').shape[0]
            result_profit.loc[col1, col2] = rawdata.loc[
                tempdata.query(col1 + '==1 and ' + col2 + '==1').index].label_profit_cost.sum()
            result_pct.loc[col1, col2] = rawdata.loc[
                tempdata.query(col1 + '==1 and ' + col2 + '==1').index].label_pct_cost.mean()
            result_ratio.loc[col1, col2] = 0
            result_profit_ratio.loc[col1, col2] = 0
            if tempdata.query(col1 + '==1').shape[0] > 0:
                result_ratio.loc[col1, col2] = tempdata.query(col1 + '==1 and ' + col2 + '==1').shape[0] / \
                                               tempdata.query(col1 + '==1').shape[0]
                result_profit_ratio.loc[col1, col2] = rawdata.loc[tempdata.query(
                    col1 + '==1 and ' + col2 + '==1').index].label_profit_cost.sum() / rawdata.loc[
                                                          tempdata.query(col1 + '==1').index].label_profit_cost.sum()
    result_ic = rawdata.filter(regex='proba1').corr('spearman')
    result_ic.columns = [x.split('proba1')[0] for x in result_ic.columns.tolist()]
    result_ic.index = [x.split('proba1')[0] for x in result_ic.index.tolist()]

    return result_num.T, result_ratio.T, result_profit.T, result_profit_ratio.T,result_pct.T,result_ic.T

def generate_group(df,fac_col,group_num=pct_group_num):
    df = df.sort_values(by=fac_col)
    group_size = int(np.floor(df.shape[0] / group_num))
    group_indicator = []
    for num in list(range(group_num)):
        if num < group_num - 1:
            group_indicator = group_indicator + group_size * [num + 1]
        else:
            group_indicator = group_indicator + (len(df) - (group_num - 1) * group_size) * [num + 1]
    df['group_id'] = group_indicator
    return df
def cal_attend_contactratio(sel_raw_data,attend_min, attend_max, step=1):
    sel_models = sorted(list(set(sel_raw_data.filter(regex='Model').columns.tolist())-set(sel_raw_data.filter(regex='proba1').columns.tolist())))
    group_ratio_indi = list(range(attend_min, attend_max, step))
    attend_data = pd.DataFrame(index=sel_raw_data.index, columns = sel_models)
    for tmp_model in sel_models:
        factor = tmp_model +  'proba1'
        sel_data = sel_raw_data.sort_values(by=factor, ascending=False)
        totalnum = sel_data.shape[0]
        attend_data[tmp_model] = 0
        group_indicator = []
        for group_indi_str in group_ratio_indi:
            ratio_num = math.ceil(totalnum * group_indi_str / 100)
            if group_indi_str == attend_min:
                tmp_num = ratio_num
            elif ratio_num >= totalnum:
                tmp_num = totalnum - math.ceil(totalnum * (group_indi_str - 1) / 100)
            else:
                tmp_num = ratio_num - math.ceil(totalnum * (group_indi_str - 1) / 100)

            group_indicator = group_indicator + tmp_num * [group_indi_str]
        group_indicator = group_indicator + (totalnum - len(group_indicator)) * [group_indi_str + 1]
        tmp_groupid = pd.Series(group_indicator, index = sel_data.index)
        attend_data[tmp_model] = tmp_groupid
    plot_data = pd.DataFrame(index=group_ratio_indi, columns = sel_models)
    for group_indi_str in group_ratio_indi:

        for col1 in sel_models:
            tmp_attend_length = attend_data.query('%s<=%s'%(col1, group_indi_str)).shape[0]
            tmp_contact_ratio = 0
            for col2 in sel_models:
                if col1 == col2:
                    pass
                else:
                    tmp_col12 = attend_data.query('%s<=%s and %s <= %s'%(col1,group_indi_str,col2, group_indi_str)).shape[0]/tmp_attend_length
                    tmp_contact_ratio = tmp_contact_ratio + tmp_col12
            plot_data.loc[group_indi_str,col1] = tmp_contact_ratio/(len(sel_models)-1)
    return plot_data
def change_index(data):
    h5data = data.reset_index()
    h5data['dt'] = [pd.Timestamp(x) for x in h5data['dt'].tolist()]
    h5data['datelist'] = h5data.apply(lambda x: int(x['dt'].to_pydatetime().strftime("%Y%m%d")), axis=1)
    h5data['stockID'] = h5data['Ticker']
    h5data['Indexs'] = h5data.apply(lambda x: x['Ticker'] + ' ' + x['dt'].to_pydatetime().strftime("%Y%m%d"), axis=1)
    h5data.drop(columns=['dt', 'Ticker'], inplace=True)
    h5data.set_index(['Indexs'], inplace=True)
    h5data = h5data.sort_values(by=['datelist', 'stockID'])
    return h5data

def cal_model_mingan_basedout(sel_raw_data, factor,threslist,  modelname, predthes=0, cost_pct=0.002):
    sel_data = sel_raw_data.sort_values(by=factor, ascending=False)
    ret_plot_data = pd.DataFrame()

    if 'label_profit_cost' not in sel_data.columns.tolist():
        sel_data['label_profit_cost'] = (sel_data['label_pct'] - cost_pct) * sel_data['label_buy_amt']
    if 'label_binary_pctcost' not in sel_data.columns.tolist():
        sel_data['label_binary_pctcost'] = sel_data.apply(lambda x: 1 if x['label_pct'] >= cost_pct else 0, axis=1)
    for idx in list(range(len(threslist) - 1)):
        minvalue, maxvalue = threslist[idx], threslist[idx + 1]
        group_indi_str = '%s~%s' % (str(int(minvalue / 1000)), str(int(maxvalue / 1000)))
        if modelname == 'basic':
            #print('basic')
            group_df = sel_data.query('%s>=%s and %s<%s' % (factor, str(minvalue), factor, str(maxvalue)))
        else:
            group_df = sel_data.query('%s>=%s and %s<%s' % (factor, str(minvalue), factor, str(maxvalue))).query(
                '%s>=%s' % (modelname, predthes))
        trade_df = group_df.query('label_buy_amt>0')
        plot_data = pd.DataFrame(index=[group_indi_str])
        if predthes == 0:
            trade_df = group_df.copy()
        plot_data.loc[group_indi_str, '数量'] = len(group_df)
        plot_data.loc[group_indi_str, '扣费胜率'] = round(trade_df['label_binary_pctcost'].mean(), 4)
        plot_data.loc[group_indi_str, '扣费收益率'] = round(trade_df['label_pct_cost'].mean(), 4)
        plot_data.loc[group_indi_str, '扣费收益率中位数'] = round(trade_df['label_pct_cost'].median(), 4)
        if predthes > 0:
            plot_data.loc[group_indi_str, '成交率'] = 0 if len(group_df) ==0 else round(len(trade_df) / len(group_df), 4)
        ret_plot_data = pd.concat([ret_plot_data, plot_data])
    return ret_plot_data
ZTTime_list = [93000000, 93100000, 93500000, 94000000, 95000000, 100000000, 103000000, 110000000, 113000000, 133000000,140000000, 143000000]
def change_date(df):
    df['last_dt'] = df['datelist'].apply(lambda x: int(hfactor.tradingday(str(x),-2)[0]))
    df['next_dt'] = df['datelist'].apply(lambda x: int(hfactor.tradingday(str(x), 2)[-1]))
    df['last_Indexs'] = df['stockID'] + ' ' + df['last_dt'].astype(str) # 修改jupZ
    df['next_Indexs'] = df['stockID'] + ' ' + df['next_dt'].astype(str) # 修改jupN
    return df.reset_index()
if __name__ == "__main__":

    '''modelEval_Tool参数说明：
    # 调用方式：modelEval_Tool(strategy_name,pred_data,valid_data,indi_str,begindate, enddate,in_begindate, in_enddate,savepath,scene_flag='')
    # strategy_name: 可选strategy_name: 策略名称：可选(SaturnS0,SaturnS1,CeresS0,CeresS1,JupiterN,Europa)
    # pred_data: 预测数据，索引为Index格式(eg. 603880.SH 20200630)，至少包括列名：['datelist','stockID','prediction','pred_Reg']
    # valid_data: 验证数据，索引为Index格式(eg. 603880.SH 20200630)，至少包括列名：['datelist','stockID','prediction','pred_Reg']
    # indi_str: 模型名称标识,其中分场景合并的模型名字中一定要包含'scene',且其余模型名字不能包含'scene'
    # begindate，enddate: 模型评估开始时间，模型评估结束时间
    # in_begindate，in_enddate: 验证集开始时间，验证集结束时间
    # savepath: 评估文件保存路径
    # scene_flag: 分场景模型标志，目前均默认不分场景，不传入 '''

    ''' test demo '''
    # 修改为测试期区间
    # from Zeus.JupiterZ.v1_0_5.path_conf import date_config
    from Zeus.Sapphire.v1_0_0.path_conf import date_config

    if len(sys.argv) > 1:
        PERIOD = sys.argv[1]
        SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
        pred_type = sys.argv[2]  # test fit
    else:
        PERIOD = 'period1'
        SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
        pred_type = 'test'   # test fit

    date_dict = date_config[f'{PERIOD}']
    out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']  # 20201001,20210630#20210101,20210630#20210101,20210630#20191001, 20200630  # 20210101,20210630#20200701,20201231#20191001,20200630#20191001,20200630#20210101,20210630#20200701, 20201231#20191001, 20200630# 220210101,20210630#  #2运行时间必须先样本外，在完全样本外
    in_begin, in_end = out_begin, out_end  # 20191231, 20201231  # 20190101,20190930#20191231,20201231#20190630, 20200630#20180920,20190930#
    # strategy_name = f'JupiterZSell_eur_pred1_{PERIOD[-1]}' # %s_%s_%s_%s （1）策略名：JupiterZSell；（2）买入信号：jup，eur；(3):买入信号：all,pred1（4）时间区间：1,2,3 只需要填写最后一个字段
    strategy_name = f'JupiterNSell_sapphire3_pred1_{PERIOD[-1]}' # %s_%s_%s_%s （1）策略名：JupiterZSell；（2）买入信号：jup，eur；(3):买入信号：all,pred1（4）时间区间：1,2,3 只需要填写最后一个字段
    op_strategy_name, period_num = strategy_name.split('_')[1], strategy_name.split('_')[-1]
    print(op_strategy_name, period_num)

    # strategy_version = 'fac_20230415'  # 'all_scene_V6_20220913_FSV6_wj'
    strategy_version = 'fac_20230810_v102'
    sel_flag = 'all'
    FilesavePath = '/data/user/015614/junkData/'

    # sel_model_names = [
    #     # 'rffs_lowCost_LgbRegModel',
    #     # 'fsv8_lowCost_LgbRegModel',
    #     'fsv10_lowCost_LgbRegModel',
    #     # 'fsv11_lowCost_LgbRegModel',
    #     'fsv8_afterZ_lowCost_LgbRegModel',
    #     # 'rffs_afterZ_lowCost_LgbRegModel',
    #     # 'fsv10_afterZ_lowCost_LgbRegModel',
    #     # 'fsv11_afterZ_lowCost_LgbRegModel',
    #
    #     # 'rffs_lowCost_XgbRegModel',
    #     # 'fsv8_lowCost_XgbRegModel',
    #     # 'fsv10_lowCost_XgbRegModel',
    #     # 'fsv11_lowCost_XgbRegModel',
    #     # 'fsv8_afterZ_lowCost_XgbRegModel',
    #     # 'rffs_afterZ_lowCost_XgbRegModel',
    #     # 'fsv10_afterZ_lowCost_XgbRegModel',
    #     # 'fsv11_afterZ_lowCost_XgbRegModel',
    # ]
    sel_model_names = ['fsv8_pct_XgbRegModel', 'fsv10_pct_XgbRegModel', 'fsv11_pct_XgbRegModel', 'fsrs_pct_XgbRegModel',
                       'fsv8_pct_after_XgbRegModel', 'fsv10_pct_after_XgbRegModel', 'fsv11_pct_after_XgbRegModel', 'fsrs_pct_after_XgbRegModel',
                       # 'fsv8_pct_LgbRegModel', 'fsv10_pct_LgbRegModel', 'fsv11_pct_LgbRegModel', 'fsrs_pct_LgbRegModel',
                       ]

    # indi_str = 'all_wj_pred'  # 'all_wjreg_pred'

    # 验证集和测试集的路径，使用csv文件格式
    # pred_path_list, valid_path_list,sel_model_names 数量要一致，顺序要严格一一对应,分场景合并信号要在子场景之前
    # 分场景合并的模型名字中一定要包含'scene',且其余模型名字不能包含'scene'
    # pred_Reg中保存是是回归标签预测或者预测为1的概率

    pred_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']
    valid_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']

    # pred_path_list = [f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_5/{x}/{out_begin}~{out_end}_{x}_{SUB_VERSION}.csv' for x in sel_model_names]
    pred_path_list = [f'/data/user/015614/Zeus/pred/Sapphire/v1_0_2/{x}/{out_begin}~{out_end}_{x}_{SUB_VERSION}.csv' for x in sel_model_names]

    # pred_path_list = [
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv8_all_LgbRegModel/{out_begin}~{out_end}_fsv8_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/rffs_lowCost_LgbRegModel/{out_begin}~{out_end}_rffs_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv10_all_LgbRegModel/{out_begin}~{out_end}_fsv10_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv8_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv8_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/rffs_all_LgbRegModel/{out_begin}~{out_end}_rffs_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv11_all_LgbRegModel/{out_begin}~{out_end}_fsv11_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv10_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv10_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv11_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv11_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv8_afterZ_all_LgbRegModel/{out_begin}~{out_end}_fsv8_afterZ_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv8_afterZ_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv8_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/rffs_afterZ_lowCost_LgbRegModel/{out_begin}~{out_end}_rffs_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv10_afterZ_all_LgbRegModel/{out_begin}~{out_end}_fsv10_afterZ_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv11_afterZ_all_LgbRegModel/{out_begin}~{out_end}_fsv11_afterZ_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/rffs_afterZ_all_LgbRegModel/{out_begin}~{out_end}_rffs_afterZ_all_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv10_afterZ_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv10_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterZ/v1_0_1/fsv11_afterZ_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv11_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    # ]

    # fac_20230425
    # pred_path_list = [
    #     '/data/user/013550/Jupiter/test_001/v2/v20230317/jupiterz/diff_pct/out/20190930~20201231_[ModelGeneralStrong@regressiongbtree_xgb]_二分类TNO2ULRollTSweight_allreg_FSV8_sel_1__.csv',
    # ]
    strategy_namelist = [strategy_name] * len(pred_path_list)
    flag = True
    for cur_file in pred_path_list:
        flag = os.path.exists(cur_file)
        if flag == False:
            print('ERROR!!!!,please check file path %s' % cur_file)
            break
        else:
            continue

    '''trainFL = [cmd5, cmd6, cmd7, cmd8]

    s = time.time()

    print ('順序:') #顺序执行(也就是串行执行，单进程)
    for fn in preFL:
        run(fn)
    t1 = time.time()
    print ("顺序执行时间：", int(t1 - s))

    print('concurrent dataprocessing:')  # 创建多个进程，并行执行
    pool = Pool(10)  # 创建拥有10个进程数量的进程池
    # testFL:要处理的数据列表，run：处理testFL列表中数据的函数
    pool.map(run, preFL)
    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()  # 主进程阻塞等待子进程的退出
    t2 = time.time()
    print("并行执行时间：", int(t2 - s))'''

if flag == True:
    print('All files are ready!')


    test_label_list = ['label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost',
                       'label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost',
                       'label_pct_cost','label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost',
                       'label_pct_cost','label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost', 'label_pct_cost',][:len(pred_path_list)]

    merge_by_sample = pd.DataFrame()
    merge_by_day = pd.DataFrame()
    merge_by_day_valid = pd.DataFrame()
    merge_modeleval = pd.DataFrame()
    merge_modeleval_extreme = pd.DataFrame()
    merge_modelmingan = pd.DataFrame()
    merge_inmodelmingan = pd.DataFrame()
    merge_group_proba = pd.DataFrame()
    merge_attend_profit = pd.DataFrame()
    merge_attend_maxdown = pd.DataFrame()
    merge_attend_sharp = pd.DataFrame()
    merge_attend_revmaxdown = pd.DataFrame()
    merge_attend_precision = pd.DataFrame()
    merge_attend_pct = pd.DataFrame()
    merge_attend_pctm = pd.DataFrame()

    count = 0
    for i in list(range(len(pred_path_list))):
        count = count + 1
        tmp_pred_path, tmp_valid_path = pred_path_list[i], pred_path_list[i]
        model_name = sel_model_names[i]
        model_proba1 = model_name + 'proba1'
        label_name = test_label_list[i]
        strategy_name = strategy_namelist[i]
        print(model_name)
        tmp_pred_df = deal_preddata(tmp_pred_path, pred_view)
        tmp_valid_df = deal_preddata(tmp_valid_path, valid_view)#.query('jupiterN_signal>=3')
        print(len(tmp_pred_df))
        tmp_modeleval = modelEval_Tool(strategy_name, tmp_pred_df, tmp_valid_df, model_name, out_begin, out_end,
                                       in_begin, in_end,
                                       FilesavePath, label_name)
        attend_min, attend_max = tmp_modeleval.attend_min, tmp_modeleval.attend_max
        totalResDf_tmp, by_day_tmp, by_sample_tmp, by_day_valid_tmp, model_mingan_tmp, model_mingan_in_tmp, group_proba_tmp, totalResDf_only_extreme_tmp = tmp_modeleval.generate_series_data()
        if count == 1:
            merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp])
            merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
        else:
            merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp[[model_name, model_proba1]]], axis=1,
                                        join_axes=[merge_by_sample.index])
            basic_cols = by_day_tmp.filter(regex='基础').columns.tolist()
            merge_by_day = pd.concat(
                [merge_by_day, by_day_tmp[sorted(list(set(by_day_tmp.columns.tolist()) - set(basic_cols)))]],
                axis=1)
        # merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
        merge_by_day_valid = pd.concat([merge_by_day_valid, by_day_valid_tmp], axis=1)
        merge_modeleval = pd.concat([merge_modeleval, totalResDf_tmp], axis=1)
        merge_modeleval_extreme = pd.concat([merge_modeleval_extreme, totalResDf_only_extreme_tmp], axis=1)

        if len(model_mingan_tmp) > 0:
            model_pd = pd.DataFrame(index=[model_name], columns=model_mingan_tmp.columns.tolist())
            merge_modelmingan = pd.concat([merge_modelmingan, model_pd, model_mingan_tmp])
            attend_profit_tmp = pd.DataFrame(model_mingan_tmp['累计盈利'].tolist(),
                                             index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                 int).tolist(),
                                             columns=[model_name])
            # attend_profit_tmp_tmp = attend_profit_tmp.copy()
            merge_attend_profit = pd.concat([merge_attend_profit, attend_profit_tmp], axis=1)
            attend_maxdown_tmp = pd.DataFrame(model_mingan_tmp['最大回撤'].tolist(),
                                              index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                  int).tolist(),
                                              columns=[model_name])
            merge_attend_maxdown = pd.concat([merge_attend_maxdown, attend_maxdown_tmp], axis=1)
            attend_revmaxdown_tmp = pd.DataFrame(model_mingan_tmp['收益风险比'].tolist(),
                                                 index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                     int).tolist(),
                                                 columns=[model_name])
            merge_attend_revmaxdown = pd.concat([merge_attend_revmaxdown, attend_revmaxdown_tmp], axis=1)
            attend_sharp_tmp = pd.DataFrame(model_mingan_tmp['收益夏普比率'].tolist(),
                                            index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                int).tolist(),
                                            columns=[model_name])
            merge_attend_sharp = pd.concat([merge_attend_sharp, attend_sharp_tmp], axis=1)
            attend_precision_tmp = pd.DataFrame(model_mingan_tmp['扣费收益率胜率'].tolist(),
                                                index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                    int).tolist(),
                                                columns=[model_name])
            merge_attend_precision = pd.concat([merge_attend_precision, attend_precision_tmp], axis=1)
            attend_pct_tmp = pd.DataFrame(model_mingan_tmp['扣费收益率'].tolist(),
                                          index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                              int).tolist(),
                                          columns=[model_name])
            merge_attend_pct = pd.concat([merge_attend_pct, attend_pct_tmp], axis=1)
            attend_pctm_tmp = pd.DataFrame(model_mingan_tmp['扣费收益率中位数'].tolist(),
                                           index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                               int).tolist(),
                                           columns=[model_name])
            merge_attend_pctm = pd.concat([merge_attend_pctm, attend_pctm_tmp], axis=1)

        if len(model_mingan_in_tmp) > 0:
            inmodel_pd = pd.DataFrame(index=[model_name], columns=model_mingan_in_tmp.columns.tolist())
            merge_inmodelmingan = pd.concat([merge_inmodelmingan, inmodel_pd, model_mingan_in_tmp])
        if len(group_proba_tmp) > 0:
            model_pd = pd.DataFrame(index=[model_name], columns=group_proba_tmp.columns.tolist())
            merge_group_proba = pd.concat([merge_group_proba, model_pd, group_proba_tmp])

    FilePath = FilesavePath + '/回测结果/'
    if not os.path.exists(FilePath):
        os.makedirs(FilePath)
        print("creat folder " + FilePath)
    merge_df = merge_by_sample.copy().reset_index()
    merge_df['Indexs'] = merge_df['stockID'].astype(str) + ' ' + merge_df['datelist'].astype(str)
    merge_df.set_index(['Indexs'], inplace=True)
    profit_data = tmp_modeleval.profit_data  # pd.concat([tmp_modeleval.valid_data.filter(regex='label*'),tmp_modeleval.pred_data.filter(regex='label*')])
    labeldata = pd.read_pickle(tmp_modeleval.label_path)
    labeldata = change_index(labeldata)
    merge_dfall1 = pd.concat(
        [merge_df[list(set(merge_df.columns.tolist()) - set(profit_data.columns.tolist()))], profit_data],
        axis=1).reindex(merge_df.index)  # , join_axes=[merge_df.index])
    merge_dfall1['ZT_Time'] = labeldata.loc[merge_dfall1.index, 'ZT_Time']

    timedf = cal_model_mingan_basedout(merge_dfall1, 'ZT_Time', ZTTime_list, 'basic')
    timedf.columns = ['基础' + x for x in timedf.columns.tolist()]
    for tmp_model in sel_model_names:
        vote3_timedf = cal_model_mingan_basedout(merge_dfall1, 'ZT_Time', ZTTime_list, tmp_model, 1)
        vote3_timedf.columns = ['%s_' % tmp_model + x for x in vote3_timedf.columns.tolist()]
        timedf = pd.concat([timedf, vote3_timedf], axis=1)
        timedf['%s_参与率'% tmp_model] = timedf['%s_数量' % tmp_model] / timedf['基础数量']
    timedf.to_excel(FilePath + '%s_%s_%s_ZT_Time_merge%dmodels_%s.xlsx'%(out_begin,out_end,strategy_name,len(sel_model_names),today))
    merge_dfall = merge_by_sample.copy()
    merge_attend_metric = pd.DataFrame()
    nan_df = pd.DataFrame(columns=merge_attend_profit.columns.tolist())
    profit_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['累计盈利'])
    maxdown_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['最大回撤'])
    revmaxdown_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['收益风险比'])
    sharp_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['收益夏普比率'])
    precision_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['扣费收益率胜率'])
    merge_attend_profit.index.name = '累计盈利'
    merge_attend_maxdown.index.name = '最大回撤'
    merge_attend_revmaxdown.index.name = '收益风险比'
    merge_attend_sharp.index.name = '收益夏普比率'
    merge_attend_precision.index.name = '扣费收益率胜率'
    merge_attend_pct.index.name = '扣费收益率'
    merge_attend_pctm.index.name = '扣费收益率中位数'
    merge_attend_metric = pd.concat(
        [profit_pd, merge_attend_profit, maxdown_pd, merge_attend_maxdown, revmaxdown_pd,
         merge_attend_revmaxdown, sharp_pd, merge_attend_sharp, precision_pd, merge_attend_precision,
         merge_attend_pct, merge_attend_pctm],
        axis=1)
    chonghe_info_sel = pd.DataFrame()
    chonghe_info_sel_pos = pd.DataFrame()
    chonghe_info_sel_group = pd.DataFrame()
    attend_contactratio = pd.DataFrame()
    if len(sel_model_names) > 1:
        result_num, result_ratio, result_profit, result_profit_ratio, result_pct, result_ic = cal_crossmetrics(
            merge_dfall)
        num_pd = pd.DataFrame(index=['信号重合数量'], columns=result_num.columns.tolist())
        ratio_pd = pd.DataFrame(index=['信号重合度'], columns=result_num.columns.tolist())
        rev_pd = pd.DataFrame(index=['收益重合'], columns=result_num.columns.tolist())
        pct_pd = pd.DataFrame(index=['收益率重合'], columns=result_num.columns.tolist())
        ic_pd = pd.DataFrame(index=['IC'], columns=result_num.columns.tolist())
        hb_model_names = sel_model_names  # ['hmlWjModel_v8','hmlWjModel_v9']#sel_model_names#['hml_wjv8_pred', 'hml_wjv9_pred']#sel_model_names  # ['open_wjv3_pred','open_wjv3test_pred']#sel_model_names#['pct5_wjv2_pred','pct5_wjv3_pred','open_wjv2_pred','open_wjv3_pred']

        chonghe_info_sel = pd.concat(
            [num_pd[hb_model_names], result_num.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
             result_ratio.loc[hb_model_names][hb_model_names], \
             rev_pd[hb_model_names],
             result_profit_ratio.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
             result_pct.loc[hb_model_names][hb_model_names], ic_pd[hb_model_names],
             result_ic.loc[hb_model_names][hb_model_names]])
        result_num_pos, result_ratio_pos, result_profit_pos, result_profit_ratio_pos, result_pct_pos, result_ic_pos = cal_crossmetrics(
            merge_dfall.query('label_pct_cost>0'))
        chonghe_info_sel_pos = pd.concat(
            [num_pd[hb_model_names], result_num_pos.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
             result_ratio_pos.loc[hb_model_names][hb_model_names], \
             rev_pd[hb_model_names],
             result_profit_ratio_pos.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
             result_pct_pos.loc[hb_model_names][hb_model_names], ic_pd[hb_model_names],
             result_ic_pos.loc[hb_model_names][hb_model_names]])
        merge_dfall = generate_group(merge_dfall, 'label_pct_cost', pct_group_num)
        for idx in list(range(pct_group_num)):
            merge_df_group = merge_dfall.query(
                'group_id==%s' % str(idx + 1))
            minpct = merge_df_group.label_pct_cost.min()  # pct_list[idx]
            maxpct = merge_df_group.label_pct_cost.max()  # pct_list[idx+1]
            tmp_index = '%.4g~%.4g' % (minpct, maxpct)
            # merge_df_group = merge_dfall.query('label_pct_cost>%s and label_pct_cost<=%s'%(str(minpct),str(maxpct)))
            chonghe_all = merge_df_group[sel_model_names].sum(1)
            result_num_group, result_ratio_group, result_profit_group, result_profit_ratio_group, result_pct_group, _ = cal_crossmetrics(
                merge_df_group)
            tmp_res = pd.DataFrame(((result_ratio_group.sum(1) - 1) / (len(sel_model_names) - 1))).T
            tmp_res.index = [tmp_index]
            tmp_res.loc[tmp_index, '总数量'] = len(merge_df_group)
            tmp_res.loc[tmp_index, '%s票数量' % len(sel_model_names)] = \
                chonghe_all[chonghe_all == len(sel_model_names)].shape[0]  # /len(merge_df_group)
            chonghe_info_sel_group = pd.concat([chonghe_info_sel_group, tmp_res])
        attend_contactratio = cal_attend_contactratio(merge_dfall, attend_min, attend_max)


    writer = pd.ExcelWriter(
        FilePath + '%d~%d_%s_%s_%s_merge_%s_%d模型评价_%s.xlsx' % (
            out_begin, out_end, strategy_name, str(strategy_version), sel_flag, pred_type, len(sel_model_names), today))

    merge_by_sample = merge_by_sample.reset_index()
    merge_by_sample.sort_values(by=['datelist'], ascending=True, inplace=True)
    merge_by_sample.to_excel(writer, sheet_name='按次')
    merge_by_day.to_excel(writer, sheet_name='按日')
    merge_modeleval.fillna(0).to_excel(writer, sheet_name='模型结果')
    merge_modeleval_extreme.fillna(0).to_excel(writer, sheet_name='极值处理模型结果')
    merge_group_proba.to_excel(writer, sheet_name='预测值分层统计')
    merge_modelmingan.to_excel(writer, sheet_name='不同参与率统计')
    merge_attend_metric.to_excel(writer, sheet_name='不同参与率指标统计')
    chonghe_info_sel.to_excel(writer, sheet_name='重合度统计')
    attend_contactratio.to_excel(writer, sheet_name='不同参与率重合度统计')
    chonghe_info_sel_pos.to_excel(writer, sheet_name='实际正收益重合度统计')
    chonghe_info_sel_group.to_excel(writer, sheet_name='收益率分层重合度统计')
    timedf.to_excel(writer, sheet_name='突破时间分组统计')
    writer.save()