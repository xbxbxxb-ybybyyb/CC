template_backend_params = {
    "Strategy": "MobiusCrossSectionCalculator",
    "WorkerThreadsNum": "40",
    "QueryConstantTime": "91000000",
    "ConstantInfoBandName": "mobius_const_info_udp",
    "AMIContextName": "mobius_cross_section_calculator_context",
    "AMIChannelName": "mobius_cross_section_calculator_channel",
    "交易日期": "",
    "交易品种": "Stock,Future,Index",
    # "历史数据交易日列表": [],
    # "MinuteShiftSec": 0,
    "指数数据目录": "/data/user/666466/06_prod_data/00_MarketData/03_IndexData/10_IndexWeight",
    "股票日频数据目录": "/data/user/666466/06_prod_data/00_MarketData/00_StockData/02_UHFData",
    "股票股本数据目录": "/data/user/666466/06_prod_data/00_MarketData/00_StockData/03_FinancialData/00_WindData/00_AShareCapitalization",
    "期货合约数据目录": "/data/user/666466/06_prod_data/00_MarketData/02_FutureData/02_UHFData/03_CCFX/10_ContractInfo",
    "历史数据目录": "/data/user/666466/06_prod_data/02_FactorData",
    "当日指标值存储目录": ".",
    # "期货代码列表": []
}

template_history_backend_params = {
    "Strategy": "MobiusCrossSectionCalculator",
    "WorkerThreadsNum": "40",
    "QueryConstantTime": "91000000",
    "ConstantInfoBandName": "mobius_const_info_udp",
    "AMIContextName": "mobius_cross_section_calculator_context",
    "AMIChannelName": "mobius_cross_section_calculator_channel",
    "交易日期": "",
    "交易品种": "Stock,Future,Index",
    # "历史数据交易日列表": [],
    # "MinuteShiftSec": 0,
    "指数数据目录": "/dfs/group/900001/XDB/00_MarketData/03_IndexData/10_IndexWeight",
    "股票日频数据目录": "/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData",
    "股票股本数据目录": "/dfs/group/900001/XDB/00_MarketData/00_StockData/03_FinancialData/00_WindData/00_AShareCapitalization",
    "期货合约数据目录": "/dfs/group/900001/XDB/00_MarketData/02_FutureData/02_UHFData/03_CCFX/10_ContractInfo",
    "历史数据目录": "/dfs/user/019906/03_mobius/02_FactorData_from_h5",
    "当日指标值存储目录": "/dfs/user/019906/03_mobius/02_FactorData",
    # "期货代码列表": []
}

template_frontend_params = {
    "path": ""
}

config_tpl = {
    "replay": False,
    # "date": "",
    "servers": [
        {
            "zoneid": "localhost",
            "mobius_udp_cpp": True,
        }
    ]
}
