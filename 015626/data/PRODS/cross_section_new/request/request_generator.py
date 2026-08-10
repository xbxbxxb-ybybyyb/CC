import json
from common.tools import *
from request.templates import *

class RequestGenerator:

    def __init__(self):
        self.thread_num = "40"
        self.request_template = template_request
        self.request_template_v2 = template_request_v2

    def generate(self, date, version='v2'):
        if date >= "20281216":
            if version == 'v2':
                request = self.request_template_v2.copy()
            elif version == 'v3':
                request = template_request_v3.copy()
        else:
            if version == 'v3':
                request = template_request_v3.copy()
            else:
                request = self.request_template.copy()
        fdate = format_date(date)
        request['StartDate'] = fdate
        request['EndDate'] = fdate
        request['TradeDate'] = str(date)
        content = json.dumps(request, indent=4, ensure_ascii=False)
        content = content.replace('${TRADING_DATE}', date)
        if version == 'v2':
            source = 'udp'
            filepath = os.path.join('/data/group/800445/Insight/shm/', date, 'sh_market_data_udp_1.gz')
            if not os.path.exists(filepath):
                source = 'parquet'
            content = content.replace('${DATA_SOURCE}', source)
        elif version == 'v3':
            source = 'udp'
            filepath = os.path.join('/data/group/800445/Insight/shm/', date, 'sz_market_data_udp_2011.gz')
            if not os.path.exists(filepath):
                source = 'parquet'
            sh_source = 'fast'
            sh_filepath = os.path.join('/dfs/group/800445/xdb_test/00_MarketData/00_StockData/01_RHFData/01_SH_merge/00_HFData/', date, 'sh_market_data_fast_1.gz')
            if not os.path.exists(sh_filepath):
                sh_source = 'udp'
            content = content.replace('${DATA_SOURCE}', source)
            content = content.replace('${SH_DATA_SOURCE}', sh_source)
        return content

