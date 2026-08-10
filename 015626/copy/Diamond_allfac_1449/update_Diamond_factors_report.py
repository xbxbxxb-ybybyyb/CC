import os
import time
import pandas as pd
from multiprocessing import Pool
import matplotlib
matplotlib.use('Agg')
from overnight.utility import get_current_date
from overnight.SIF_Factor_Test20 import SIF_Factor_Test


class FactorReportGenerator:
    def __init__(self, factor_path, save_path, start_date, end_date, ticker, layers, project_name, overnight_time_period, factor_format, save_image):
        self.factor_path = factor_path
        self.save_path = save_path
        self.start_date = start_date
        self.end_date = end_date
        self.ticker = ticker
        self.layers = layers
        self.project_name = project_name
        self.overnight_time_period = overnight_time_period
        self.factor_format = factor_format
        self.save_image = save_image
        
    def load_factor_data(self):
        assert self.factor_format in ['h5', 'csv']
        factor_agg_df = None

        if self.factor_format == 'h5':
            factor_path_detail = os.path.join(self.factor_path, self.project_name)
            factors = sorted([i for i in os.listdir(factor_path_detail) if i.endswith('h5')])
            factors_list = [os.path.join(factor_path_detail, i) for i in factors]
            for i, i_name in enumerate(factors_list):
                factor = pd.read_hdf(i_name)
                factor_agg_df = factor if factor_agg_df is None else pd.concat([factor_agg_df, factor], axis=1)
                
        elif self.factor_format == 'csv':
            trade_time = self.overnight_time_period[0] - 1
            factor_path_detail = sorted([i for i in os.listdir(self.factor_path) if (i.endswith(str(trade_time)) & (int(i[:4]) > 2015))])
            for i_path in factor_path_detail:
                df_temp = pd.read_csv(os.path.join(self.factor_path, i_path, i_path) + '.csv', index_col=0)[['norm']]
                df_temp.columns = [pd.to_datetime(i_path[:8])]
                factor_agg_df = df_temp if factor_agg_df is None else factor_agg_df.merge(df_temp, left_index=True, right_index=True)
            factor_agg_df = factor_agg_df.T
        
        factor_agg_df.index.name = 'dt'
        self.factor_agg_df = factor_agg_df

    def get_save_path(self):
        if str(self.start_date)[:4] == str(self.end_date)[:4]:
            save_path_future = os.path.join(self.save_path, self.ticker[:2].lower(), self.project_name, 'future',
                                            'layers' + str(self.layers), str(self.start_date)[:4])
            save_path_spot = os.path.join(self.save_path, self.ticker[:2].lower(), self.project_name, 'spot',
                                          'layers' + str(self.layers), str(self.start_date)[:4])
        else:
            save_path_future = os.path.join(self.save_path, self.ticker[:2].lower(), self.project_name, 'future',
                                            'layers' + str(self.layers),
                                            str(self.start_date)[:4] + '-' + str(self.end_date)[:4])
            save_path_spot = os.path.join(self.save_path, self.ticker[:2].lower(), self.project_name, 'spot',
                                          'layers' + str(self.layers),
                                          str(self.start_date)[:4] + '-' + str(self.end_date)[:4])
        if not os.path.exists(save_path_future):
            os.makedirs(save_path_future)
        if not os.path.exists(save_path_spot):
            os.makedirs(save_path_spot)
        self.save_path_future = save_path_future
        self.save_path_spot = save_path_spot

    def generate_factor_report(self, i_column):
        factor_temp = self.factor_agg_df[i_column]
        
        try:
            stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap',
                                          direction='long', ticker=self.ticker, layers=self.layers, 
                                          overnight_time_period=self.overnight_time_period,
                                          starttime=self.start_date, endtime=self.end_date, show_image=False,
                                          save_image=self.save_image, savepath=self.save_path_future).draw_result()
            stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret',
                                          direction='long', ticker=self.ticker, layers=self.layers, 
                                          overnight_time_period=self.overnight_time_period,
                                          starttime=self.start_date, endtime=self.end_date, show_image=False,
                                          save_image=self.save_image, savepath=self.save_path_spot).draw_result()
            temp_df1 = pd.DataFrame(stats_temp1.values(), columns=[i_column], index=stats_temp1.keys())
            temp_df2 = pd.DataFrame(stats_temp2.values(), columns=[i_column], index=stats_temp2.keys())
        except:
            temp_df1 = pd.DataFrame(columns=[i_column])
            temp_df2 = pd.DataFrame(columns=[i_column])
            print(i_column)
        return temp_df1, temp_df2

    def multi_processing_helper(self):
        with Pool() as pool:
            stats_list = pool.map(self.generate_factor_report, self.factor_agg_df.columns)

        stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
        stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)
        
        stats_all_future.T.to_excel(os.path.join(self.save_path_future, 'stats_future.xlsx'))
        stats_all_spot.T.to_excel(os.path.join(self.save_path_spot, 'stats_spot.xlsx'))
        
