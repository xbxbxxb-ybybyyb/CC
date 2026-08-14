from alphagen.data.expression import *


MAX_EXPR_LENGTH = 15
MAX_EPISODE_LENGTH = 256

OPERATORS = [
    # Unary
    Abs, Log, PercentileRank, # Sign, #Square, SquareRoot, Cube, CubeRoot, Reciprocal, Inverse, Sin, Cos, Tan, Sigmoid, Exp, IfElse1,IfElse2,IfElse3,
    # Binary
    Add, Sub, Mul, Div, Greater, Less,# Euc_Dis,# Rel_Div,Perc_Rank_Diff,Mean_Dis,Perc_Rank_Div,Perc_Diff, Rel_Strength,IfElse4,
    # Rolling
    Ref, Mean, Sum, Std, Skew, Kurt, Rank, # GainFromMin, DropFromMax, Rel_UpandDown,# Var,
    # Max, Min,
    # Med, Mad,
    Delta, WMA, EMA, ZScore, # CV, MinPos, MaxPos, Chg_Perc, Prod,
    # Pair rolling
    Corr, # Cov
    Filter,Filter,Filter,Filter,Filter,
    BinaryFilter,BinaryFilter
]

DELTA_TIMES = [10, 20, 30, 10, 20, 30]

# CONSTANTS = [-30., -10., -5., -2., -1., -0.5, -0.01, 0.01, 0.5, 1., 2., 5., 10., 30.]
# CONSTANTS = [-10., -1., -0.01, 0, 0.01, 1.,  10.]
CONSTANTS = []
DIV_RULE = ['<mkt_mean', '>mkt_mean', '>ts_mean', '<ts_mean', '<const_0', '>const_0']
BINARY_DIV_RULE = ['when_y>0', 'when_y<0', 'when_y<1/4[y]', 'when_y>3/4[y]']
REWARD_PER_STEP = 0.
