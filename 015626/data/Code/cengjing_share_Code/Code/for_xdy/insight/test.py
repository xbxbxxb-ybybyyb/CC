# from xquant.thirdpartydata.insightlib import InsightSample
#
#
# insight = InsightSample(user_id = '013150')
# #回放行情数据
# insight.play_back_oneday(stock_list = ["000905.SH"], start_time = "20201124000000", stop_time="20201124235959")#回放历史行情数据
from insight.model import ESecurityType_pb2 as ESecurityType
from xquant.thirdpartydata.insightlib import InsightSample

insight = InsightSample(user_id = '013150') #订阅实时行情数据*

insight.subscribe_by_type(security_type =ESecurityType.IndexType)