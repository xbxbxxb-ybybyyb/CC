import sys
sys.path.append('/data/user/015614/Lucien')
from xquant.factordata import FactorData

hfactor = FactorData()
import pandas as pd
from model_eval.modelEval_Tool import *
from multiprocessing import Pool
import time

pct_group_num = 10
def deal_preddata(path, viewcol, sel_data='all'):
    pred_df = pd.read_csv(open(path)).set_index(['Indexs'])
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
    from Zeus.Europa.v1_0_31.path_conf import date_config
    PERIOD = 'period4'
    SUB_VERSION = 'v4'  # v1 v2 v3
    pred_type = 'test'   # test fit
    factor_type = 'FSV8'
    date_dict = date_config[f'{PERIOD}_{pred_type}']
    out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
    in_begin, in_end = out_begin, out_end
    # 修改为测试期区间
    # out_begin, out_end = 20191002, 20200630
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'test'

    # out_begin, out_end = 20200701, 20201231
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'fit'

    # 第二个区间
    # out_begin, out_end = 20200401, 20201231
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'test'

    # out_begin, out_end = 20210101, 20210630
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'fit'

    # 第三个区间
    # out_begin, out_end = 20201001, 20210630
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'test'

    # out_begin, out_end = 20210701, 20211231
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'fit'

    # 第四个区间test
    # out_begin, out_end = 20210401, 20211231
    # in_begin, in_end = out_begin, out_end
    # pred_type = 'test'

    # strategy_namelist = ['SaturnS3'] * 2 # 'SaturnS1
    sel_flag = 'all' # 可选SZ,SH,all
    # strategy_version = 'SaturnS3'
    strategy_version = f'fac_20221220_{factor_type}_all_pct_graded_lowCost_{PERIOD}'
    # 修改为自己的文件保存路径
    FilesavePath = '/data/user/015614/junkData/'

    # 验证集和测试集的路径，使用csv文件格式
    # pred_path_list, valid_path_list,sel_model_names,test_label_list,strategy_namelist 数量要一致，顺序要严格一一对应,分场景合并信号要在子场景之前
    # hb_model_names: 需要计算模型重合度相关信息的模型列表，需要是sel_model_names的子集
    # 分场景合并的模型名字中一定要包含'scene',且其余模型名字不能包含'scene'
    # pred_Reg中保存是是回归标签预测或者预测为1的概率
    # sel_model_names = ['filter1Model', 'filter2Model', 'filter3Model', 'method2Model']
    # sel_model_names = ['V20220927FcModel', 'V20220923FcModel', 'V20220913FcModel']
    # sel_model_names = ['V0927FilterV1FcModel', 'V0927FilterV1FcModel2', 'V0923FilterV1FcModel']
    # sel_model_names = ['all933FcModel', 'V0927Model', 'V0923Model']
    # sel_model_names = ['Filter62Model', 'FilterV1Model', 'V0927Model', 'FilterV1AlignModel']
    # sel_model_names = ['V38Model', 'V39Model', 'V40Model', 'V41Model', 'V25Model', 'V21Model']
    # sel_model_names = ['V104Model', 'V103Model', 'NewFcModel', 'OldFcModel']
    # sel_model_names = ['noRollFcModel', 'rollFcModel']
    # sel_model_names = ['LgbRSFcModel', 'XgbRSFcModel', 'oldFcModel']
    # sel_model_names = ['LgbRSFcModel', 'XgbRSFcModel', 'LrRSFcModel', 'LgbV8FcModel', 'XgbV8FcModel', 'LrV8FcModel',]
    # sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrV8FcModel', 'LgbV1FcModel', 'XgbV1FcModel', 'LrV1FcModel',]
    # sel_model_names = ['LgbV8FcModel', 'LrRSFcModel']
    # sel_model_names = ['LgbV8FcModelV1', 'LgbV8FcModelV2', 'LgbV8FcModelV3']
    # sel_model_names = ['LgbV8FcModel', 'LgbAllFcModel', 'LgbAll2FcModel']
    # sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'oldLgbV8FcModel', 'oldXgbV8FcModel', 'oldLrRSFcModel']
    # sel_model_names = ['LgbV8Hml0FcModel', 'LgbV8Hml1FcModel', 'LgbV8Hml2FcModel']
    # sel_model_names = ['XgbV8Hml0FcModel', 'XgbV8Hml1FcModel', 'XgbV8Hml2FcModel']
    # sel_model_names = ['XgbV8HmlFcModel']
    # sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel']
    # sel_model_names = ['LgbV8FcModel', 'CatV8FcModel']
    # sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel']
    # sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel', 'oldLgbV8FcModel', 'oldLrRSFcModel']
    sel_model_names = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel',
                       'JupLgbV8FcModel', 'JupXgbV8FcModel', 'JupLrRSFcModel', 'JupLgbV8HmlFcModel', 'JupXgbV8HmlFcModel',
                       'EurLgbV8FcModel', 'EurXgbV8FcModel', 'EurLrRSFcModel', 'EurLgbV8HmlFcModel', 'EurXgbV8HmlFcModel']
    hb_model_names = sel_model_names
    test_label_list = ['label_pct_cost'] * len(sel_model_names)  # 'label_pct_cost','label_v2o10d1','label_v2o10d1_new'
    strategy_namelist = ['JupiterN'] * 10 + ['Europa'] * 5  # 'SaturnS1
    # strategy_namelist = ['JupiterN'] * 5 + ['Europa'] * 5  # 'SaturnS1
    # test_label_list = ['label_pct_cost']  # 'label_pct_cost','label_v2o10d1','label_v2o10d1_new'

    pred_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']
    valid_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']

    # valid_path_list = [
    #     # f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv',
    #     # f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}_hml.csv',
    # ]

    # valid_path_list = [
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_v30.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_v31.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_v32.csv',
    # ]

    # valid_path_list = [
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_30/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_v1031.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_30/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_v1031.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_30/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}_v1031.csv',
    # ]

    # valid_path_list = [
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/Europa/v1_0_31/CatRegModel/{out_begin}~{out_end}_CatRegModel_{SUB_VERSION}.csv',
    # ]

    # valid_path_list = [
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv',
    # ]
    #
    # valid_path_list = [
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv',
    #
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_jupiter.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_jupiter.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}_jupiter.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_jupiter_hml.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_jupiter_hml.csv',
    #
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_europa.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_europa.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}_europa.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_europa_hml.csv',
    #     f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_europa_hml.csv',
    # ]

    valid_path_list = [
        f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_31/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_31/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_v3_forcmp.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/{out_begin}~{out_end}_LrRegModel_v3_forcmp.csv'
    ]
    pred_path_list = valid_path_list

    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/20210401~20211231_LrRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_old.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/20210401~20211231_LrRegModel_old.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/20210401~20211231_LrRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_old.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/20210401~20211231_LrRegModel_old.csv',
    # ]

    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/20210401~20211231_LgbRegModel_v4.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20191001~20200630_LgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20191001~20200630_LgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20191001~20200630_LgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20200401~20201231_LgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20200401~20201231_LgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20200401~20201231_LgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20201001~20210630_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20201001~20210630_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20201001~20210630_LgbRegModel_v3.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20200701~20201231_LgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20200701~20201231_LgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20200701~20201231_LgbRegModel_v1.csv'
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20210101~20210630_LgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20210101~20210630_LgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20210101~20210630_LgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_26/LgbRegModel/20210701~20211231_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_27/LgbRegModel/20210701~20211231_LgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_29/LgbRegModel/20210701~20211231_LgbRegModel_v3.csv',
    # ]


    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/prod_for_search_threshold.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/prod_for_search_threshold.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_24/LgbRegModel/prod_for_search_threshold.csv',
    #     '/data/user/015614/Zeus/pred/Europa/v1_0_25/LrRegModel/prod_for_search_threshold.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_12/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_11/20190102~20200630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_12/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_11/20190102~20201231_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_12/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_11/20190102~20200630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_12/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_17/20190102~20201231_lrRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_14/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_13/20200401~20201231_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_14/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_13/20200401~20210630_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_14/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_13/20200401~20201231_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_14/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_13/20200401~20210630_lrRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20201001~20210630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20210701~20211231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20210701~20211231_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20201001~20210630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20210701~20211231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20210701~20211231_lrRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20201001~20210630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20210701~20211231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20210701~20211231_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20201001~20210630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_16/20210701~20211231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_15/20210701~20211231_lrRegModel_v1.csv',
    # ]

    # 第一个区间
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_17/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_17/20190102~20200630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_17/20190102~20200630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_20/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_20/20190102~20200630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_20/20190102~20200630_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_17/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_17/20190102~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_17/20190102~20201231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_20/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_20/20190102~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_20/20190102~20201231_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_17/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_17/20190102~20200630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_17/20190102~20200630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_20/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_20/20190102~20200630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_20/20190102~20200630_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_17/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_17/20190102~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_17/20190102~20201231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_20/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_20/20190102~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_20/20190102~20201231_lrRegModel_v1.csv',
    # ]

    # 第二个区间
    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_18/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_18/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_18/20200401~20201231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_21/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_21/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_21/20200401~20201231_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_18/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_18/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_18/20200401~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_21/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_21/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_21/20200401~20210630_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_18/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_18/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_18/20200401~20201231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_21/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_21/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_21/20200401~20201231_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_18/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_18/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_18/20200401~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_21/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_21/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_21/20200401~20210630_lrRegModel_v1.csv',
    # ]

    # 第三个区间
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_19/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_19/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_19/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_22/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_22/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_22/20201001~20210630_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_19/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_19/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_19/20210701~20211231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_22/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_22/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_22/20210701~20211231_lrRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_19/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_19/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_19/20201001~20210630_lrRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_22/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_22/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_22/20201001~20210630_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_19/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_19/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_19/20210701~20211231_lrRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_22/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_22/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lr_reg_model/v1_0_22/20210701~20211231_lrRegModel_v1.csv',
    # ]

    # 20221102
    # valid_path_list = [
    # # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_5/20190102~20200630_lgbRegModel_v1.csv',
    # # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_5/20190102~20200630_xgbRegModel_v2.csv',
    # # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_5/20190102~20201231_lgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_5/20190102~20201231_xgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    # # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_5/20190102~20200630_lgbRegModel_v1.csv',
    # # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_5/20190102~20200630_xgbRegModel_v2.csv',
    # # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_5/20190102~20201231_lgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_5/20190102~20201231_xgbRegModel_v1.csv',
    # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_6/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_6/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_7/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_7/20200401~20201231_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_6/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_6/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_7/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_7/20200401~20210630_xgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_6/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_6/20200401~20201231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_7/20200401~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_7/20200401~20201231_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_6/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_6/20200401~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_7/20200401~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_7/20200401~20210630_xgbRegModel_v1.csv',
    # ]

    # 20221103
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_8/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_8/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_9/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_9/20201001~20210630_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_8/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_8/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_9/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_9/20210701~20211231_xgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_8/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_8/20201001~20210630_xgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_9/20201001~20210630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_9/20201001~20210630_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_8/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_8/20210701~20211231_xgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_9/20210701~20211231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/xgb_reg_model/v1_0_9/20210701~20211231_xgbRegModel_v1.csv',
    # ]

    flag = True
    for cur_file in pred_path_list:
        flag = os.path.exists(cur_file)
        if flag == False:
            print('ERROR!!!!,please check file path %s' % cur_file)
            break
        else:
            continue

    if flag == True:
        print('All files are ready!')
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
        merge_attend_pct = pd.DataFrame()
        merge_attend_revmaxdown = pd.DataFrame()
        count = 0
        for i in list(range(len(pred_path_list))):
            count = count + 1
            tmp_pred_path, tmp_valid_path = pred_path_list[i], valid_path_list[i]
            model_name = sel_model_names[i]
            model_proba1 = model_name + 'proba1'
            test_label_name = test_label_list[i]
            strategy_name = strategy_namelist[i]
            print(model_name)
            tmp_pred_df = deal_preddata(tmp_pred_path, pred_view, sel_flag)
            tmp_valid_df = deal_preddata(tmp_valid_path, valid_view, sel_flag)
            tmp_modeleval = modelEval_Tool(strategy_name, tmp_pred_df, tmp_valid_df, model_name, out_begin, out_end,
                                           in_begin, in_end,
                                           FilesavePath,test_label_name)
            attend_min, attend_max = tmp_modeleval.attend_min,tmp_modeleval.attend_max
            totalResDf_tmp, by_day_tmp, by_sample_tmp, by_day_valid_tmp, model_mingan_tmp, model_mingan_in_tmp, group_proba_tmp,totalResDf_only_extreme_tmp = tmp_modeleval.generate_series_data()
            if count == 1:
                merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp])
                merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
            else:
                merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp[[model_name,model_proba1]]], axis=1,
                                            join_axes=[merge_by_sample.index])
                basic_cols = by_day_tmp.filter(regex='基础').columns.tolist()
                merge_by_day = pd.concat([merge_by_day, by_day_tmp[sorted(list(set(by_day_tmp.columns.tolist())-set(basic_cols)))]], axis=1)
            #merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
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
                attend_pct_tmp = pd.DataFrame(model_mingan_tmp['扣费收益率'].tolist(),
                                                index=(100 * (model_mingan_tmp['实际参与率'].round(2))).astype(
                                                    int).tolist(),
                                                columns=[model_name])
                merge_attend_pct = pd.concat([merge_attend_pct, attend_pct_tmp], axis=1)

            if len(model_mingan_in_tmp) > 0:
                inmodel_pd = pd.DataFrame(index=[model_name], columns=model_mingan_in_tmp.columns.tolist())
                merge_inmodelmingan = pd.concat([merge_inmodelmingan, inmodel_pd, model_mingan_in_tmp])

            if len(group_proba_tmp) > 0:
                model_pd = pd.DataFrame(index=[model_name], columns=group_proba_tmp.columns.tolist())
                merge_group_proba = pd.concat([merge_group_proba, model_pd, group_proba_tmp])
        merge_dfall = merge_by_sample.copy()
        merge_attend_metric = pd.DataFrame()
        nan_df = pd.DataFrame(columns=merge_attend_profit.columns.tolist())
        profit_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['累计盈利'])
        maxdown_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['最大回撤'])
        revmaxdown_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['收益风险比'])
        sharp_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['收益夏普比率'])
        pct_pd = pd.DataFrame(index=merge_attend_profit.index.tolist(), columns=['扣费收益率'])
        merge_attend_profit.index.name = '累计盈利'
        merge_attend_maxdown.index.name = '最大回撤'
        merge_attend_revmaxdown.index.name = '收益风险比'
        merge_attend_sharp.index.name = '收益夏普比率'
        merge_attend_pct.index.name = '扣费收益率'
        merge_attend_metric = pd.concat(
            [profit_pd, merge_attend_profit, maxdown_pd, merge_attend_maxdown, revmaxdown_pd, merge_attend_revmaxdown,sharp_pd, merge_attend_sharp,pct_pd,merge_attend_pct],
            axis=1)
        chonghe_info_sel = pd.DataFrame()
        chonghe_info_sel_pos = pd.DataFrame()
        chonghe_info_sel_group = pd.DataFrame()
        attend_contactratio = pd.DataFrame()
        if len(sel_model_names) > 1:
            result_num, result_ratio, result_profit, result_profit_ratio, result_pct,result_ic = cal_crossmetrics(merge_dfall)
            num_pd = pd.DataFrame(index=['信号重合数量'], columns=result_num.columns.tolist())
            ratio_pd = pd.DataFrame(index=['信号重合度'], columns=result_num.columns.tolist())
            rev_pd = pd.DataFrame(index=['收益重合'], columns=result_num.columns.tolist())
            pct_pd = pd.DataFrame(index=['收益率重合'], columns=result_num.columns.tolist())
            ic_pd = pd.DataFrame(index=['IC'], columns=result_num.columns.tolist())
            chonghe_info_sel = pd.concat(
                [num_pd[hb_model_names], result_num.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
                 result_ratio.loc[hb_model_names][hb_model_names], \
                 rev_pd[hb_model_names],
                 result_profit_ratio.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
                 result_pct.loc[hb_model_names][hb_model_names],ic_pd[hb_model_names],
             result_ic.loc[hb_model_names][hb_model_names]])

            result_num_pos, result_ratio_pos, result_profit_pos, result_profit_ratio_pos, result_pct_pos,result_ic_pos = cal_crossmetrics(merge_dfall.query('label_pct_cost>0'))
            chonghe_info_sel_pos = pd.concat(
                [num_pd[hb_model_names], result_num_pos.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
                 result_ratio_pos.loc[hb_model_names][hb_model_names], \
                 rev_pd[hb_model_names],
                 result_profit_ratio_pos.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
                 result_pct_pos.loc[hb_model_names][hb_model_names],ic_pd[hb_model_names],
             result_ic_pos.loc[hb_model_names][hb_model_names]])
            merge_dfall = generate_group(merge_dfall, 'label_pct_cost', pct_group_num)
            for idx in list(range(pct_group_num)):
                merge_df_group = merge_dfall.query('group_id==%s' % str(idx + 1))
                minpct = merge_df_group.label_pct_cost.min()  # pct_list[idx]
                maxpct = merge_df_group.label_pct_cost.max()  # pct_list[idx+1]
                tmp_index = '%.4g~%.4g' % (minpct, maxpct)
                chonghe_all = merge_df_group[sel_model_names].sum(1)
                result_num_group, result_ratio_group, result_profit_group, result_profit_ratio_group, result_pct_group,_ = cal_crossmetrics(merge_df_group)
                tmp_res = pd.DataFrame(((result_ratio_group.sum(1) - 1) / (len(sel_model_names) - 1))).T
                tmp_res.index = [tmp_index]
                tmp_res.loc[tmp_index, '总数量'] = len(merge_df_group)
                tmp_res.loc[tmp_index, '%s票数量' % len(sel_model_names)] = chonghe_all[chonghe_all == len(sel_model_names)].shape[0]  # /len(merge_df_group)
                chonghe_info_sel_group = pd.concat([chonghe_info_sel_group, tmp_res])
            attend_contactratio = cal_attend_contactratio(merge_dfall,attend_min, attend_max)
        FilePath = FilesavePath + '/回测结果/'
        if not os.path.exists(FilePath):
            os.makedirs(FilePath)
            print("creat folder " + FilePath)
        writer = pd.ExcelWriter(
            FilePath + '%d~%d_%s_%s_%s_merge_%s_模型评价_%s.xlsx' % (
            out_begin, out_end, strategy_name, str(strategy_version), sel_flag, pred_type, today))

        merge_by_sample = merge_by_sample.reset_index()
        merge_by_sample.sort_values(by=['datelist'], ascending=True, inplace=True)
        merge_by_sample.to_excel(writer, sheet_name='按次')
        merge_by_day.to_excel(writer, sheet_name='按日')
        #merge_by_day_valid.to_excel(writer, sheet_name='样本内按日')
        merge_modeleval.fillna(0).to_excel(writer, sheet_name='模型结果')
        merge_modeleval_extreme.fillna(0).to_excel(writer, sheet_name='极值处理模型结果')
        merge_group_proba.to_excel(writer, sheet_name='预测值分层统计')
        #merge_inmodelmingan.to_excel(writer, sheet_name='样本内不同参与率统计')
        merge_modelmingan.to_excel(writer, sheet_name='不同参与率统计')
        merge_attend_metric.to_excel(writer, sheet_name='不同参与率指标统计')
        chonghe_info_sel.to_excel(writer, sheet_name='重合度统计')
        attend_contactratio.to_excel(writer, sheet_name='不同参与率重合度统计')
        chonghe_info_sel_pos.to_excel(writer, sheet_name='实际正收益重合度统计')
        chonghe_info_sel_group.to_excel(writer, sheet_name='收益率分层重合度统计')
        writer.save()