#        if os.path.exists(os.path.join(self.save_path_future, 'stats_future.xlsx')):
#            stats_all_future.T.to_excel(os.path.join(self.save_path_future, 'stats_future_' + dt.datetime.now().strftime('%Y%m%d') + '.xlsx'))
#        else:
#            stats_all_future.T.to_excel(os.path.join(self.save_path_future, 'stats_future.xlsx'))
#        if os.path.exists(os.path.join(self.save_path_spot, 'stats_spot.xlsx')):
#            stats_all_spot.T.to_excel(os.path.join(self.save_path_spot, 'stats_spot_' + dt.datetime.now().strftime('%Y%m%d') + '.xlsx'))
#        else:
#            stats_all_spot.T.to_excel(os.path.join(self.save_path_spot, 'stats_spot.xlsx'))



def minute_flag_check(date):
    path1 = '/data/group/800466/trade/overnight/flag/' + str(date) + '/' + str(date) + '_Diamond_monitor_report.success'
    return os.path.exists(path1)

if __name__ == '__main__':
    date = get_current_date()
    print(date) 

    flag_root = '/data/group/800466/trade/overnight/flag/' + str(date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(date) + '_Diamond_factors_report.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait minute flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')   
    
    
    factor_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/'
    # factor_path = '/data/group/800466/trade/overnight/factor_proof/'
    factor_format = 'h5'
    save_path = '/data/group/800466/warehouse/prod/tradingstats/Diamond/factor_report/'
    overnight_time_period = [1450, 930]
    for i_ticker in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        for i_layer in [4, 8]:
            for i_dates in [[20160101, 20241231], [20200101, 20241231], [20210101, 20241231], [20220101, 20241231], [20230101, 20241231], [20240101, 20241231]]:
                print(i_ticker, i_layer, i_dates)
                start_date = i_dates[0]
                end_date = i_dates[1]
                ticker = i_ticker
                layers = i_layer
                project_name = '1449'
                

                generate_factor_report = FactorReportGenerator(factor_path=factor_path, save_path=save_path, start_date=start_date,
                                                               end_date=end_date, ticker=ticker, layers=layers, project_name=project_name,
                                                               overnight_time_period=overnight_time_period, factor_format=factor_format, save_image=True)
                generate_factor_report.get_save_path()
                generate_factor_report.load_factor_data()
                generate_factor_report.multi_processing_helper()
                
                
    factor_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/'
    # factor_path = '/data/group/800466/trade/overnight/factor_proof/'
    factor_format = 'h5'
    save_path = '/data/group/800466/warehouse/prod/tradingstats/Diamond/factor_report/'
    overnight_time_period = [1430, 930]
    for i_ticker in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        for i_layer in [4, 8]:
            for i_dates in [[20160101, 20241231], [20200101, 20241231], [20210101, 20241231], [20220101, 20241231], [20230101, 20241231], [20240101, 20241231]]:
                print(i_ticker, i_layer, i_dates)
                start_date = i_dates[0]
                end_date = i_dates[1]
                ticker = i_ticker
                layers = i_layer
                project_name = '1429'
                

                generate_factor_report = FactorReportGenerator(factor_path=factor_path, save_path=save_path, start_date=start_date,
                                                               end_date=end_date, ticker=ticker, layers=layers, project_name=project_name,
                                                               overnight_time_period=overnight_time_period, factor_format=factor_format, save_image=True)
                generate_factor_report.get_save_path()
                generate_factor_report.load_factor_data()
                generate_factor_report.multi_processing_helper()
                
                
    flag_path_success = flag_root + str(date) + '_Diamond_factors_report.success'
    with open(flag_path_success, 'w') as file:
        pass