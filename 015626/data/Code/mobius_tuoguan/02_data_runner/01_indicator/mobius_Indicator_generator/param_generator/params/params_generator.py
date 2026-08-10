import multiprocessing as mp
import sys
from decimal import Decimal as D

from joblib import Parallel, delayed

from common.notice import *
from common.query_service import *
from common.tools import *
from param_generator.params.mock_info_generator import *
from param_generator.params.templates import *

index_list = ['SZ50', 'HS300', 'ZZ500', 'ZZ1000']

ashare_total = factor_query_service.get_factor_value \
    ('WIND_AShareCapitalization', factors=['S_INFO_WINDCODE', 'CHANGE_DT', 'FLOAT_A_SHR']).rename(
    columns={'S_INFO_WINDCODE': 'Ticker'}).set_index('Ticker')

ashare_total['CHANGE_DT'] = ashare_total['CHANGE_DT'].astype('int')


def get_shares(stock, trading_day):
    temp = ashare_total.loc[stock].reset_index(drop=True).sort_values(by='CHANGE_DT')
    if stock == '689009.SH' and temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1][
        'FLOAT_A_SHR'] < 10000:
        return [stock, temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1]['FLOAT_A_SHR'] * 10]
    else:
        return [stock, temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1]['FLOAT_A_SHR']]


