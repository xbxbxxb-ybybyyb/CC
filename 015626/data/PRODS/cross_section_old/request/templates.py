template_request = {
    "Strategy": "CSICalculator",
    "BackTestTimeFrame": "PERIOD_Tick_M1",
    "MarketDataSortType": "MD_TIME",
    "Match": "OPPOSITE",
    "TradeDate": "",
    "StartDate": "",
    "EndDate": "",
    "Bands": [
        {
            "Name": "mobius_sh_market_data_udp_1",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_1.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_2",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_2.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_3",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_3.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_4",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_4.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_5",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_5.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_6",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_6.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2011",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2011.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2012",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2012.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2013",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2013.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2014",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2014.gz"
        },
        {
            "Name": "mobius_sz_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/data/user/019073/marketdata/Stock/SZ/TickEx/${TRADING_DATE}/Stock_SZ_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_sh_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/data/user/019073/marketdata/Stock/SH/TickEx/${TRADING_DATE}/Stock_SH_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_future_tick_udp",
            "UniformMarketDataFutureQuoteFile": "/data/user/019073/marketdata/Future/SFE/TickEx/${TRADING_DATE}/Future_SFE_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_index_tick_udp",
            "UniformMarketDataIndexQuoteFile": "/data/user/019073/marketdata/Index/SH/TickEx/${TRADING_DATE}/Index_SH_TickEx_${TRADING_DATE}"
        }
    ]
}


template_request_v2 = {
    "Strategy": "CSICalculator",
    "BackTestTimeFrame": "PERIOD_Tick_M1",
    "MarketDataSortType": "MD_TIME",
    "Match": "OPPOSITE",
    "TradeDate": "",
    "StartDate": "",
    "EndDate": "",
    "Bands": [
        {
            "Name": "mobius_sh_market_data_udp_1",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_1.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_2",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_2.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_3",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_3.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_4",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_4.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_5",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_5.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_6",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sh_market_data_${DATA_SOURCE}_6.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2011",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2011.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2012",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2012.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2013",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2013.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2014",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2014.gz"
        },
        {
            "Name": "mobius_sz_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/00_SZ/00_TickEx/${TRADING_DATE}/Stock_SZ_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_sh_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/01_SH/00_TickEx//${TRADING_DATE}/Stock_SH_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_future_tick_udp",
            "UniformMarketDataFutureQuoteFile": "/dfs/group/900001/XDB/00_MarketData/02_FutureData/02_UHFData/03_CCFX/00_TickEx/${TRADING_DATE}/Future_SFE_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_index_tick_udp",
            "UniformMarketDataIndexQuoteFile": "/dfs/group/900001/XDB/00_MarketData/03_IndexData/02_UHFData/01_SH/00_TickEx/${TRADING_DATE}/Index_SH_TickEx_${TRADING_DATE}"
        }
    ]
}


# 上交所逐笔合并后新的数据源
template_request_v3 = {
    "Strategy": "CSICalculator",
    "BackTestTimeFrame": "PERIOD_Tick_M1",
    "MarketDataSortType": "MD_TIME",
    "Match": "OPPOSITE",
    "TradeDate": "",
    "StartDate": "",
    "EndDate": "",
    "Bands": [
        {
            "Name": "mobius_sh_market_data_udp_1",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_1.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_2",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_2.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_3",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_3.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_4",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_4.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_5",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_5.gz"
        },
        {
            "Name": "mobius_sh_market_data_udp_6",
            "RawMarketChannelFile": "/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/${TRADING_DATE}/sh_market_data_${SH_DATA_SOURCE}_6.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2011",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2011.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2012",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2012.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2013",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2013.gz"
        },
        {
            "Name": "mobius_sz_market_data_udp_2014",
            "RawMarketChannelFile": "/data/group/800445/Insight/shm/${TRADING_DATE}/sz_market_data_${DATA_SOURCE}_2014.gz"
        },
        {
            "Name": "mobius_sz_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/00_SZ/00_TickEx/${TRADING_DATE}/Stock_SZ_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_sh_stock_tick_udp",
            "UniformMarketDataQuoteFile": "/dfs/group/900001/XDB/00_MarketData/00_StockData/02_UHFData/01_SH/00_TickEx//${TRADING_DATE}/Stock_SH_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_future_tick_udp",
            "UniformMarketDataFutureQuoteFile": "/dfs/group/900001/XDB/00_MarketData/02_FutureData/02_UHFData/03_CCFX/00_TickEx/${TRADING_DATE}/Future_SFE_TickEx_${TRADING_DATE}"
        },
        {
            "Name": "mobius_index_tick_udp",
            "UniformMarketDataIndexQuoteFile": "/dfs/group/900001/XDB/00_MarketData/03_IndexData/02_UHFData/01_SH/00_TickEx/${TRADING_DATE}/Index_SH_TickEx_${TRADING_DATE}"
        }
    ]
}
