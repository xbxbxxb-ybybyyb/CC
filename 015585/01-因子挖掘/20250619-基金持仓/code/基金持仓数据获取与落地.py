import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
import sys
s = FactorData()

df_basicinfo = s.get_factor_value('WIND_ChinaMutualFundDescription')
# df_basicinfo = df_basicinfo[~df_basicinfo['F_INFO_WINDCODE'].str.contains('!')]
#
df_portfolio = pd.DataFrame()

for year in range(2010,2025+1,1):
    print(year)
    #
    df_portfolio_year1 = s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',F_PRT_ENDDATE=[f'>={year}0101', f'<={year}0331'])
    df_portfolio = df_portfolio.append(df_portfolio_year1)
    #
    try:
        df_portfolio_year2 = s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'])
    except:
        df_portfolio_year2 = pd.DataFrame()
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=[f'<={year}0630']))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=[f'>={year}0701', f'<={year}0725']))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=[f'>={year}0726', f'<={year}0731']))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=[f'>={year}0801', f'<={year}0828']))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=f'{year}0829'))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=f'{year}0830'))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=f'{year}0831'))
        df_portfolio_year2 = df_portfolio_year2.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}0401', f'<={year}0630'],
                                                                          ANN_DATE=[f'>={year}0901']))
    df_portfolio = df_portfolio.append(df_portfolio_year2)
    #
    df_portfolio_year3 = s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',F_PRT_ENDDATE=[f'>={year}0701', f'<={year}0930'])
    df_portfolio = df_portfolio.append(df_portfolio_year3)
    #
    try:
        df_portfolio_year4 = s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'])
    except:
        df_portfolio_year4 = pd.DataFrame()
        # for windcode in df_basicinfo['F_INFO_WINDCODE']:
        #     sys.stdout.write(f'\r{windcode}')
        #     sys.stdout.flush()
        #     df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'], S_INFO_WINDCODE = [f'{windcode}']))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=[f'<={year+1}0131']))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=[f'>={year+1}0201', f'<={year+1}0325']))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0326'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0327'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0328'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0329'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0330'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=f'{year+1}0331'))
        df_portfolio_year4 = df_portfolio_year4.append(s.get_factor_value('WIND_ChinaMutualFundStockPortfolio',
                                                                          F_PRT_ENDDATE=[f'>={year}1001', f'<={year}1231'],
                                                                          ANN_DATE=[f'>={year+1}0401']))
    df_portfolio = df_portfolio.append(df_portfolio_year4)
    print(f'{year} portfolio数据已下载')
df_portfolio.to_pickle('/data/user/015585/01-因子挖掘/20250619-基金持仓/file/portfolio_2010_202309.pkl')

