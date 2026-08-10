template_backend_params = {
    "Strategy": "MobiusCrossSectionCalculator",
    "WorkerThreadsNum": "40",
    "QueryConstantTime": "91000000",
    "SubscribeBandList":
        ["mobius_sh_market_data_udp_1", "mobius_sh_market_data_udp_2", "mobius_sh_market_data_udp_3",
         "mobius_sh_market_data_udp_4",
         "mobius_sh_market_data_udp_5", "mobius_sh_market_data_udp_6", "mobius_sz_market_data_udp_2011",
         "mobius_sz_market_data_udp_2012", "mobius_sz_market_data_udp_2013",
         "mobius_sz_market_data_udp_2014",
         "mobius_sh_stock_tick_udp", "mobius_sz_stock_tick_udp", "mobius_future_tick_udp",
         "mobius_index_tick_udp"],
    "ConstantInfoBandName": "mobius_const_info_udp",
    "AMIContextName": "mobius_cross_section_calculator_context",
    "AMIChannelName": "mobius_cross_section_calculator_channel",
    "交易日期": "",
    "交易品种": "Stock,Future,Index",
    "历史数据交易日列表": [],
    "历史数据目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData", # 实盘参数
    # "历史数据目录": "/data/user/018728/cpp_projects/csi_calculator/history_data", # 本地回测
    '当日指标值存储目录': "./",
    "期货代码列表": [],
    "沪深300标的列表": [],
    "中证500标的列表": [],
    "中证1000标的列表": [],
    "上证50标的列表": [],
    "成分股权重列表": [],
    "成分股信息": []
}

template_history_backend_params = {
    "Strategy": "MobiusCrossSectionCalculator",
    "WorkerThreadsNum": "40",
    "QueryConstantTime": "91000000",
    "SubscribeBandList":
        ["mobius_sh_market_data_udp_1", "mobius_sh_market_data_udp_2", "mobius_sh_market_data_udp_3",
         "mobius_sh_market_data_udp_4",
         "mobius_sh_market_data_udp_5", "mobius_sh_market_data_udp_6", "mobius_sz_market_data_udp_2011",
         "mobius_sz_market_data_udp_2012", "mobius_sz_market_data_udp_2013",
         "mobius_sz_market_data_udp_2014",
         "mobius_sh_stock_tick_udp", "mobius_sz_stock_tick_udp", "mobius_future_tick_udp",
         "mobius_index_tick_udp"],
    "ConstantInfoBandName": "mobius_const_info_udp",
    "AMIContextName": "mobius_cross_section_calculator_context",
    "AMIChannelName": "mobius_cross_section_calculator_channel",
    "交易日期": "",
    "交易品种": "Stock,Future,Index",
    "历史数据交易日列表": [],
    # "历史数据目录": "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData",
    "历史数据目录": "/data/user/018728/cpp_projects/csi_calculator/history_data",
    # '当日指标值存储目录': "/data/user/018728/cpp_projects/csi_calculator/output",
    '当日指标值存储目录': "./uniform_indicators",
    "期货代码列表": [],
    "沪深300标的列表": [],
    "中证500标的列表": [],
    "中证1000标的列表": [],
    "上证50标的列表": [],
    "成分股权重列表": [],
    "成分股信息": []
}

template_frontend_params = {
    "path": ""
}

config_tpl = {
    "replay": False,
    "date": "",
    "servers": [
        {
            "zoneid": "localhost",
            "mobius_udp_cpp": True,
        }
    ]
}
