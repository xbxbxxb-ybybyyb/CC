import struct
import time
import datetime
from loguru import logger
import numpy as np
import pandas as pd
from xdb.hfd_type import DataType
import zlib
import zstd


class Location:
    def __init__(self, symbol, channel, start, end):
        self.symbol = symbol
        self.channel = channel
        self.start = start
        self.end = end


# 从头部解析出来的元信息
class MetaData:
    def __init__(self, version, market_data_type):
        self.version = version
        self.market_data_type = market_data_type
        self.location_map = {}
        self.channel_map = {}
        self.empty_location = Location("", 0, 0, 0)

    def parse_header(self, file_stream, market):
        magic_data = file_stream.read(8)
        ending = "." + market
        if self.market_data_type == DataType.STATICINFO or self.market_data_type == DataType.ETFCREATIONREDEMPTIONINFO:
            _header_size = file_stream.read(8)
            _header_size = struct.unpack('q', _header_size)[0]
            _header_count = _header_size // 34
            if _header_count != _header_size / 34:
                logger.error("解析头文件出错：头文件大小不合规。请检查数据文件是否完整。")
                return
            first_start = -1

            for i in range(_header_count):
                cur_symbol = file_stream.read(34)
                name, channel, start, end = struct.unpack('<16shqq', cur_symbol)
                if i == 0:
                    first_start = start
                name = name[:6].decode().strip(b'\x00'.decode())
                if len(name) > 6:
                    name = name[:6]
                self.location_map[name] = Location(name, channel, start, end)
                if self.market_data_type in [DataType.TICK1S, DataType.TRADE, DataType.ORDER, DataType.CANCEL,
                                             DataType.TICKFULL]:
                    self.channel_map[name + ending] = channel
        else:
            _header_size = file_stream.read(8)
            _header_size = struct.unpack('q', _header_size)[0]
            _header_count = _header_size // 26
            if _header_count != _header_size / 26:
                logger.error("解析头文件出错：头文件大小不合规。请检查数据文件是否完整。")
                return
        # buf = file_stream.read(_header_size)
            first_start = -1

            for i in range(_header_count):
                cur_symbol = file_stream.read(26)
                name, channel, start, end = struct.unpack('<8shqq', cur_symbol)
                if i == 0:
                    first_start = start
                name = name[:6].decode().strip(b'\x00'.decode())
                if len(name) > 6:
                    name = name[:6]
                self.location_map[name] = Location(name, channel, start, end)
                if self.market_data_type in [DataType.TICK1S, DataType.TRADE, DataType.ORDER, DataType.CANCEL, DataType.TICKFULL]:
                    self.channel_map[name + ending] = channel

        if self.market_data_type == DataType.FACTOR:
            col = file_stream.read(first_start - _header_size - 16)
            col_arr = col.decode().split(",")
            format_arr = []
            format_arr.append((col_arr[0], "<i8"))
            for i in range(1, len(col_arr)):
                format_arr.append((col_arr[i], "<f8"))
            self.factor_format_arr = format_arr

    def get_channel_dict(self):
        return self.channel_map

    def get_location(self, symbol):
        # 1 应该替换为默认的空 dataframe
        return self.location_map.get(symbol, self.empty_location)

    def check_symbol(self, symbol):
        symbol = symbol[:6]
        return symbol in self.location_map

    def get_location_map(self):
        return self.location_map


def t(x, suffix):
    return bytes.decode(x) + suffix


