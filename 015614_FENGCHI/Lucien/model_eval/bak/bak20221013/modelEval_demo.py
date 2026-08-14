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
    rawdata = rawdata.fillna(0)
    data = rawdata.filter(regex='Model') # 根据个人命名方式进行修改
    result_num = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    result_ratio = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
    #result_ratio_pos = pd.DataFrame(index=data.columns.tolist(), columns=data.columns.tolist())
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
    return result_num.T, result_ratio.T, result_profit.T, result_profit_ratio.T, result_pct.T#,result_ratio_pos.T
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
    out_begin, out_end = 20191008, 20200630
    in_begin, in_end = 20190102, 20190930
    # out_begin, out_end = 20200701, 20201231
    # in_begin, in_end = 20200201, 20200630
    strategy_name = 'SaturnS1'
    sel_flag = 'all' # 可选SZ,SH,all
    strategy_version = 'fac_20220927_FSV8_all_v2o10d1'
    pred_type = 'test'  # 可选test，fit
    # pred_type = 'fit'  # 可选test，fit
    # 修改为自己的文件保存路径
    FilesavePath = '/data/user/015614/junkData/'

    # 验证集和测试集的路径，使用csv文件格式
    # pred_path_list, valid_path_list,sel_model_names,test_label_list 数量要一致，顺序要严格一一对应,分场景合并信号要在子场景之前
    # hb_model_names: 需要计算模型重合度相关信息的模型列表，需要是sel_model_names的子集
    # 分场景合并的模型名字中一定要包含'scene',且其余模型名字不能包含'scene'
    # pred_Reg中保存是是回归标签预测或者预测为1的概率
    # sel_model_names = ['filter1Model', 'filter2Model', 'filter3Model', 'method2Model']
    # sel_model_names = ['V20220927FcModel', 'V20220923FcModel', 'V20220913FcModel']
    sel_model_names = ['V32FcModel']
    hb_model_names = sel_model_names
    test_label_list = ['label_pct_cost',]  # 'label_pct_cost','label_v2o10d1','label_v2o10d1_new'

    pred_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']
    valid_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']

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
    valid_path_list = [
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20200630_lgbRegModel_v1.csv',
        '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20201231_lgbRegModel_v1.csv',
    ]
    pred_path_list = [
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20200630_lgbRegModel_v1.csv',
        '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20200630_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_28/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_29/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_30/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_31/20190102~20201231_lgbRegModel_v1.csv',
        # '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_32/20190102~20201231_lgbRegModel_v1.csv',
    ]
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
        count = 0
        for i in list(range(len(pred_path_list))):
            count = count + 1
            tmp_pred_path, tmp_valid_path = pred_path_list[i], valid_path_list[i]
            model_name = sel_model_names[i]
            test_label_name = test_label_list[i]

            print(model_name)
            tmp_pred_df = deal_preddata(tmp_pred_path, pred_view, sel_flag)
            tmp_valid_df = deal_preddata(tmp_valid_path, valid_view, sel_flag)
            tmp_modeleval = modelEval_Tool(strategy_name, tmp_pred_df, tmp_valid_df, model_name, out_begin, out_end,
                                           in_begin, in_end,
                                           FilesavePath,test_label_name)
            totalResDf_tmp, by_day_tmp, by_sample_tmp, by_day_valid_tmp, model_mingan_tmp, model_mingan_in_tmp, group_proba_tmp,totalResDf_only_extreme_tmp = tmp_modeleval.generate_series_data()
            if count == 1:
                merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp])
            else:
                merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp[[model_name]]], axis=1,
                                            join_axes=[merge_by_sample.index])
            merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
            merge_by_day_valid = pd.concat([merge_by_day_valid, by_day_valid_tmp], axis=1)
            merge_modeleval = pd.concat([merge_modeleval, totalResDf_tmp], axis=1)
            merge_modeleval_extreme = pd.concat([merge_modeleval_extreme, totalResDf_only_extreme_tmp], axis=1)

            if len(model_mingan_tmp) > 0:
                model_pd = pd.DataFrame(index=[model_name], columns=model_mingan_tmp.columns.tolist())
                merge_modelmingan = pd.concat([merge_modelmingan, model_pd, model_mingan_tmp])

            if len(model_mingan_in_tmp) > 0:
                inmodel_pd = pd.DataFrame(index=[model_name], columns=model_mingan_in_tmp.columns.tolist())
                merge_inmodelmingan = pd.concat([merge_inmodelmingan, inmodel_pd, model_mingan_in_tmp])
            if len(group_proba_tmp) > 0:
                model_pd = pd.DataFrame(index=[model_name], columns=group_proba_tmp.columns.tolist())
                merge_group_proba = pd.concat([merge_group_proba, model_pd, group_proba_tmp])
        merge_dfall = merge_by_sample.copy()
        chonghe_info_sel = pd.DataFrame()
        chonghe_info_sel_pos = pd.DataFrame()
        chonghe_info_sel_group = pd.DataFrame()
        if len(sel_model_names) > 1:
            result_num, result_ratio, result_profit, result_profit_ratio, result_pct = cal_crossmetrics(merge_dfall)
            num_pd = pd.DataFrame(index=['信号重合数量'], columns=result_num.columns.tolist())
            ratio_pd = pd.DataFrame(index=['信号重合度'], columns=result_num.columns.tolist())
            rev_pd = pd.DataFrame(index=['收益重合'], columns=result_num.columns.tolist())
            pct_pd = pd.DataFrame(index=['收益率重合'], columns=result_num.columns.tolist())
            chonghe_info_sel = pd.concat(
                [num_pd[hb_model_names], result_num.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
                 result_ratio.loc[hb_model_names][hb_model_names], \
                 rev_pd[hb_model_names],
                 result_profit_ratio.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
                 result_pct.loc[hb_model_names][hb_model_names]])

            result_num_pos, result_ratio_pos, result_profit_pos, result_profit_ratio_pos, result_pct_pos = cal_crossmetrics(merge_dfall.query('label_pct_cost>0'))
            chonghe_info_sel_pos = pd.concat(
                [num_pd[hb_model_names], result_num_pos.loc[hb_model_names][hb_model_names], ratio_pd[hb_model_names],
                 result_ratio_pos.loc[hb_model_names][hb_model_names], \
                 rev_pd[hb_model_names],
                 result_profit_ratio_pos.loc[hb_model_names][hb_model_names], pct_pd[hb_model_names],
                 result_pct_pos.loc[hb_model_names][hb_model_names]])
            merge_dfall = generate_group(merge_dfall, 'label_pct_cost', pct_group_num)
            for idx in list(range(pct_group_num)):
                merge_df_group = merge_dfall.query('group_id==%s' % str(idx + 1))
                minpct = merge_df_group.label_pct_cost.min()  # pct_list[idx]
                maxpct = merge_df_group.label_pct_cost.max()  # pct_list[idx+1]
                tmp_index = '%.4g~%.4g' % (minpct, maxpct)
                chonghe_all = merge_df_group[sel_model_names].sum(1)
                result_num_group, result_ratio_group, result_profit_group, result_profit_ratio_group, result_pct_group = cal_crossmetrics(merge_df_group)
                tmp_res = pd.DataFrame(((result_ratio_group.sum(1) - 1) / (len(sel_model_names) - 1))).T
                tmp_res.index = [tmp_index]
                tmp_res.loc[tmp_index, '总数量'] = len(merge_df_group)
                tmp_res.loc[tmp_index, '%s票数量' % len(sel_model_names)] = chonghe_all[chonghe_all == len(sel_model_names)].shape[0]  # /len(merge_df_group)
                chonghe_info_sel_group = pd.concat([chonghe_info_sel_group, tmp_res])
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
        merge_by_day_valid.to_excel(writer, sheet_name='样本内按日')
        merge_modeleval.fillna(0).to_excel(writer, sheet_name='模型结果')
        merge_modeleval_extreme.fillna(0).to_excel(writer, sheet_name='极值处理模型结果')
        merge_group_proba.to_excel(writer, sheet_name='预测值分层统计')
        merge_inmodelmingan.to_excel(writer, sheet_name='样本内不同参与率统计')
        merge_modelmingan.to_excel(writer, sheet_name='不同参与率统计')
        chonghe_info_sel.to_excel(writer, sheet_name='重合度统计')
        chonghe_info_sel_pos.to_excel(writer, sheet_name='实际正收益重合度统计')
        chonghe_info_sel_group.to_excel(writer, sheet_name='收益率分层重合度统计')
        writer.save()