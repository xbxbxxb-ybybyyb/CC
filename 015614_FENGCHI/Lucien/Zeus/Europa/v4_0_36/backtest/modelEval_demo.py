import sys
sys.path.append('/data/user/015614/Lucien')
from xquant.factordata import FactorData

hfactor = FactorData()
import pandas as pd
from Zeus.Europa.v4_0_36.backtest.modelEval_Tool import *
from Zeus.Europa.v4_0_36.path_conf import version, bt_out_path
from multiprocessing import Pool
import time

pct_group_num = 10
def deal_preddata(path, viewcol, sel_data='all'):
    pred_df = pd.read_csv(open(path)).set_index(['Indexs']) # 卖出为标签

    # # index_duiqi = pd.read_csv('/data/user/015614/Zeus/pred/Europa/v4_0_362/LgbRegModel/20210701~20211231_LgbRegModel_v4.csv', index_col=0) # period4
    # index_duiqi = pd.read_csv('/data/user/015614/Zeus/pred/Europa/v4_0_366/LgbRffsRegModel/20220401~20220930_LgbRffsRegModel_v5.csv', index_col=0)
    # sell_profit = pd.read_pickle('/data/group/800463/wangj/save_files/Europa_v3/sell/sell12_profitdata_foreur_SH300_SZ30.pkl')
    # # sell_profit = pd.read_pickle('/data/group/800463/wangj/save_files/Europa_v3/sell/sell23_profitdata_foreur_SH300_SZ30.pkl')
    # sell_profit['stockID'] = sell_profit.index.get_level_values(1)
    # sell_profit['zt_dt_int'] = sell_profit['dt_last_zt_1_ts'].apply(lambda x: x.strftime('%Y%m%d'))
    # sell_profit['new_Indexs'] = sell_profit[['stockID', 'zt_dt_int']].apply(lambda x: x['stockID'] + ' ' + x['zt_dt_int'], axis=1)
    # sell_profit = sell_profit.set_index('new_Indexs')
    # index_duiqi = index_duiqi.loc[list(set(index_duiqi.index).intersection(set(sell_profit.index.tolist())))].sort_index()
    # index_duiqi['sell_datelist'] = sell_profit.loc[index_duiqi.index]['sell_dt'].map(lambda x: int(x.strftime('%Y%m%d')))
    # # index_duiqi = pd.read_csv('/data/group/800463/wangj/save_files/buySignal/sell12_realrealrealout_combine_europabuySignal_wjmodels_eur.csv', index_col=0)
    # index_duiqi['sell_Indexs'] = index_duiqi[['stockID', 'sell_datelist']].apply(lambda x: x['stockID'] + ' ' + str(x['sell_datelist']), axis=1)
    # index_duiqi['buy_dt'] = index_duiqi.index.map(lambda x: int(x[-8:])).tolist()
    # index_duiqi['buy_Indexs'] = index_duiqi.index.tolist()
    # index_duiqi = index_duiqi.set_index('sell_Indexs')
    # pred_df = pd.merge(pred_df, index_duiqi[['buy_Indexs']], left_index=True, right_index=True)
    # pred_df = pred_df.set_index('buy_Indexs')
    # pred_df.index.name = 'Indexs'

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
    pred_df['prediction'] = pred_df['prediction'].astype(int)
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
    from Zeus.Europa.v4_0_36.path_conf import date_config
    if len(sys.argv) > 1:
        PERIOD = sys.argv[1]
        pred_type = sys.argv[2]  # test fit
    else:
        PERIOD = 'period1'
        pred_type = 'test'   # test fit
    date_dict = date_config[f'{PERIOD}']
    out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
    in_begin, in_end = out_begin, out_end

    sel_flag = 'all' # 可选SZ,SH,all
    strategy_version = f'{PERIOD}'
    FilesavePath = bt_out_path + f'Europa/{version}/'

    # sel_model_names = ['fsv8_pct_AllXgbRegModel', 'fsv10_pct_AllXgbRegModel', 'fsv11_pct_AllXgbRegModel', 'fsrs_pct_AllLgbRegModel', 'rffs_pct_AllLgbRegModel']
    # sel_model_names = ['fsv8_pct_AllXgbRegModel', 'fsrs_pct_AllXgbRegModel', 'fsv10_pct_AllXgbRegModel', 'fsv11_pct_AllXgbRegModel', 'rffs_pct_AllXgbRegModel',
    #                    'fsv8_pct_AllLgbRegModel', 'fsrs_pct_AllLgbRegModel', 'fsv10_pct_AllLgbRegModel', 'fsv11_pct_AllLgbRegModel', 'rffs_pct_AllLgbRegModel']
    sel_model_names = os.listdir(f'/data/user/015614/Zeus/pred/Europa/v4_0_36/')

    hb_model_names = sel_model_names
    strategy_namelist = ['Europa'] * len(sel_model_names)
    test_label_list = ['label_pct_cost'] * len(sel_model_names)

    pred_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']
    valid_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']

    valid_path_list = [f'/data/user/015614/Zeus/pred/Europa/v4_0_36/{x}/model/{PERIOD}/seed_0/{out_begin}~{out_end}.csv' for x in sel_model_names]

    pred_path_list = valid_path_list

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
                merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp[[model_name,model_proba1]]], axis=1).reindex(merge_by_sample.index)#,join_axes=[merge_by_sample.index])
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