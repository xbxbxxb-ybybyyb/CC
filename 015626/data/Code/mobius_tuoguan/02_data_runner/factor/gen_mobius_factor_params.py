import datetime
import json
import os
import sys

# 获取当前日期
current_date = sys.argv[1]

# 计算路径列表
compute_paths = [sys.argv[2]]

# 父目录路径（根据交易日期生成）
parent_dir = f"/dfs/user/666466/01_params/{current_date}"

# 遍历计算路径列表，生成每个路径对应的文件
for compute_path in compute_paths:
    # 构建完整路径（包含 offset 文件夹）
    offset_folder = f"offset_{compute_path}"
    full_path = os.path.join(parent_dir, offset_folder,'factor')

    # 确保目标目录存在，如果不存在则创建
    os.makedirs(full_path, exist_ok=True)

    # 生成 config.json 文件
    config = {
        "交易日期": current_date,
        "历史数据目录": "/dfs/user/666466/03_mobius/02_FactorData",
        "日频数据目录": "/dfs/group/900001/XDB/00_MarketData",
        "因子配置文件": "/dfs/user/666466/01_params/factor_definition_set_V7.0.1.json",
        "是否记录因子值": "True",
        "静态信息查询失败时是否使用本地文件": "True",
        "是否校验历史数据": "False",
        "开始处理分钟聚合数据时间": "09:30:00",
        "计算路径": compute_path
    }

    # 生成 config.json 文件路径
    config_filename = f"params.json"
    config_file_path = os.path.join(full_path, config_filename)

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print(f"文件已生成: {config_file_path}")

    # 生成 request.json 文件
    request_config = {
        "Strategy": "MobiusFactorStrategy",
        "MarketDataTunnel": "HISTORY",
        "StartDate": "2025-02-25",
        "EndDate": "2025-02-25",
        "BackTestTimeFrame": "PERIOD_Tick",
        "MarketDataSortType": "RECEIVE_TIME",
        "ReportTimeFrame": "PERIOD_Tick",
        "Match": "OPPOSITE",
        "RuleJsonFile": "",
        "StrategyType": "NONE",
        "BenchMarks": [],
        "BaseCash": 500000000,
        "Commission": 0.3,
        "StampDuty": 1,
        "Environment": "SIM",
        "IndicatorFile": "",
        "Universe": [],
        "future_position": [{
                "Symbol": "IM2503.CF",
                "long_position": 188,
                "short_position": 188,
                "BuySecAcc": "x",
                "SellSecAcc": "x",
                "BuyTradeAcc": "x",
                "SellTradeAcc": "x",
                "PortfolioNo": "x",
                "PortfolioType": "x",
                "margin_ratio": "0.06",
                "contract_multiple": 200
       }],
        "SpecHistoryMDService": "com.huatai.strategy.MobiusFactor.localTest.LocalXDBDataSourceService",
        "SpecHisotryMDServiceParam": {
            "tradeDate": current_date,
            "replayPath": "/dfs/user/666466/03_mobius/02_FactorData",
            "offset": compute_path
        }
    }

    # 生成 request.json 文件路径
    request_filename = "request.json"
    request_file_path = os.path.join(full_path, request_filename)

    with open(request_file_path, 'w') as f:
        json.dump(request_config, f, indent=4)

    print(f"文件已生成: {request_file_path}")

print("所有文件生成完成！")
