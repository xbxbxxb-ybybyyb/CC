from alphagen.data.expression import *

# 汇总动作空间和状态空间内容的设定

MAX_EXPR_LENGTH = 20
MAX_EPISODE_LENGTH = 256

OPERATORS = [
    # Unary
    Abs, Log, PercentileRank,   # Sign,
    # Binary
    Add, Sub, Mul, Div, Greater, Less,Euc_Dis,
    # Rolling
    Mean, Sum, Std, Skew, Kurt, Rank, GainFromMin, DropFromMax, Rel_UpandDown, # Skew, Kurt,
    Max, Min,
    # Med, Mad,  # Rank,
    WMA, EMA, ZScore, # 待会别不小心把这个丢掉了
    # Pair rolling
    Corr, # Cov,
    Filter, Filter, Filter, Filter, Filter,Filter, Filter, Filter, Filter, Filter,
    BinaryFilter, BinaryFilter,
    # 获取某个截面
    Get,  # 分别获取的是开盘，开盘一分钟，开盘5分钟，开盘9分钟，开盘10分钟时的数据，改间隔的话这几个函数里面的参数都要改，因为索引变了
    Diff1, Diff5
]

DELTA_TIMES = [] # 全都是闭区间,是71不是72是因为开盘时刻和后面不太一样，特别是算量、额、笔数的时候都没法平均
GET_CONSTANTS = ['93000','93100','93500','93900','93957']
# CONSTANTS = [-30., -10., -5., -2., -1., -0.5, -0.01, 0.01, 0.5, 1., 2., 5., 10., 30.]
CONSTANTS = []
# 复制是想增加频率
DIV_RULE = ['[93000,93100]','[93900,93957]','[93000,93500]','[93500,93957]', '[93000,93100]','[93900,93957]','[93000,93500]','[93500,93957]','<mkt_mean', '>mkt_mean', '>ts_mean', '<ts_mean', '<const_0', '>const_0']
BINARY_DIV_RULE = ['when_y>0', 'when_y<0', 'when_y<1/4[y]', 'when_y>3/4[y]']
REWARD_PER_STEP = 0.