# 20220926对比
    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # 20220927对比，两个filter v1的对比
    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_12/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_12/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_12/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_12/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # 20220927对比，全样本对比
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_10/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # 不同因子筛选下的对比
    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_33/20190102~20200630_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_33/20190102~20200630_lgbRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_35/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_35/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_35/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_35/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_24/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # # 对比FilteV6.2 与 Filter V1 与对齐样本的等等
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_37/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_37/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v3.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v2.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_37/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v3.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20200630_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_37/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v3.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_34/20190102~20201231_lgbRegModel_v2.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v2.csv'
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v2.csv'
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v2.csv'
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v2.csv'
    # ]

    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v2.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v2.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS3/lgb_reg_model/v3_0_36/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # valid_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_2/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_0/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_2/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_0/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_2/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_0/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_2/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_1/20190102~20201231_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/Europa/lgb_reg_model/v1_0_0/20190102~20201231_lgbRegModel_v1.csv',
    # ]

    # 用于测试因子筛选
    # valid_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_38/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_39/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_40/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_41/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_38/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_39/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_40/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_41/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    # ]
    # pred_path_list = [
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_38/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_39/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_40/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_41/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20200630_lgbRegModel_v1.csv',
    #     '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_38/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_39/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_40/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_41/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_25/20190102~20201231_lgbRegModel_v1.csv',
    #     # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv',
    # ]