class ParamsGenerator:
    def __init__(self, real_env=True, use_h5_data=False):
        self.thread_num = "40"
        self.params_template = template_backend_params
        if real_env is False:
            self.params_template = template_history_backend_params
        self.real_env = real_env
        # self.user_ids = user_ids
        # self.link_messager = LinkMessage(user_ids)
        self.message_prefix = "[Mobius截面指标计算通知]"
        self.use_h5_data = use_h5_data
        self.mock_generator = MockInfoGenerator()
        self.cache_mock_data = {}

    # def send_link_message(self, msg: str):
    #     self.link_messager.sendMessage(self.message_prefix + msg)

    def get_future_trading_instruments(self, trading_day):
        start_date = trading_day
        end_date = trading_day
        result_IH = future_query_service.get_instrument_all("IH", start_date, end_date)
        result_IH = sorted(result_IH)
        result_IF = future_query_service.get_instrument_all("IF", start_date, end_date)
        result_IF = sorted(result_IF)
        result_IC = future_query_service.get_instrument_all("IC", start_date, end_date)
        result_IC = sorted(result_IC)
        result_IM = future_query_service.get_instrument_all("IM", start_date, end_date)
        result_IM = sorted(result_IM)
        result = result_IH + result_IF + result_IC + result_IM
        final_res = []
        for sym in result:
            final_res.append(sym[:6])
        if len(final_res) < 16:
            msg = "可交易期货列表不符合预期, 期货代码列表={}".format(final_res)
            logger.error(msg)
            # self.send_link_message(msg)
            sys.exit(1)
        return final_res

    def get_index_constituent_stock(self, variety, trading_day):
        stocks = []
        res = factor_query_service.hset('INDEX', trading_day, variety, weightType=1)
        for index, row in res.iterrows():
            stocks.append(row['stock'])
        return stocks

    def getType(self, index_type):
        if index_type == "SZ50":
            return "IH"
        if index_type == "HS300":
            return "IF"
        if index_type == "ZZ500":
            return "IC"
        if index_type == "ZZ1000":
            return "IM"

    def get_index_weight(self, parse_date, index_list=index_list):
        df_res_list = []
        for index_type in index_list:
            df = factor_query_service.hset("INDEX", parse_date, index_type, weightType=1)
            df = df.reset_index()
            index_type_name = self.getType(index_type)
            df['type'] = index_type_name
            df['date'] = parse_date
            df = df.rename(columns={'stock': 'symbol'})
            df = df[['date', 'symbol', 'type', 'weight']]
            df_res_list.append(df)
        res = pd.concat(df_res_list)
        index_weight = json.loads(res.to_json(orient='records', double_precision=15))
        return index_weight

    def get_adjfactor(self, parse_date, stock_list):
        ashareeodprices = factor_query_service.get_factor_value('WIND_AShareEODPrices',
                                                                factors=['S_INFO_WINDCODE', 'S_DQ_ADJFACTOR'],
                                                                trade_dt=[parse_date])
        try:
            adjfactor_df = ashareeodprices.set_index('S_INFO_WINDCODE').loc[
                list(set(stock_list) - {'689009.SH'})].reset_index()
            adjfactor_df = adjfactor_df.append(
                pd.Series({'S_INFO_WINDCODE': '689009.SH', 'S_DQ_ADJFACTOR': 1, 'dt': parse_date}), ignore_index=True)
            adjfactor_df['dt'] = parse_date
        except KeyError as e:
            msg = "获取adjfactor失败, KeyError, error_msg={}".format(e)
            logger.error(msg)
            # self.send_link_message(msg)
            sys.exit(1)
            return pd.DataFrame()
        return adjfactor_df

    def get_constituent_stock_info(self, stock_list, trading_day):
        results = Parallel(n_jobs=10, backend=mp)(delayed(get_shares)(i, trading_day) for i in stock_list)
        float_shares_df = pd.DataFrame(results, columns=['Ticker', 'float_shares'])

        all_date_list = [trading_day]
        adjfactor_df_list = []
        for d in all_date_list:
            temp = self.get_adjfactor(d, stock_list)
            adjfactor_df_list.append(temp)
        adjfactor_df = pd.concat(adjfactor_df_list)
        if len(adjfactor_df) == 0:
            logger.error("adjfactor为空")
            sys.exit(1)
        adjfactor_df['dt'] = adjfactor_df['dt'].astype('datetime64[ns]')
        adjfactor_df['S_DQ_ADJFACTOR'] = adjfactor_df['S_DQ_ADJFACTOR'].fillna(1)
        adjfactor_df = adjfactor_df.rename(
            columns={'S_DQ_ADJFACTOR': 'adjfactor', 'S_INFO_WINDCODE': 'stock', 'dt': 'mddate'})
        adjfactor_df = adjfactor_df.set_index(['mddate', 'stock'])
        close_df = factor_query_service.get_factor_value("Basic_factor", stock_list, all_date_list, ['close'])
        close_df = close_df.reset_index()
        close_df['mddate'] = close_df['mddate'].astype('datetime64[ns]')
        close_df = close_df.set_index(['mddate', 'stock'])
        close_adjfactor_df = pd.concat([adjfactor_df, close_df], axis=1)
        close_adjfactor_df = close_adjfactor_df.xs('{} 00:00:00'.format(format_date(trading_day)), level=0)
        if close_adjfactor_df.close.isnull().any():
            msg = "成分股pre_close字段存在空值, 请重新生成!"
            logger.error(msg)
            # self.send_link_message(msg)
            sys.exit(1)
        # raise Exception("preclose exists null")
        if close_adjfactor_df.adjfactor.isnull().any():
            msg = "成分股pre_djfactor字段存在空值, 请重新生成!"
            logger.error(msg)
            # self.send_link_message(msg)
            sys.exit(1)
        # raise Exception("preadjcator exists null")
        if float_shares_df.empty or float_shares_df['float_shares'].isnull().any():
            msg = "成分股float_shares字段存在空值, 请重新生成!"
            logger.error(msg)
            # self.send_link_message(msg)
            sys.exit(1)
        # raise Exception("float_shares exists null")
        constituent_stock_info = pd.concat([float_shares_df.set_index(['Ticker']), close_adjfactor_df], axis=1)
        constituent_stock_info = constituent_stock_info.reset_index()
        # 策略参数生成完成需要校验一下, 检查float_shares等字段是否不为null, 可能出现查询太早导致查询结果为null的情况
        constituent_stock_info = constituent_stock_info.rename(
            columns={"index": "Ticker", "adjfactor": "pre_adjfactor", "close": "pre_close"})
        res = json.loads(constituent_stock_info.to_json(orient='records', double_precision=15))
        return res

    def add_stock_list(self, res: list, to_add):
        help_set = set(res)
        for i in to_add:
            if i not in help_set:
                res.append(i)
                help_set.add(i)
        return res

    def generate(self, next_trading_day, base_date=None, mock=False, batch_run_stock_list=None, load_his_data=None, work_indicator_folder=None,
                 minute_shift=0, work_index_weight_folder=None):
        if base_date is None:
            base_date = next_trading_day
        params = self.params_template.copy()
        params['交易日期'] = str(next_trading_day)
        his_dates = factor_query_service.tradingday(next_trading_day, -7)
        # params['历史数据交易日列表'] = his_dates[:-1]
        # params['期货代码列表'] = self.get_future_trading_instruments(next_trading_day)
        # params['MinuteShiftSec'] = minute_shift
        if batch_run_stock_list is not None:
            params['batch_run_stock_list'] = list(batch_run_stock_list)
        if load_his_data is not None:
            params['load_history_data'] = load_his_data
        if work_indicator_folder is not None:
            params['历史数据目录'] = work_indicator_folder
            params['当日指标值存储目录'] = work_indicator_folder
        if work_index_weight_folder is not None:
            params['指数数据目录'] = work_index_weight_folder

        return json.dumps(params, indent=4, ensure_ascii=False)

    def generate_frontend(self, date, filepath):
        frontend_params = template_frontend_params.copy()
        # frontend_params['参数地址'] = filepath
        frontend_params['path'] = filepath
        frontend_content = json.dumps(frontend_params, indent=4, ensure_ascii=False)
        return frontend_content

    def generate_config(self, date, filepath, replay, zone_ids: list,minute_shift=0):
        config_params = config_tpl.copy()
        # config_params['date'] = str(date)
        config_params['replay'] = replay
        server_conf = []
        for zone_id in zone_ids:
            conf = dict(zoneid="localhost", mobius_udp_cpp=True)
            conf['zoneid'] = zone_id
            conf['offset'] = minute_shift
            server_conf.append(conf)
        if len(zone_ids) > 0:
            config_params['servers'] = server_conf
        config_content = json.dumps(config_params, indent=4, ensure_ascii=False)
        return config_content


if __name__ == "__main__":
    # testcase_base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
    sys.stdout = open(os.devnull, 'w')
    base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"