class FileLoader:
    def __init__(self, market_data_type, path, market, cached=False):
        self.path = path
        self.market_data_type = market_data_type
        self.market = market
        self.num_map = {}
        self.channel_map = {}
        self.full_loaded = False
        self.data_format_ETF_Component = None
        if market_data_type is DataType.ORDER:
            self.data_format = np.dtype([
                ("symbol", 'S8'),
                ("appl_seq_num", '<u8'), ("order_no", '<u8'),
                ("price", '<f8'),
                ("qty", '<i8'), ("md_time", '<i8'),
                ("receive_time", '<i8'), ("order_index", '<i8'),
                ("local_index", '<i8'),
                ("side", 'S1'), ("type", 'S1'), ("reserved", 'S6'), ])
        elif market_data_type is DataType.TRADE:
            self.data_format = np.dtype([
                ("symbol", 'S8'),
                ("appl_seq_num", '<u8'), ("trade_buy_no", '<u8'),
                ("trade_sell_no", '<u8'), ("trade_price", '<f8'),
                ("trade_qty", '<i8'), ("md_time", '<i8'),
                ("receive_time", '<i8'), ("trade_index", '<i8'),
                ("local_index", '<i8'),
                ("side", 'S1'), ("reserved", 'S7'), ])
        elif market_data_type is DataType.CANCEL:
            self.data_format = np.dtype([
                ("symbol", 'S8'),
                ("appl_seq_num", '<u8'), ("order_no", '<u8'),
                ("order_price", '<f8'),
                ("order_qty", '<i8'), ("md_time", '<i8'),
                ("receive_time", '<i8'), ("order_index", '<i8'),
                ("local_index", '<i8'),
                ("order_side", 'S1'), ("reserved", 'S7'), ])
        elif market_data_type is DataType.TICK1S or market_data_type is DataType.TICKFULL or market_data_type is DataType.TICKEX:
            self.data_format = np.dtype([
                ("symbol", 'S8'),
                ("ask_price1", "<f8"),
                ("ask_price2", "<f8"), ("ask_price3", "<f8"),
                ("ask_price4", "<f8"), ("ask_price5", "<f8"),
                ("ask_price6", "<f8"), ("ask_price7", "<f8"),
                ("ask_price8", "<f8"), ("ask_price9", "<f8"),
                ("ask_price10", "<f8"),

                ("ask_qty1", "<i8"),
                ("ask_qty2", "<i8"), ("ask_qty3", "<i8"),
                ("ask_qty4", "<i8"), ("ask_qty5", "<i8"),
                ("ask_qty6", "<i8"), ("ask_qty7", "<i8"),
                ("ask_qty8", "<i8"), ("ask_qty9", "<i8"),
                ("ask_qty10", "<i8"),

                ("ask_order_nums1", "<i8"),
                ("ask_order_nums2", "<i8"), ("ask_order_nums3", "<i8"),
                ("ask_order_nums4", "<i8"), ("ask_order_nums5", "<i8"),
                ("ask_order_nums6", "<i8"), ("ask_order_nums7", "<i8"),
                ("ask_order_nums8", "<i8"), ("ask_order_nums9", "<i8"),
                ("ask_order_nums10", "<i8"),

                ("bid_price1", "<f8"),
                ("bid_price2", "<f8"), ("bid_price3", "<f8"),
                ("bid_price4", "<f8"), ("bid_price5", "<f8"),
                ("bid_price6", "<f8"), ("bid_price7", "<f8"),
                ("bid_price8", "<f8"), ("bid_price9", "<f8"),
                ("bid_price10", "<f8"),

                ("bid_qty1", "<i8"),
                ("bid_qty2", "<i8"), ("bid_qty3", "<i8"),
                ("bid_qty4", "<i8"), ("bid_qty5", "<i8"),
                ("bid_qty6", "<i8"), ("bid_qty7", "<i8"),
                ("bid_qty8", "<i8"), ("bid_qty9", "<i8"),
                ("bid_qty10", "<i8"),

                ("bid_order_nums1", "<i8"),
                ("bid_order_nums2", "<i8"), ("bid_order_nums3", "<i8"),
                ("bid_order_nums4", "<i8"), ("bid_order_nums5", "<i8"),
                ("bid_order_nums6", "<i8"), ("bid_order_nums7", "<i8"),
                ("bid_order_nums8", "<i8"), ("bid_order_nums9", "<i8"),
                ("bid_order_nums10", "<i8"),

                ("open_px", '<f8'), ("last_px", '<f8'),
                ("high_px", '<f8'), ("low_px", '<f8'),
                ("ask_order_qty", '<i8'), ("bid_order_qty", '<i8'),
                ("ask_avg_px", '<f8'), ("bid_avg_px", '<f8'),
                ("appl_seq_num", '<i8'), ("md_time", '<i8'), ("receive_time", '<i8'),
                ("total_volume", '<i8'), ("total_amount", '<f8'),
                ("volume", '<i8'), ("total_num_trades", '<i8'),
                ("last_local_index", '<i8'),
                ("trading_phase_code", 'S1'), ("source", 'S1'), ("reserved", 'S6')])
        # elif market_data_type is DataType.TICKEX:
        #     self.data_format = np.dtype([
        #         ("symbol", 'S8'),
        #         ("ask_price1", "<f8"),
        #         ("ask_price2", "<f8"), ("ask_price3", "<f8"),
        #         ("ask_price4", "<f8"), ("ask_price5", "<f8"),
        #         ("ask_price6", "<f8"), ("ask_price7", "<f8"),
        #         ("ask_price8", "<f8"), ("ask_price9", "<f8"),
        #         ("ask_price10", "<f8"),
        # 
        #         ("ask_qty1", "<i8"),
        #         ("ask_qty2", "<i8"), ("ask_qty3", "<i8"),
        #         ("ask_qty4", "<i8"), ("ask_qty5", "<i8"),
        #         ("ask_qty6", "<i8"), ("ask_qty7", "<i8"),
        #         ("ask_qty8", "<i8"), ("ask_qty9", "<i8"),
        #         ("ask_qty10", "<i8"),
        # 
        #         ("ask_order_nums1", "<i8"),
        #         ("ask_order_nums2", "<i8"), ("ask_order_nums3", "<i8"),
        #         ("ask_order_nums4", "<i8"), ("ask_order_nums5", "<i8"),
        #         ("ask_order_nums6", "<i8"), ("ask_order_nums7", "<i8"),
        #         ("ask_order_nums8", "<i8"), ("ask_order_nums9", "<i8"),
        #         ("ask_order_nums10", "<i8"),
        # 
        #         ("bid_price1", "<f8"),
        #         ("bid_price2", "<f8"), ("bid_price3", "<f8"),
        #         ("bid_price4", "<f8"), ("bid_price5", "<f8"),
        #         ("bid_price6", "<f8"), ("bid_price7", "<f8"),
        #         ("bid_price8", "<f8"), ("bid_price9", "<f8"),
        #         ("bid_price10", "<f8"),
        # 
        #         ("bid_qty1", "<i8"),
        #         ("bid_qty2", "<i8"), ("bid_qty3", "<i8"),
        #         ("bid_qty4", "<i8"), ("bid_qty5", "<i8"),
        #         ("bid_qty6", "<i8"), ("bid_qty7", "<i8"),
        #         ("bid_qty8", "<i8"), ("bid_qty9", "<i8"),
        #         ("bid_qty10", "<i8"),
        # 
        #         ("bid_order_nums1", "<i8"),
        #         ("bid_order_nums2", "<i8"), ("bid_order_nums3", "<i8"),
        #         ("bid_order_nums4", "<i8"), ("bid_order_nums5", "<i8"),
        #         ("bid_order_nums6", "<i8"), ("bid_order_nums7", "<i8"),
        #         ("bid_order_nums8", "<i8"), ("bid_order_nums9", "<i8"),
        #         ("bid_order_nums10", "<i8"),
        # 
        #         ("open_px", '<f8'), ("last_px", '<f8'),
        #         ("high_px", '<f8'), ("low_px", '<f8'),
        #         ("ask_order_qty", '<i8'), ("bid_order_qty", '<i8'),
        #         ("ask_avg_px", '<f8'), ("bid_avg_px", '<f8'),
        #         ("appl_seq_num", '<i8'), ("md_time", '<i8'), ("receive_time", '<i8'),
        #         ("total_volume", '<i8'), ("total_amount", '<f8'),
        #         ("volume", '<i8'), ("total_num_trades", '<i8'),
        #         ("last_local_index", '<i8'),
        #         ("trading_phase_code", 'S1'), ("source", 'S1'), ("reserved", 'S6')])
        elif market_data_type is DataType.ENHANCEDTRADE:
            self.data_format = np.dtype([
                ("symbol", 'S8'), ("appl_seq_num", '<i8'), ("receive_time", '<i8'),
                ("md_time", '<i4'), ("trade_buy_no", '<i4'), ("trade_sell_no", '<i4'), ("buy_order_time", '<i4'),
                ("sell_order_time", '<i4'), ("trade_bs_flag", '<i4'),("trade_price", '<f4'),("trade_qty", '<f4'),
                ("buy_order_price", '<f4'),("buy_order_amount", '<f4'),("sell_order_price", '<f4'),("sell_order_amount", '<f4'),
                ("buy1_price", '<f4'),("buy1_order_qty", '<f4'),("sell1_price", '<f4'),("sell1_order_qty", '<f4')])
        elif market_data_type is DataType.STATUS:
            self.data_format = np.dtype([
                ("symbol", 'S8'), ("appl_seq_num", '<i8'), ("md_time", '<i8'),
                ("receive_time", '<i8'), ("local_index", '<i8'), ("source", 'u1'), ("reserved", 'S7')])
        elif market_data_type is DataType.KLINE1MIN:
            self.data_format = np.dtype([
                ("symbol", 'S8'),
                ("open_price", '<f8'), ("close_price", '<f8'),
                ("high_price", '<f8'), ("low_price", '<f8'),
                ("num_trades", '<i8'), ("total_volume", '<i8'), ("total_amount", '<f8'),
                ("md_time", '<i8'), ("receive_time", '<i8'), ("source", 'S1'), ("reserved", 'S7'), ])
        elif market_data_type is DataType.INDEXTICKEX:
            self.data_format = np.dtype([
                ("symbol", 'S8'), ("md_time", '<i8'), ("receive_time", '<i8'), ("pre_close_px", '<f8'),
                ("open_price", '<f8'), ("close_price", '<f8'), ("high_price", '<f8'), ("low_price", '<f8'),
                ("last_price", '<f8'), ("total_amount", '<f8'), ("total_volume", '<i8'),
                ("source", 'S1'), ("reserved", 'S7'), ])
        elif market_data_type is DataType.FUTURETICKEX:
            self.data_format = np.dtype([("symbol", "<S8"),
                                         ("ask_p0", "<f8"), ("ask_p1", "<f8"), ("ask_p2", "<f8"), ("ask_p3", "<f8"),
                                         ("ask_p4", "<f8"),
                                         ("ask_qty0", "<i8"), ("ask_qty1", "<i8"), ("ask_qty2", "<i8"),
                                         ("ask_qty3", "<i8"), ("ask_qty4", "<i8"),
                                         ("bid_p0", "<f8"), ("bid_p1", "<f8"), ("bid_p2", "<f8"), ("bid_p3", "<f8"),
                                         ("bid_p4", "<f8"),
                                         ("bid_qty0", "<i8"), ("bid_qty1", "<i8"), ("bid_qty2", "<i8"),
                                         ("bid_qty3", "<i8"), ("bid_qty4", "<i8"),
                                         ("pre_close_px", "<f8"), ("open", "<f8"), ("last", "<f8"), ("high", "<f8"),
                                         ("low", "<f8"),
                                         ("pre_open_interest", "<i8"), ("pre_settle_price", "<f8"),
                                         ("open_interest", "<i8"), ("settle_price", "<f8"),
                                         ("md_time", "<i8"), ("receive_time", "<i8"), ("total_volume", "<i8"),
                                         ("total_amount", "<f8"),
                                         ("trading_phase_code", 'S1'), ("source", 'S1'), ("reserved", 'S6')])
        elif market_data_type is DataType.DAILYDATA:
            self.data_format = np.dtype([
                ("md_date", 'S8'), ("symbol", 'S8'),
                ("pre_close", '<f8'), ("open", '<f8'),
                ("close", '<f8'), ("high", '<f8'),
                ("low", '<f8'), ("vwap", '<f8'),
                ("chg", '<f8'), ("pct_chg", '<f8'),
                ("turn", '<f8'), ("free_turn", '<f8'),
                ("volume", '<f8'), ("amt", '<f8'), ("dealnum", '<i8'), ("swing", '<f8'),
                ("re_ipo_chg", '<f8'), ("rel_ipo_pct_chg", '<f8'),
                ("mdc_maxpx", '<f8'), ("mdc_minpx", '<f8'),
                ("last_trade_day", 'S8'), ("adjfactor", '<f8'),
                ("maxupordown", '<f8'), ("total_shares", '<f8'),
                ("free_float_shares", '<f8'), ("float_a_shr_today", '<f8'),
                ("float_a_shares", '<f8'), ("share_totala", '<f8'),
                ("pre_close_badj", '<f8'), ("open_badj", '<f8'),
                ("high_badj", '<f8'), ("low_badj", '<f8'),
                ("close_badj", '<f8'), ("re_ipo_chg_badj", '<f8'),
                ("rel_ipo_pct_chg_badj", '<f8'),
                ("trade_status", 'S1'), ("reserved", 'S7'), ])
        elif market_data_type is DataType.STATICINFO:
            self.data_format = np.dtype([
                ("htsc_security_id", 'S16'), ("security_id", 'S8'),
                ("symbol", 'S128'), ("chi_spelling", 'S64'),
                ("english_name", 'S128'), ("list_date", '<i8'),
                ("currency", 'S8'), ("outstanding_share", '<i8'),
                ("public_float_share_qty", '<i8'), ("md_date", '<i8'),
                ("preclose_px", '<f8'), ("max_px", '<f8'),
                ("min_px", '<f8'), ("lot_size", '<i8'), ("exchange_date", '<i8'), ("exchange_symbol", 'S16'),
                ("tick_size", '<f8'), ("px_accuracy", '<i8'),
                ("hk_spread_table_code", 'S8'), ("pre_settle_px", '<f8'),
                ("pre_iopv", '<f8'), ("option_contract_id", 'S32'),
                ("option_contract_symbol", 'S32'), ("option_underlying_security_id", 'S8'),
                ("option_underlying_symbol", 'S16'), ("option_underlying_type", 'S8'),
                ("option_contract_multiplier_unit", '<i8'), ("option_exercise_price", '<f8'),
                ("option_start_date", '<i8'), ("option_end_date", '<i8'),
                ("option_exercise_date", '<i8'), ("option_delivery_date", '<i8'),
                ("option_expire_date", '<i8'), ("option_total_long_position", '<i8'),
                ("option_security_close_px", '<f8'), ("option_settl_price", '<f8'),
                ("option_underlying_close_px", '<f8'), ("option_daily_price_up_limit", '<f8'),
                ("option_daily_price_down_limit", '<f8'), ("option_margin_unit", '<f8'),
                ("option_margin_ratio_param1", '<f8'), ("option_margin_ratio_param2", '<f8'),
                ("option_round_lot", '<i8'), ("option_lmt_ord_min_floor", '<i8'),
                ("option_lmt_ord_max_floor", '<i8'), ("option_mkt_ord_min_floor", '<i8'),
                ("option_mkt_ord_max_floor", '<i8'), ("option_tick_size", '<f8'),
                ("option_security_status_flag", 'S8'), ("option_carry_interest_date", '<i8'),
                ("option_early_expire_date", '<i8'), ("option_strategy_security_id", 'S8'),
                ("fi_pledged_security_id", 'S8'), ("fi_open_time", '<i8'),
                ("fi_close_time", '<i8'), ("fi_face_amount", 'f8'),
                ("fi_issue_price", '<f8'), ("fi_guaranteed_interest_rate", '<f8'),
                ("fi_base_interest_rate", '<f8'), ("fi_quoted_margin", '<f8'),
                ("fi_total_issuance", '<f8'), ("fi_issue_start_date", '<i8'),
                ("fi_issue_end_date", '<i8'), ("fi_list_date", '<i8'),
                ("fi_expire_date", '<i8'), ("fi_total_short_sell_quota", '<f8'),
                ("fi_dealer_short_sell_quota", '<f8'), ("fi_preclose_px", '<f8'),
                ("fi_pre_weighted_px", '<f8'), ("option_contract_position", '<i8'),
                ("option_buy_qty_upper_limit", '<i8'), ("option_sell_qty_upper_limit", '<i8'),
                ("option_market_order_buy_qty_upper_limit", '<i8'), ("option_market_order_sell_qty_upper_limit", '<i8'),
                ("option_quote_order_buy_qty_upper_limit", '<i8'), ("option_quote_order_sell_qty_upper_limit", '<i8'),
                ("option_buy_qty_unit", '<i8'), ("option_sell_qty_unit", '<i8'),
                ("option_last_sell_margin", '<f8'), ("option_sell_margin", '<f8'),
                ("option_combination_strategy", 'S128'), ("instrument_id", 'S8'),
                ("instrument_name", 'S32'), ("exchange_inst_id", 'S8'),
                ("product_id", 'S8'), ("max_market_order_volume", '<i8'),
                ("min_market_order_volume", '<i8'), ("max_limit_order_volume", '<i8'),
                ("min_limit_order_volume", '<i8'), ("volume_multiple", '<i8'),
                ("create_date", '<i8'), ("expire_date", '<i8'),
                ("start_deliv_date", '<i8'), ("end_deliv_date", '<i8'),
                ("long_margin_ratio", '<f8'), ("short_margin_ratio", '<f8'),
                ("strike_price", '<f8'), ("pre_open_interest", '<f8'),
                ("former_symbol", 'S128'), ("delist_date", '<i8'),
                ("buy_qty_unit", '<i8'), ("sell_qty_unit", '<i8'),
                ("buy_qty_upper_limit", '<i8'), ("sell_qty_upper_limit", '<i8'),
                ("buy_qty_lower_limit", '<i8'), ("sell_qty_lower_limit", '<i8'),
                ("pos_upper_limit_px", '<f8'), ("pos_lower_limit_px", '<f8'),
                ("base_contract_id", 'S8'), ("interest_accrual_date", '<i8'),

                ("security_id_source", '<i4'), ("security_type", '<i4'),
                ("security_sub_type", '<i4'), ("loan_margin_indicator", '<i4'),
                ("ipo_profitable", '<i4'), ("diff_rights_indicator", '<i4'),
                ("sh_hk_connect", '<i4'), ("sz_hk_connect", '<i4'),
                ("fi_time_limit", '<i4'), ("option_adjust_times", '<i4'),
                ("vcm_flag", '<i4'), ("cas_flag", '<i4'),
                ("pos_flag", '<i4'), ("data_multiple_power_of_10", '<i4'),
                ("fi_trade_product_type", '<i2'), ("delivery_year", '<i2'),
                ("delivery_month", '<i2'), ("trading_phase_code", 'S1'),

                ("option_option_type", 'S1'), ("option_call_or_put", 'S1'),
                ("option_update_version", 'S1'), ("option_price_limit_type", 'S1'),
                ("fi_security_property", 'S1'), ("fi_security_status", 'S1'),
                ("fi_issue_mode", 'S1'), ("fi_interest_type", 'S1'),
                ("fi_interest_frequency", 'S1'), ("fi_national_debt_type", 'S1'),
                ("fi_issue_method", 'S1'), ("option_list_type", 'S1'),
                ("option_delivery_type", 'S1'), ("option_market_maker_flag", 'S1'),
                ("position_type", 'S1'), ("max_margin_side_algorithm", 'S1'),
                ("short_sell_flag", '<?'), ("fi_cross_market", '<?'),
                ("fi_short_sell_flag", '<?'), ("reserved", 'S6'), ])
        elif market_data_type is DataType.ETFCREATIONREDEMPTIONINFO:
            self.data_format = np.dtype([
                ("htsc_security_id", 'S16'), ("security_id", 'S8'),
                ("symbol", 'S128'), ("former_symbol", 'S128'),
                ("md_date", '<i8'), ("md_time", '<i8'),
                ("trading_day", '<i8'), ("pre_trading_day", '<i8'),
                ("security_id_source", '<i4'), ("security_type", '<i4'),
                ("creation_id", 'S8'),("creation_symbol", 'S128'),("redemption_id", 'S8'),("redemption_symbol", 'S128'),
                ("creation_redemption_capital_id", 'S8'),("creation_redemption_capital_symbol", 'S128'),
                ("cross_source_capital_id", 'S8'),("cross_source_capital_symbol", 'S128'),
                ("fund_management_company", 'S128'),("underlying_security_id", 'S8'),

                ("creation_redemption_unit", '<f8'), ("estimate_cash_component", '<f8'),("max_cash_ratio", '<f8'),
                ("cash_component", '<f8'),
                ("nav_per_cu", '<f8'), ("nav", '<f8'),("dividend_per_cu", '<f8'), ("creation_limit", '<f8'),
                ("redemption_limit", '<f8'), ("creation_limit_per_user", '<f8'),("redemption_limit_per_user", '<f8'),
                ("net_creation_limit", '<f8'), ("net_redemption_limit", '<f8'), ("net_creation_limit_per_user", '<f8'),
                ("net_redemption_limit_per_user", '<f8'),
                ("underlying_security_id_source", '<i4'), ("data_multiple_power_of_10", '<i4'),
                ("is_publish", '<?'), ("is_allow_creation", '<?'),("is_allow_redemption", '<?'), ("cross_market", '<?'),
                ("reserved", 'S4'), ("record_num", '<i8'), ("total_record_num", '<i8'),])

            self.data_format_ETF_Component = np.dtype([
                ("htsc_security_id", 'S16'), ("security_id", 'S8'),
                ("symbol", 'S128'), ("security_id_source", '<i4'),("substitute_flag", '<i4'), ("component_share", '<f8'),
                ("premium_ratio", '<f8'), ("creation_cash_substitute", '<f8'), ("redemption_cash_substitute", '<f8'),
                ("total_cash_substitute", '<f8'), ("discount_ratio", '<f8'),])

        elif market_data_type is DataType.FACTOR:
            self.data_format = None
        else:
            self.data_format = None
            logger.error("market data type error, please check valid market data types and retry.")

        self._open_file(path)
        self.daily_data_store = None
        if market_data_type != DataType.DAILYDATA:
            self._load_file_meta_data()
        else:
            self.read_dailydata()

    def _open_file(self, path):
        try:
            self.file_stream = open(path, 'rb')
        except Exception as r:
            logger.error("数据文件读取错误{}，请检查参数是否正确".format(r))
            self.file_stream = None
            raise Exception("Read data file error {}，please check inputs".format(r))
        return

    def _load_file_meta_data(self):
        # 解析文件的头部
        if self.file_stream is None:
            logger.error("解析Header失败：文件未打开！")
            return
        self.meta_data = MetaData(1, self.market_data_type)
        # 解析 symbol 的 start 和 end
        self.meta_data.parse_header(self.file_stream, self.market)

    def read_dailydata(self):
        if self.file_stream is None:
            logger.error("加载日频数据失败：文件未打开！")
            self.daily_data_store = pd.DataFrame()
            return
        if self.daily_data_store == None:
            buf = self.file_stream.read()
            df = pd.DataFrame(np.frombuffer(buf, self.data_format))
            if df.empty:
                logger.error("加载日频数据失败：日频数据为空！")
                self.daily_data_store = pd.DataFrame()
                return
            df['md_date'] = df['md_date'].apply(lambda x: x.decode())
            df['symbol'] = df['symbol'].apply(lambda x: x.decode())
            df['trade_status'] = df['trade_status'].apply(lambda x: x.decode())
            df['last_trade_day'] = df['last_trade_day'].apply(lambda x: x.decode())
            df.drop(columns=['reserved'], inplace=True)
            self.daily_data_store = df

    def load_dailydata(self, date, symbol):
        df = self.daily_data_store
        if df.empty:
            return df
        tmp_symbol = symbol.split('.')[0]
        d_data = df[df["symbol"] == tmp_symbol].copy()
        if d_data.empty:
            logger.warning("获取数据失败: 标的在当前交易日无相关存储信息！标的={}, 日期={}".format(symbol, date))
        d_data["symbol"] = symbol
        return d_data

    def load_factor(self, symbol, data_type):
        if self.file_stream == None:
            logger.error("symbol={}, 数据源文件不存在", symbol)
            return pd.DataFrame()
        loc = self.meta_data.get_location(symbol[:6])
        start = loc.start
        end = loc.end
        if len(loc.symbol) == 0:
            logger.error("未找到数据: symbol={}, 请检查标的及后缀是否正确，或检查标的是否交易", symbol)
            return pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            logger.error("Header信息错误: symbol={}, start={}, end={}", symbol, start, end)
            return pd.DataFrame()
        if self.meta_data.factor_format_arr is None:
            logger.error("数据格式错误: 因子数据格式为空！")
            return pd.DataFrame()
        self.file_stream.seek(start, 0)
        _data = self.file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)
        df = pd.DataFrame(
            np.frombuffer(uncompress, self.meta_data.factor_format_arr))  # copy data, might be time consuming

        return df

    def load_ETF_symbol(self, date, symbol):
        if self.file_stream == None:
            logger.error("date={}, symbol={}, 数据源文件不存在", date, symbol)
            return pd.DataFrame(), pd.DataFrame()
        loc = self.meta_data.get_location(symbol[:6])
        start = loc.start
        end = loc.end
        if len(loc.symbol) == 0:
            logger.error("未找到数据: symbol={}, 请检查标的及后缀是否正确，或检查标的是否交易", symbol)
            return pd.DataFrame(), pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            logger.error("Header信息错误: symbol={}, start={}, end={}", symbol, start, end)
            return pd.DataFrame(), pd.DataFrame()
        if self.data_format is None:
            logger.error("数据格式错误: 数据格式为空！")
            return pd.DataFrame(), pd.DataFrame()
        self.file_stream.seek(start, 0)
        _data = self.file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)

        ETF_const_info = pd.DataFrame(np.frombuffer(uncompress[:1152], self.data_format))
        ETF_component_info = pd.DataFrame(np.frombuffer(uncompress[1152:], self.data_format_ETF_Component))

        def decode_bytes(x):
            if isinstance(x, pd.Series):
                return x.apply(lambda x: x.decode())
            else:
                raise RuntimeError("input data is not series")

        ETF_const_info[['htsc_security_id','security_id', 'symbol', 'former_symbol', 'creation_id',
                        'creation_symbol', 'redemption_id', 'redemption_symbol',
                        'creation_redemption_capital_id', 'creation_redemption_capital_symbol',
                        'cross_source_capital_id', 'cross_source_capital_symbol',
                        'fund_management_company', 'underlying_security_id']] = ETF_const_info[
            ['htsc_security_id','security_id', 'symbol', 'former_symbol', 'creation_id',
                        'creation_symbol', 'redemption_id', 'redemption_symbol',
                        'creation_redemption_capital_id', 'creation_redemption_capital_symbol',
                        'cross_source_capital_id', 'cross_source_capital_symbol',
                        'fund_management_company', 'underlying_security_id']].apply(decode_bytes,axis=1)
        ETF_const_info = ETF_const_info.drop(columns=['reserved'])

        ETF_component_info[["htsc_security_id", "htsc_security_id", "symbol"]] = ETF_component_info[
            ["htsc_security_id", "htsc_security_id", "symbol"]].apply(decode_bytes,axis=1)

        return ETF_const_info, ETF_component_info

    def load_symbol(self, date, symbol, market_data_type):
        if self.file_stream == None:
            logger.error("date={}, symbol={}, 数据源文件不存在", date, symbol)
            return pd.DataFrame()
        loc = self.meta_data.get_location(symbol[:6])
        start = loc.start
        end = loc.end
        if len(loc.symbol) == 0:
            logger.error("未找到数据: symbol={}, 请检查标的及后缀是否正确，或检查标的是否交易", symbol)
            return pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            logger.error("Header信息错误: symbol={}, start={}, end={}", symbol, start, end)
            return pd.DataFrame()
        if self.data_format is None:
            logger.error("数据格式错误: 数据格式为空！")
            return pd.DataFrame()
        self.file_stream.seek(start, 0)
        _data = self.file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)

        df = pd.DataFrame(np.frombuffer(uncompress, self.data_format))  # copy data, might be time consuming

        isSH = ".SH" in symbol

        if market_data_type == DataType.STATICINFO:
            df = df.drop(columns=['reserved'])
            df['htsc_security_id'] = df['htsc_security_id'].apply(lambda x: x.decode())
            df['security_id'] = df['security_id'].apply(lambda x: x.decode())
            df['symbol'] = df['symbol'].apply(lambda x: x.decode())
            df['product_id'] = df['product_id'].apply(lambda x: x.decode())
            df['instrument_id'] = df['instrument_id'].apply(lambda x: x.decode())
            df['instrument_name'] = df['instrument_name'].apply(lambda x: x.decode())
            df['exchange_inst_id'] = df['exchange_inst_id'].apply(lambda x: x.decode())
            return df
        elif market_data_type == DataType.STATUS:
            df = df.drop(columns=['reserved'])
            df['symbol'] = df['symbol'].apply(lambda x: x.decode())
            return df

        df['symbol'] = symbol
        df["md_date"] = date

        if market_data_type == DataType.TICKEX:
            df = df.sort_values(by="md_time", ascending=True)
        # create
        sta = time.time()
        # timeList = df["md_time"].values
        # mdtime = int(timeList[0])
        # ms = mdtime % 1000
        ti = date + " 000000"
        timeStruct = time.strptime(ti, "%Y%m%d %H%M%S")
        start_timestamp = time.mktime(timeStruct)
        # start_timestamp = int(time.mktime(datetime.date.today().timetuple()))
        df["timestamp"] = np.apply_along_axis(lambda x: np.round(start_timestamp + self.time_2_sec(x), 3),
                                              arr=df["md_time"].values, axis=0)

        # time_arr = []

        # for i in timeList:
        # new_timestamp = round(start_timestamp + self.calc_sec_diff(int(timeList[i]), int(timeList[i - 1])), 3)
        # time_arr.append(round(start_timestamp + self.time_2_sec(i), 3))
        # start_timestamp = new_timestamp
        # df["timestamp"] = time_arr
        # print("create timestamp cost = " + str(time.time() - sta))

        if market_data_type == DataType.TICK1S or market_data_type == DataType.TICKFULL or market_data_type == DataType.TICKEX:
            df = df.drop(columns=['source', 'reserved'])
            df['trading_phase_code'] = df['trading_phase_code'].apply(lambda x: x.decode())
            df = df.loc[:, ['symbol', "md_date", 'md_time', 'timestamp',"appl_seq_num", 'open_px', 'last_px', 'high_px', 'low_px',
                            'ask_order_qty', 'bid_order_qty', 'ask_avg_px', 'bid_avg_px',
                            'total_volume', 'total_amount', 'volume', 'total_num_trades',
                            'trading_phase_code', "last_local_index", 'ask_price1', 'ask_price2', 'ask_price3', 'ask_price4',
                            'ask_price5', 'ask_price6', 'ask_price7', 'ask_price8', 'ask_price9',
                            'ask_price10', 'ask_qty1', 'ask_qty2', 'ask_qty3', 'ask_qty4',
                            'ask_qty5', 'ask_qty6', 'ask_qty7', 'ask_qty8', 'ask_qty9', 'ask_qty10',
                            'ask_order_nums1', 'ask_order_nums2', 'ask_order_nums3',
                            'ask_order_nums4', 'ask_order_nums5', 'ask_order_nums6',
                            'ask_order_nums7', 'ask_order_nums8', 'ask_order_nums9',
                            'ask_order_nums10', 'bid_price1', 'bid_price2', 'bid_price3',
                            'bid_price4', 'bid_price5', 'bid_price6', 'bid_price7', 'bid_price8',
                            'bid_price9', 'bid_price10', 'bid_qty1', 'bid_qty2', 'bid_qty3',
                            'bid_qty4', 'bid_qty5', 'bid_qty6', 'bid_qty7', 'bid_qty8', 'bid_qty9',
                            'bid_qty10', 'bid_order_nums1', 'bid_order_nums2', 'bid_order_nums3',
                            'bid_order_nums4', 'bid_order_nums5', 'bid_order_nums6',
                            'bid_order_nums7', 'bid_order_nums8', 'bid_order_nums9',
                            'bid_order_nums10']]

        # elif market_data_type == DataType.TICKEX:
        #     df = df.drop(columns=['source', 'reserved', "appl_seq_num"])
        #     # df['trading_phase_code'] = df['trading_phase_code'].apply(lambda x: x.decode())
        #     df = df.loc[:, ['symbol', "md_date", 'md_time', 'timestamp', 'open_px', 'last_px', 'high_px',
        #                     'low_px', 'ask_order_qty', 'bid_order_qty', 'ask_avg_px', 'bid_avg_px',
        #                     'total_volume', 'total_amount','volume', 'num_trades',
        #                     'last_local_index', 'ask_price1', 'ask_price2', 'ask_price3', 'ask_price4',
        #                     'ask_price5', 'ask_price6', 'ask_price7', 'ask_price8', 'ask_price9',
        #                     'ask_price10', 'ask_qty1', 'ask_qty2', 'ask_qty3', 'ask_qty4',
        #                     'ask_qty5', 'ask_qty6', 'ask_qty7', 'ask_qty8', 'ask_qty9', 'ask_qty10',
        #                     'ask_order_nums1', 'ask_order_nums2', 'ask_order_nums3',
        #                     'ask_order_nums4', 'ask_order_nums5', 'ask_order_nums6',
        #                     'ask_order_nums7', 'ask_order_nums8', 'ask_order_nums9',
        #                     'ask_order_nums10', 'bid_price1', 'bid_price2', 'bid_price3',
        #                     'bid_price4', 'bid_price5', 'bid_price6', 'bid_price7', 'bid_price8',
        #                     'bid_price9', 'bid_price10', 'bid_qty1', 'bid_qty2', 'bid_qty3',
        #                     'bid_qty4', 'bid_qty5', 'bid_qty6', 'bid_qty7', 'bid_qty8', 'bid_qty9',
        #                     'bid_qty10', 'bid_order_nums1', 'bid_order_nums2', 'bid_order_nums3',
        #                     'bid_order_nums4', 'bid_order_nums5', 'bid_order_nums6',
        #                     'bid_order_nums7', 'bid_order_nums8', 'bid_order_nums9',
        #                     'bid_order_nums10']]
        elif market_data_type == DataType.FUTURETICKEX:
            df['trading_phase_code'] = df['trading_phase_code'].apply(lambda x: x.decode())
            df = df.drop(columns=['source', 'reserved'])
            df = df.loc[:,
                 ['symbol', 'md_date', 'md_time', 'ask_p0', 'ask_p1', 'ask_p2', 'ask_p3', 'ask_p4', 'ask_qty0', 'ask_qty1', 'ask_qty2',
                  'ask_qty3', 'ask_qty4', 'bid_p0', 'bid_p1', 'bid_p2', 'bid_p3', 'bid_p4', 'bid_qty0', 'bid_qty1',
                  'bid_qty2', 'bid_qty3', 'bid_qty4', 'pre_close_px', 'open', 'last', 'high', 'low',
                  'pre_open_interest', 'pre_settle_price', 'open_interest', 'settle_price', 'receive_time',
                  'total_volume', 'total_amount', 'trading_phase_code']]

        elif market_data_type == DataType.INDEXTICKEX:
            df = df.drop(columns=['source', 'reserved'])
        elif market_data_type == DataType.ORDER:
            df = df.drop(columns=["receive_time", 'reserved'])
            if date >= "20240617" and isSH:
                df["order_index"] = df['appl_seq_num']
            df['side'] = df['side'].apply(lambda x: int(x.decode()))
            df['type'] = df['type'].apply(lambda x: str(x.decode()))
        elif market_data_type == DataType.TRADE:
            if date >= "20240617" and isSH:
                df["trade_index"] = df['appl_seq_num']
            df = df.drop(columns=["receive_time", 'reserved'])
            df['side'] = df['side'].apply(lambda x: int(x.decode()))
        elif market_data_type == DataType.CANCEL:
            if date >= "20240617" and isSH:
                df["order_index"] = df['appl_seq_num']
            df = df.drop(columns=["receive_time", 'reserved'])
            df["order_side"] = df['order_side'].apply(lambda x: int(x.decode()))

        return df

    def time_2_sec(self, time):
        hm1 = time % 1000
        s1 = (time % 100000) // 1000
        m1 = (time // 100000) % 100
        h1 = time // 10000000
        return h1 * 3600 + m1 * 60 + s1 + hm1 / 1000

    def calc_sec_diff(self, time1, time2):

        if time1 == time2:
            return 0

        if time1 < time2:
            time1, time2 = time2, time1

        hm1 = time1 % 1000
        s1 = int((time1 % 100000) / 1000)
        m1 = int(time1 / 100000) % 100
        h1 = int(time1 / 10000000)

        hm2 = time2 % 1000
        s2 = int((time2 % 100000) / 1000)
        m2 = int(time2 / 100000) % 100
        h2 = int(time2 / 10000000)

        res_hr = h1 - h2
        res_min = m1 - m2
        res_sec = s1 - s2
        res_ms = hm1 - hm2

        if res_ms < 0:
            res_ms += 1000
            res_sec -= 1

        if res_sec < 0:
            res_sec += 60
            res_min -= 1

        if res_min < 0:
            res_min += 60
            res_hr -= 1

        if res_hr < 0:
            print("time diff error!")

        return res_hr * 3600 + res_min * 60 + res_sec + res_ms / 1000

    def _load_channel(self, symbol):
        if self.file_stream == None:
            logger.error("symbol={}, 数据源文件不存在", symbol)
            return {}
        channel_dict = self.meta_data.get_channel_dict()
        if symbol == "":
            return channel_dict
        else:

            if symbol in channel_dict:
                return {symbol : channel_dict[symbol]}
            else:
                logger.error("数据读取错误: 未查询到标的={}在该日的相关信息！".format(symbol))
                return {symbol : 0}


    def _load_info(self, market_data_type, symbol, market):
        if self.file_stream == None:
            logger.error("数据源文件不存在")
            return {}
        data_size = -1
        if market_data_type == DataType.ORDER:
            data_size = 80
        elif market_data_type == DataType.TRADE:
            data_size = 88
        elif market_data_type == DataType.CANCEL:
            data_size = 80
        elif market_data_type == DataType.TICK1S or market_data_type == DataType.TICKFULL:
            data_size = 624
        else:
            logger.error("参数错误: 仅支持查询 Order, Trade, Cancel, Tick1s, TickFull的数量。")
            return {}
        if symbol == "":
            if self.full_loaded:
                return self.num_map
            else:
                for v in self.meta_data.location_map.values():
                    if v.end == v.start:
                        logger.warn("数据读取异常: 标的={} start end偏移量相同！".format(symbol))
                        continue
                    self.file_stream.seek(v.start, 0)
                    uncom = zstd.ZSTD_uncompress(self.file_stream.read(v.end - v.start))
                    self.num_map[v.symbol + "." + market] = int(len(uncom) / data_size)
                self.full_loaded = True
                return self.num_map
        else:
            if self.full_loaded:
                if symbol in self.num_map:
                    return {symbol: self.num_map[symbol[:6]]}
                else:
                    logger.error("数据读取错误: 未查询到标的={}在该日的相关信息！".format(symbol))
                    return {symbol: 0}
            else:
                if self.check_symbol_exist(symbol):
                    v = self.meta_data.get_location(symbol[:6])
                    if v.end == v.start:
                        logger.error("数据读取错误: 标的={} start end偏移量相同！".format(symbol))
                        return {v.symbol: 0}
                    self.file_stream.seek(v.start, 0)
                    uncom = zstd.ZSTD_uncompress(self.file_stream.read(v.end - v.start))
                    data_num = int(len(uncom) / data_size)
                    self.num_map[symbol] = data_num
                    return {v.symbol: data_num}
                else:
                    logger.error("数据读取错误: 未查询到标的={}在该日的相关信息！".format(symbol))
                    return {symbol: 0}

    def check_symbol_exist(self, symbol):
        return self.meta_data.check_symbol(symbol)

    # 获取全部标的
    # def load_all_symbol(self):
    #     if self.file_stream is None:
    #         logger.error("解析Header失败：文件未打开！")
    #         return
    #     loc_map = self.meta_data.get_location_map()
    #     max_size = 0
    #     max_symbol = ""
    #     if self.market_data_type is DataType.TRADE:
    #         s = "trade"
    #     elif self.market_data_type is DataType.ORDER:
    #         s = "order"
    #     elif self.market_data_type is DataType.CANCEL:
    #         s = "cancel"
    #     elif self.market_data_type is DataType.TICK1S:
    #         s = "tick"
    #     total_time = 0
    #     cnt = 0
    #     for k, v in loc_map.items():
    #         s = time.time()
    #         start = v.start
    #         end = v.end
    #         if end <= start or end < 0 or start < 0:
    #             print("Symbol meta data error!")
    #             return
    #         if self.data_format is None:
    #             print("marketdata types error")
    #         if end - start > max_size:
    #             max_symbol = k
    #             max_size = end - start
    #         self.file_stream.seek(start, 0)
    #         _data = self.file_stream.read(end - start)
    #         df = pd.DataFrame(np.frombuffer(_data, self.data_format))  # copy data, might be time consuming
    #         e = time.time()
    #         total_time += (e - s)
    #         cnt += 1
    #         # df.to_pickle(f"/data/group/800445/marketdata/20230224/pickle_data/{s}/20230224_{k}_{s}.pickle")
    # 
    #     # print(f"max {s} symbol = {max_symbol}, max chunk size = {max_size}")
    #     return total_time / cnt
