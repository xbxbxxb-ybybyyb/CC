# coding: utf-8
# Author：fengchi863
# Date ：2022/7/28 14:52

from xquant.factordata import FactorData

hfactor = FactorData()
from model_eval.bak.bak20230105_simple_bt.v3_3_Simple_modelEval_Tool import *

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

class EvalLaunch:
    def __init__(self,
                 date_config: dict,
                 strategy_name='SaturnS1',
                 sel_flag='all',
                 strategy_version='6',
                 pred_type='test',
                 sel_model_names=None,
                 valid_path_list=None,
                 pred_path_list=None,
                 file_save_path='/data/user/015614/junkData/',
                 save_flag=True):
        self.out_begin = date_config['test_start_date']
        self.out_end = date_config['test_end_date']
        self.in_begin = date_config['valid_start_date']
        self.in_end = date_config['valid_end_date']
        self.strategy_name = strategy_name
        self.sel_flag = sel_flag
        self.strategy_version = strategy_version
        self.pred_type = pred_type
        self.sel_model_names = sel_model_names
        self.valid_path_list = valid_path_list
        self.pred_path_list = pred_path_list
        self.file_save_path = file_save_path
        self.save_flag = save_flag

    def launch(self):
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
        out_begin, out_end = self.out_begin, self.out_end
        in_begin, in_end = self.in_begin, self.in_end
        strategy_name = self.strategy_name
        sel_flag = self.sel_flag  # 可选SZ,SH,all
        strategy_version = self.strategy_version
        pred_type = self.pred_type  # 可选test，fit
        # 修改为自己的文件保存路径
        FilesavePath = self.file_save_path

        # 验证集和测试集的路径，使用csv文件格式
        # pred_path_list, valid_path_list,sel_model_names 数量要一致，顺序要严格一一对应,分场景合并信号要在子场景之前
        # hb_model_names: 需要计算模型重合度相关信息的模型列表，需要是sel_model_names的子集
        # 分场景合并的模型名字中一定要包含'scene',且其余模型名字不能包含'scene'
        # pred_Reg中保存是是回归标签预测或者预测为1的概率
        sel_model_names = self.sel_model_names
        hb_model_names = sel_model_names
        test_label_list = ['label_pct_cost']

        pred_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']
        valid_view = ['datelist', 'stockID', 'prediction', 'pred_Reg']

        valid_path_list = self.valid_path_list
        pred_path_list = self.pred_path_list
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
            # merge_by_day_valid = pd.DataFrame()
            merge_modeleval = pd.DataFrame()
            merge_modelmingan = pd.DataFrame()
            merge_inmodelmingan = pd.DataFrame()
            count = 0
            for i in list(range(len(pred_path_list))):
                count = count + 1
                tmp_pred_path, tmp_valid_path = pred_path_list[i], valid_path_list[i]
                model_name = sel_model_names[i]
                label_name = test_label_list[i]

                print(model_name)
                tmp_pred_df = deal_preddata(tmp_pred_path, pred_view, sel_flag)
                tmp_valid_df = deal_preddata(tmp_valid_path, valid_view, sel_flag)
                tmp_modeleval = modelEval_Tool(strategy_name, tmp_pred_df, tmp_valid_df, model_name, out_begin, out_end,
                                               in_begin, in_end, FilesavePath, label_name)
                totalResDf_tmp, by_day_tmp, by_sample_tmp, model_mingan_tmp, model_mingan_in_tmp = tmp_modeleval.generate_series_data()
                if count == 1:
                    merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp])
                else:
                    merge_by_sample = pd.concat([merge_by_sample, by_sample_tmp[[model_name]]], axis=1,
                                                join_axes=[merge_by_sample.index])
                merge_by_day = pd.concat([merge_by_day, by_day_tmp], axis=1)
                # merge_by_day_valid = pd.concat([merge_by_day_valid, by_day_valid_tmp], axis=1)
                merge_modeleval = pd.concat([merge_modeleval, totalResDf_tmp], axis=1)

            if len(model_mingan_tmp) > 0:
                model_pd = pd.DataFrame(index=[model_name], columns=model_mingan_tmp.columns.tolist())
                merge_modelmingan = pd.concat([merge_modelmingan, model_pd, model_mingan_tmp])
            if len(model_mingan_in_tmp) > 0:
                inmodel_pd = pd.DataFrame(index=[model_name], columns=model_mingan_in_tmp.columns.tolist())
                merge_inmodelmingan = pd.concat([merge_inmodelmingan, inmodel_pd, model_mingan_in_tmp])
            if self.save_flag:
                FilePath = FilesavePath + '/回测结果/'
                if not os.path.exists(FilePath):
                    os.makedirs(FilePath, exist_ok=True)
                    print("creat folder " + FilePath)
                writer = pd.ExcelWriter(
                    FilePath + '%d~%d_%s_v%s_%s_merge_%s_模型评价_%s.xlsx' % (
                        out_begin, out_end, strategy_name, str(strategy_version), sel_flag, pred_type, today))

                # merge_by_sample = merge_by_sample.reset_index()
                # merge_by_sample.sort_values(by=['datelist'], ascending=True, inplace=True)
                # merge_by_sample.to_excel(writer, sheet_name='按次')
                # merge_by_day.to_excel(writer, sheet_name='按日')
                # merge_by_day_valid.to_excel(writer, sheet_name='样本内按日')
                merge_modeleval.fillna(0).to_excel(writer, sheet_name='模型结果')
                merge_modelmingan.to_excel(writer, sheet_name='不同参与率统计')
                merge_inmodelmingan.to_excel(writer, sheet_name='样本内不同参与率统计')
                writer.save()
                return merge_modeleval, merge_modelmingan
            else:
                return merge_modeleval, merge_modelmingan