from datetime import date
import math

# from model_eval.MultiEval_Tool import *
from MultiEval_Tool import *

## different participation





def model_eval_new_demo(para_dict):
    #para_dict['total_strategy'] = {'Buy': ['Europa', 'JupiterN'], 'Sell': ['JupiterNSell', 'Sapphire1', 'Sapphire2','Sapphire3']}
    para_dict['total_strategy'] = {'Buy': ['Europa'], 'Sell': ['Sapphire1', 'Sapphire2', 'Sapphire3']}
    para_dict['buy_signal_strategies'] = ['Europa', 'JupiterN']
    para_dict['defalut_strategy'] = []
    para_dict['date_range'] = [para_dict['test_start_date'], para_dict['test_end_date']]
    para_dict['target_s_list'] = [
        {'Sapphire1': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_0/fsv8_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv8_pct_after_XgbRegModel_v1.csv',
         'Sapphire2': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_1/fsv8_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv8_pct_after_XgbRegModel_v1.csv',
         'Sapphire3': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_2/fsv8_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv8_pct_after_XgbRegModel_v1.csv',
        },
        {'Sapphire1': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_0/fsv10_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv10_pct_after_XgbRegModel_v1.csv',
         'Sapphire2': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_1/fsv10_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv10_pct_after_XgbRegModel_v1.csv',
         'Sapphire3': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_2/fsv10_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv10_pct_after_XgbRegModel_v1.csv',
         },
        {'Sapphire1': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_0/fsv11_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv11_pct_after_XgbRegModel_v1.csv',
         'Sapphire2': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_1/fsv11_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv11_pct_after_XgbRegModel_v1.csv',
         'Sapphire3': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_2/fsv11_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsv11_pct_after_XgbRegModel_v1.csv',
         },
        {'Sapphire1': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_0/fsrs_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsrs_pct_after_XgbRegModel_v1.csv',
         'Sapphire2': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_1/fsrs_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsrs_pct_after_XgbRegModel_v1.csv',
         'Sapphire3': f'/data/user/015614/Zeus/pred/Sapphire/v1_0_2/fsrs_pct_after_XgbRegModel/{para_dict["test_start_date"]}~{para_dict["test_end_date"]}_fsrs_pct_after_XgbRegModel_v1.csv',
         },

    ]
    multiEvalIndex = MultiEvalIndex(para_dict)
    multiEvalIndex.multi_model_eval()
    return



