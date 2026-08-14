# coding: utf-8
# Author：fengchi863
# Date ：2024/1/30 16:20

import pandas as pd

# 不同指标权重
score_weight_config = {
    'TOP10模型数量得分': 0.1, # 0.1 # 0.15
    '实盘模型数量得分': 0.2, # 0.2 # 0.15
    'TOP10模型质量得分': 0.3, # 0.2 # 0.35
    '实盘模型质量得分': 0.4, # 0.5 # 0.35
}

# 模型数量按策略权重
num_weight_config = {
    'Europa_v2': 1.1,
    'Europa_v3': 1.1,
    'Europa_v4': 0,   # 当前只选出模型，尚未跟踪
    'Jupiter_v9': 1.1,
    'JupiterZ_v1': 1,
    'Metis_v1': 1,
    'Saturn_v6': 1,
    'Sell_v1_v1': 1,
    'Sell_v3_v1': 1,
    'Leda_v1': 1,
}

# 模型质量按策略权重
quality_weight_config = {
    # 'Europa_v2': 1.1,
    'Europa_v3': 1.1,
    # 'Europa_v4': 0,
    'Jupiter_v9': 1.1,
    'JupiterZ_v1': 1,
    'Metis_v1': 1,
    'Saturn_v6': 1,
    'Sell_v1_v1': 1,
    'Sell_v3_v1': 1,
    'Leda_v1': 1
}

# 模型质量参考可选项：扣费收益率均值、扣费总收益、收益风险比、收益夏普比率
model_quality_ref_indicator=['收益夏普比率']

dev_names = ['Wj', 'Xly', 'Fc', 'Skk', 'Xbc', 'Zwh']

class ModelScore:
    def __init__(self, model_num_eval='method1', model_quality_eval='method1', model_fpath=None):
        self.model_num_eval = model_num_eval
        self.model_quality_eval = model_quality_eval
        self.model_fpath = model_fpath
        self.model_data = self.load_basic_data()

    def load_basic_data(self):
        data = pd.read_excel(self.model_fpath)
        data['strategy'] = data['strategy'].fillna(method='ffill')
        data['version'] = data['version'].fillna(method='ffill')
        data['strategy_version'] = data[['strategy', 'version']].apply(lambda x: x['strategy'] + '_' + x['version'], axis=1)
        filter_strategy_version = list(num_weight_config.keys())
        data = data.query(f'strategy_version in {filter_strategy_version}')
        return data

    @staticmethod
    def add_quality_weight(strategy_name, w):
        return w * quality_weight_config[strategy_name]

    @staticmethod
    def add_num_weight(strategy_name, w):
        return w * num_weight_config[strategy_name]

    def calc_score(self):
        model_score = pd.DataFrame(index=dev_names,
                                   columns=['TOP10模型数量', '实盘模型数量',
                                            'TOP10模型数量（加权）', '实盘模型数量（加权）',
                                            'TOP10模型质量', '实盘模型质量',
                                            'TOP10模型数量得分', '实盘模型数量得分',
                                            'TOP10模型质量得分', '实盘模型质量得分'])

        # 统计模型数量
        top10_model_group = self.model_data.groupby(['strategy_version', '开发人'])['model'].count()
        prod_model_group = self.model_data.groupby(['strategy_version', '开发人'])['是否实盘'].sum()
        model_score['TOP10模型数量'] = top10_model_group.reset_index().fillna(method='ffill').groupby('开发人')['model'].sum().reindex(dev_names)
        model_score['实盘模型数量'] = prod_model_group.reset_index().fillna(method='ffill').groupby('开发人')['是否实盘'].sum().reindex(dev_names)
        self.model_data['该模型所占数量权重'] = self.model_data[['strategy_version']].apply(lambda x: num_weight_config[x['strategy_version']], axis=1)
        self.model_data['in_top10'] = 1
        self.model_data['in_top10（加权）'] = self.model_data[['strategy_version', 'in_top10']].apply(lambda x: self.add_num_weight(x['strategy_version'], x['in_top10']), axis=1)
        model_score['TOP10模型数量（加权）'] = self.model_data[['开发人', 'in_top10（加权）']].groupby('开发人').sum().loc[dev_names].values
        prod_model = self.model_data.query('是否实盘 == 1').copy()
        model_score['实盘模型数量（加权）'] = prod_model[['开发人', 'in_top10（加权）']].groupby('开发人').sum().loc[dev_names].values

        # 计算模型质量
        self.model_data['模型策略内排名'] = self.model_data.groupby(['strategy_version'])[model_quality_ref_indicator].rank(pct=True, ascending=True)  # 表现越好，得分越高
        self.model_data['模型策略内排名（加权）'] = self.model_data[['strategy_version', '模型策略内排名']].apply(lambda x: self.add_quality_weight(x['strategy_version'], x['模型策略内排名']), axis=1)
        self.model_data['该模型所占质量权重'] = self.model_data[['strategy_version']].apply(lambda x: quality_weight_config[x['strategy_version']], axis=1)
        model_score['TOP10模型质量'] = self.model_data[['开发人', '模型策略内排名（加权）']].groupby('开发人').sum().loc[dev_names].values / self.model_data[['开发人', '该模型所占质量权重']].groupby('开发人').sum().loc[dev_names].values

        prod_model = self.model_data.query('是否实盘 == 1').copy()
        prod_model['模型策略内排名'] = prod_model.groupby(['strategy_version'])[model_quality_ref_indicator].rank(pct=True, ascending=True) # 重新在实盘模型中排序
        prod_model['模型策略内排名（加权）'] = prod_model[['strategy_version', '模型策略内排名']].apply(lambda x: self.add_quality_weight(x['strategy_version'], x['模型策略内排名']), axis=1)
        model_score['实盘模型质量'] = prod_model[['开发人', '模型策略内排名（加权）']].groupby('开发人').sum().loc[dev_names].values / prod_model[['开发人', '该模型所占质量权重']].groupby('开发人').sum().loc[dev_names].values

        # 依次计算上述四项得分(百分制)，计算方式：当前值 / 当前组最大值 * 100
        model_score['TOP10模型数量得分'] = model_score['TOP10模型数量（加权）'] / model_score['TOP10模型数量（加权）'].max() * 100
        model_score['实盘模型数量得分'] = model_score['实盘模型数量（加权）'] / model_score['实盘模型数量（加权）'].max() * 100
        model_score['TOP10模型质量得分'] = model_score['TOP10模型质量'] / model_score['TOP10模型质量'].max() * 100
        model_score['实盘模型质量得分'] = model_score['实盘模型质量'] / model_score['实盘模型质量'].max() * 100

        model_score['总得分'] = model_score['TOP10模型数量得分'] * score_weight_config['TOP10模型数量得分'] + \
            model_score['实盘模型数量得分'] * score_weight_config['实盘模型数量得分'] + \
            model_score['TOP10模型质量得分'] * score_weight_config['TOP10模型质量得分'] + \
            model_score['实盘模型质量得分'] * score_weight_config['实盘模型质量得分']

        model_score['总排名'] = model_score['总得分'].rank(ascending=False)   # 得分最高排第一
        return model_score


if __name__ == '__main__':
    # root_path = '/data/user/015614/shared/for_wys/'
    root_path = '/data/user/015614/'
    model_fpath = root_path + '2024年中模型评估结果.xlsx'
    ms = ModelScore(model_fpath=model_fpath)
    model_score = ms.calc_score()
    model_score.to_excel(root_path + '2024年中模型得分.xlsx')

    from dataApi.sendInfo import send_file
    send_file('/data/user/015614/2024年中模型评估结果.xlsx')


