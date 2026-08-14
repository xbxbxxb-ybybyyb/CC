import pandas as pd

data_zz1000 = pd.read_pickle('/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_20210701_20240630.pkl')
data_zz1000['label_931_941_twap_next_twap'] = data_zz1000['next_twap'] / data_zz1000['931_941_twap'] - 1

data_zz500 = pd.read_pickle('/data/user/023859/Hedging/zz500_sw_weight_and_price_20210701_20240630.pkl')
data_zz500['label_931_941_twap_next_twap'] = data_zz500['next_twap'] / data_zz500['931_941_twap'] - 1

data_hs300 = pd.read_pickle('/data/user/023859/Hedging/hs300_sw_weight_and_price_20210701_20240630.pkl')
data_hs300['label_931_941_twap_next_twap'] = data_hs300['next_twap'] / data_hs300['931_941_twap'] - 1

periods = [20210701,20211231],[20220101,20220630]
datasets = [data_zz1000, data_zz500, data_hs300]

final_df = []
for dataset in datasets:
    data_df = []
    for i in range(2):
        start_date, end_date = periods[i][0], periods[i][1]
        data = dataset.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
        industry_avg = data.groupby(['dt','sw_industry_code_1'])['label_931_941_twap_next_twap'].mean().rename('industry_mean').reset_index()
        merged_df = dataset.reset_index().merge(industry_avg, on=['dt','sw_industry_code_1'])
        pearson_corr_series = merged_df.groupby('Ticker').apply(lambda x:x['label_931_941_twap_next_twap'].corr(x['industry_mean']))
        spearman_corr_series = merged_df.groupby('Ticker').apply(lambda x:x['label_931_941_twap_next_twap'].corr(x['industry_mean'], method='spearman'))
        sw1_code_series = merged_df.groupby('Ticker')['sw_industry_code_1'].last()
        sw1_name_series = merged_df.groupby('Ticker')['sw_industry_name_1'].last()
        result_df = pd.DataFrame({
        '行业代码':sw1_code_series,
        '行业名称':sw1_name_series,
        'Pearson相关系数':pearson_corr_series,
        'Spearman相关系数':spearman_corr_series
        })
        result_df.columns = pd.MultiIndex.from_product([[f'区间{i+1}'], result_df.columns])
        data_df.append(result_df)

    data_df = pd.concat(data_df, axis=1,sort=False)
    data_df = data_df.sort_values(by=[('区间1','Pearson相关系数'),('区间1','Spearman相关系数'),('区间2','Pearson相关系数'),('区间2','Spearman相关系数')],ascending=False)
    data_df.index.names = ['Ticker']
    final_df.append(data_df)

excel_writer = pd.ExcelWriter(f'/dfs/user/023859/share_file/for_wys/industry_hedging/index/指数成分股与对应行业相关性.xlsx')
final_df[0].to_excel(excel_writer, sheet_name='zz1000')
final_df[1].to_excel(excel_writer, sheet_name='zz500')
final_df[2].to_excel(excel_writer, sheet_name='hs300')
excel_writer.save()