class MultiEvalIndex:
    def __init__(self, para_dict):
        self.para_dict = para_dict

    def multi_model_eval(self):
        file_path = self.para_dict['save_path'] + '/回测结果/'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
            print("Creat folder " + file_path)
        today = (date.today()).strftime("%Y%m%d")
        writer = pd.ExcelWriter(file_path + '%d~%d_模型评价_%s.xlsx' % (self.para_dict['test_start_date'], self.para_dict['test_end_date'], today))

        for i,model_name in enumerate(self.para_dict['sel_model_names']):
            self.para_dict['model_name'] = model_name
            print(model_name)
            para_dict['target_s'] = para_dict['target_s_list'][i]
            self.multiEval_Tool = MultiEval_Tool(self.para_dict['target_s'], self.para_dict['date_range'], self.para_dict['save_path'], self.para_dict['total_strategy'])
            self.para_dict['target_strategy'] = list(self.para_dict['target_s'].keys())
            self.multiEval_Tool.total_df.fillna(0, inplace=True)
            self.para_dict['target_col1'] = eval(self.multiEval_Tool.Contents.loc[self.para_dict['target_strategy'][0],'signal_col'])
            self.para_dict['target_col2'] = eval(self.multiEval_Tool.Contents.loc[self.para_dict['target_strategy'][1],'signal_col'])
            self.para_dict['target_col3'] = eval(self.multiEval_Tool.Contents.loc[self.para_dict['target_strategy'][2], 'signal_col'])

            diff_parti = self.merge_diff_parti_index()
            #eval_index = self.calculate_model_evel_result()

            # eval_index.fillna(0).to_excel(writer, sheet_name='模型结果')
            diff_parti.to_excel(writer, sheet_name='不同参与率统计_'+model_name)
        writer.save()
        return


    def merge_diff_parti_index(self):
        diff_parti_index_dict = self.calculate_diff_parti()
        diff_parti = pd.DataFrame(index=diff_parti_index_dict['收益'].index)
        for diff_parti_index in diff_parti_index_dict.keys():
            diff_parti[diff_parti_index] = np.nan
            diff_parti = pd.concat((diff_parti,diff_parti_index_dict[diff_parti_index]),axis=1)
        return diff_parti



    def calculate_model_evel_result(self):
        profit_series_eval = pd.DataFrame()
        for strategy in self.para_dict['total_strategy']['Buy']:
            profit_series_eval += self.multiEval_Tool.total_df[strategy+'_amt'] * self.multiEval_Tool.total_df[strategy+'_pct'] * self.multiEval_Tool.total_df[strategy+'_prediction']
        for strategy in self.para_dict['total_strategy']['Sell']:
            profit_series_eval += self.multiEval_Tool.total_df['Sell_amt'] * self.multiEval_Tool.total_df[strategy+'_pct'] * self.multiEval_Tool.total_df[strategy+'_prediction']

        # model evel index
        eval_index = pd.DataFrame(columns=[self.para_dict['model_name']])
        eval_index.loc['收益'] = profit_series_eval.sum()
        eval_index.loc['最大回撤'] = (profit_series_eval.cumsum().cummax()-profit_series_eval.cumsum()).max()
        eval_index.loc['收益风险比'] = eval_index.loc['收益']/eval_index.loc['最大回撤']
        eval_index.loc['日扣费胜率'] = np.sum(profit_series_eval>0)/np.sum(profit_series_eval!=0)
        eval_index.loc['收益夏普比'] = profit_series_eval.mean()/profit_series_eval.std()/math.sqrt(250)
        return eval_index



    def calculate_diff_parti(self):
        # diff parti index
        diff_parti_index_dict = {}
        profit_dfs = pd.DataFrame()
        max_withdraw_dfs = pd.DataFrame()
        win_ratio_dfs = pd.DataFrame()
        profit_shap_dfs = pd.DataFrame()
        profit_risk_ratio_dfs = pd.DataFrame()

        for parti3 in self.para_dict['target_col3']:
            profit_df = pd.DataFrame(np.nan, index=self.para_dict['target_col1'], columns=self.para_dict['target_col2'])
            max_withdraw_df = pd.DataFrame(np.nan, index=self.para_dict['target_col1'], columns=self.para_dict['target_col2'])
            win_ratio_df = pd.DataFrame(np.nan, index=self.para_dict['target_col1'], columns=self.para_dict['target_col2'])
            profit_shap_df = pd.DataFrame(np.nan, index=self.para_dict['target_col1'], columns=self.para_dict['target_col2'])

            profit_df = pd.concat((pd.DataFrame(index=[parti3]), profit_df), axis=0)
            max_withdraw_df = pd.concat((pd.DataFrame(index=[parti3]), max_withdraw_df), axis=0)
            win_ratio_df = pd.concat((pd.DataFrame(index=[parti3]), win_ratio_df), axis=0)
            profit_shap_df = pd.concat((pd.DataFrame(index=[parti3]), profit_shap_df), axis=0)

            for parti1 in self.para_dict['target_col1']:
                for parti2 in self.para_dict['target_col2']:
                        self.tmp_total_df = self.multiEval_Tool.total_df.copy()
                        profit_series = self.calculate_profit_series(parti1, parti2,parti3)
                        profit_df.loc[parti1,parti2] = profit_series.sum()
                        max_withdraw_df.loc[parti1,parti2] = (profit_series.cumsum().cummax()-profit_series.cumsum()).max()
                        win_ratio_df.loc[parti1,parti2] = np.sum(profit_series>0)/np.sum(profit_series!=0)
                        profit_shap_df.loc[parti1,parti2] = profit_series.sum()/ profit_series.std()/math.sqrt(250)

            # generate profit risk
            profit_risk_ratio_df = profit_df / max_withdraw_df

            profit_dfs = pd.concat([profit_dfs,profit_df],axis=0)
            max_withdraw_dfs = pd.concat([max_withdraw_dfs,max_withdraw_df],axis=0)
            win_ratio_dfs = pd.concat([win_ratio_dfs,win_ratio_df],axis=0)
            profit_shap_dfs = pd.concat([profit_shap_dfs,profit_shap_df],axis=0)
            profit_risk_ratio_dfs = pd.concat([profit_risk_ratio_dfs,profit_risk_ratio_df],axis=0)



        diff_parti_index_dict['收益'] = profit_dfs
        diff_parti_index_dict['最大回撤'] = max_withdraw_dfs
        diff_parti_index_dict['收益风险比'] =profit_risk_ratio_dfs
        diff_parti_index_dict['日扣费胜率'] = win_ratio_dfs
        diff_parti_index_dict['收益夏普比'] = profit_shap_dfs
        return diff_parti_index_dict



    def calculate_default_profit_series(self):
        profit_series_default = 0
        for strategy in self.para_dict['total_strategy']['Buy']:
            if (strategy not in self.para_dict['target_strategy']) and (strategy in self.para_dict['defalut_strategy']):
                prediction_col = self.tmp_total_df.filter(like=strategy+'_prediction').columns[0]
                profit_series_default += self.tmp_total_df[strategy+'_amt'] * self.tmp_total_df[strategy+'_pct'] * self.tmp_total_df[prediction_col]
        for strategy in self.para_dict['total_strategy']['Sell']:
            if (strategy not in self.para_dict['target_strategy']) and (strategy in self.para_dict['defalut_strategy']):
                prediction_col = self.tmp_total_df.filter(like=strategy + '_prediction').columns[0]
                profit_series_default += self.tmp_total_df['Sell_amt'] * self.tmp_total_df[strategy + '_pct'] * self.tmp_total_df[prediction_col]

        return profit_series_default


    def sell_signal_logic_process(self,parti1, parti2, parti3):
        self.tmp_total_df['cum_prediction'] = 0
        for now_priority in range(len(self.para_dict['total_strategy']['Sell'])):
            for strategy in self.para_dict['total_strategy']['Sell']:
                if strategy==self.para_dict['target_strategy'][0]:
                    prediction_col = parti1
                elif strategy==self.para_dict['target_strategy'][1]:
                    prediction_col = parti2
                elif strategy==self.para_dict['target_strategy'][2]:
                    prediction_col = parti3
                else:
                    prediction_col = self.tmp_total_df.filter(like=strategy + '_prediction').columns[0]
                self.tmp_total_df.loc[self.tmp_total_df[strategy+'_priority']==now_priority+1,prediction_col] -=self.tmp_total_df.loc[self.tmp_total_df[strategy+'_priority']==now_priority+1,'cum_prediction']
                self.tmp_total_df.loc[self.tmp_total_df[prediction_col] < 0, prediction_col] = 0
                self.tmp_total_df.loc[self.tmp_total_df[strategy+'_priority']==now_priority+1,'cum_prediction'] += self.tmp_total_df.loc[self.tmp_total_df[strategy+'_priority']==now_priority+1,prediction_col]
                self.tmp_total_df.loc[self.tmp_total_df['cum_prediction']>1,'cum_prediction'] = 1
        return


    def signal_logic_process(self,parti1, parti2,parti3):
        if ('Europa_pct' in self.tmp_total_df.columns) and ('JupiterN_pct' in self.tmp_total_df.columns):
            if self.para_dict['target_strategy'][0]=='Europa':
                Europa_col = parti1
            elif self.para_dict['target_strategy'][1]=='Europa':
                Europa_col = parti2
            elif self.para_dict['target_strategy'][2]=='Europa':
                Europa_col = parti3
            else:
                Europa_col = self.tmp_total_df.filter(like='Europa'+'_prediction').columns[0]
            if self.para_dict['target_strategy'][0]=='JupiterN':
                Jupiter_col = parti1
            elif self.para_dict['target_strategy'][1]=='JupiterN':
                Jupiter_col = parti2
            elif self.para_dict['target_strategy'][2]=='JupiterN':
                Jupiter_col = parti3
            else:
                Jupiter_col = self.tmp_total_df.filter(like='JupiterN'+'_prediction').columns[0]
            self.tmp_total_df.loc[self.tmp_total_df[Europa_col] == 0, Jupiter_col] = 0

        self.sell_signal_logic_process(parti1, parti2, parti3)
        return


    def sell_amt_logic_process(self):
        # generate max amt
        self.tmp_total_df['Sell_amt'] = 0
        for strategy in self.para_dict['total_strategy']['Buy']:
            if strategy in self.para_dict['buy_signal_strategies']:
                prediction_col = self.tmp_total_df.filter(like=strategy + '_prediction').columns[0]
                self.tmp_total_df.loc[self.tmp_total_df[prediction_col]==0,strategy + '_amt'] = 0
            self.tmp_total_df['Sell_amt']+=self.tmp_total_df[strategy+'_amt']
        return



    def calculate_profit_series(self, parti1, parti2, parti3):
        self.signal_logic_process(parti1, parti2, parti3)
        self.sell_amt_logic_process()
        profit_series = self.calculate_default_profit_series()
        if self.para_dict['target_strategy'][0] in self.para_dict['total_strategy']['Sell']:
            profit_series += self.tmp_total_df['Sell_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][0] + '_pct'] * self.tmp_total_df[parti1]
        else:
            profit_series += self.tmp_total_df[self.para_dict['target_strategy'][0]+'_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][0]+'_pct'] * self.tmp_total_df[parti1]
        if self.para_dict['target_strategy'][1] in self.para_dict['total_strategy']['Sell']:
            profit_series += self.tmp_total_df['Sell_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][1] + '_pct'] * self.tmp_total_df[parti2]
        else:
            profit_series += self.tmp_total_df[self.para_dict['target_strategy'][1]+'_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][1]+'_pct'] * self.tmp_total_df[parti2]
        if self.para_dict['target_strategy'][2] in self.para_dict['total_strategy']['Sell']:
            profit_series += self.tmp_total_df['Sell_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][2] + '_pct'] * self.tmp_total_df[parti3]
        else:
            profit_series += self.tmp_total_df[self.para_dict['target_strategy'][2]+'_amt'] * self.tmp_total_df[self.para_dict['target_strategy'][2]+'_pct'] * self.tmp_total_df[parti3]
        return profit_series





if __name__ == "__main__":
    para_dict = {}
    para_dict['test_start_date'], para_dict['test_end_date'] = 20191001, 20200331
    para_dict['save_path'] = '/data/user/015614/junkData/'
    para_dict['sel_model_names'] = ['fsv8', 'fsv10', 'fsv11', 'fsrs']
    model_eval_new_demo(para_dict)
    print('finish')
