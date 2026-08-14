from typing import Tuple, Optional
import gymnasium as gym
import math

from alphagen.config import MAX_EXPR_LENGTH
from alphagen.data.tokens import *
from alphagen.data.expression import *
from alphagen.data.tree import ExpressionBuilder
from alphagen.models.alpha_pool import AlphaPoolBase, AlphaPool
from alphagen.utils import reseed_everything
from alphagen_qlib.utils import load_alpha_pool_by_path, load_recent_data
import re
from collections import Counter

# 统计池子里的因子的各个action出现的概率
def counter_action():
    POOL_PATH = "/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/path/for/checkpoints/new_100_2_20240812104326/36864_steps_pool.json"
    exprs = load_alpha_pool_by_path(POOL_PATH)  # 一个list
    # 按照 $() 进行划分并丢掉这些分隔符
    split_strings = [re.split(r'[\(,\)]', str(s)) for s in exprs]

    # 将划分后的字符串部分合并成一个列表
    cleaned_strings = [part for parts in split_strings for part in parts if part]
    # 统计每个字符串出现的次数
    counter = Counter(cleaned_strings)
    del counter['Constant']
    total_sum = sum(counter.values())
    counter = {key: value/total_sum for key, value in counter.items()}
    return counter

class AlphaEnvCore(gym.Env):
    pool: AlphaPoolBase
    _tokens: List[Token]
    _builder: ExpressionBuilder
    _print_expr: bool

    def __init__(self,
                 pool: AlphaPoolBase,
                 device: torch.device = torch.device('cuda:0'),
                 print_expr: bool = False
                 ):
        super().__init__()

        self.pool = pool
        self._print_expr = print_expr
        self._device = device

        self.eval_cnt = 0
        self.num_step = 0  # 经过了多少步

        self.render_mode = None

    def reset(
        self, *,
        seed: Optional[int] = None,
        return_info: bool = False,
        options: Optional[dict] = None
    ) -> Tuple[List[Token], dict]:
        reseed_everything(seed)
        self._tokens = [BEG_TOKEN]
        self._builder = ExpressionBuilder()
        return self._tokens, self._valid_action_types()

    def step(self, action: Token) -> Tuple[List[Token], float, bool, bool, dict]:
        self.num_step += 1
        # counter = counter_action()
        if (isinstance(action, SequenceIndicatorToken) and
                action.indicator == SequenceIndicatorType.SEP):
            reward = self._evaluate()
            done = True
        elif len(self._tokens) < MAX_EXPR_LENGTH:
            self._tokens.append(action)
            self._builder.add_token(action)
            done = False
            reward = 0.0
        else:
            done = True
            reward = self._evaluate() if self._builder.is_valid() else -0.5

        if math.isnan(reward):
            reward = 0.

        truncated = False  # Fk gymnasium
        return self._tokens, reward, done, truncated, self._valid_action_types()

    def _evaluate(self):
        expr: Expression = self._builder.get_tree()
        if self._print_expr:
            print(expr)  # 是先输出所以有可能输出的一堆都没法加入池子里
            # 这个是输出的是expression里面每个类定义的__str__,因为这个实际上栈里面只剩一个元素，是一个类嵌套类再嵌套下去，
            # 所以print实际上返回的就是class里面定义的__str__函数返回的内容，然后一层层进入进去，就得到了一个完整的表达式，计算也是如此，也是一层层展开进去
        try:
            ret = self.pool.try_new_expr(expr, self.num_step)
            self.eval_cnt += 1
            return ret
        except OutOfDataRangeError:
            return 0.

    def _valid_action_types(self) -> dict:
        valid_op_unary = self._builder.validate_op(UnaryOperator)
        valid_op_binary = self._builder.validate_op(BinaryOperator)
        valid_op_rolling = self._builder.validate_op(RollingOperator)
        valid_op_pair_rolling = self._builder.validate_op(PairRollingOperator)
        valid_op_get = self._builder.validate_op(GetOperator)
        valid_op_filter = self._builder.validate_op(Filter)
        valid_op_binaryfilter = self._builder.validate_op(BinaryFilter)
        valid_op_diff = self._builder.validate_op(DiffOperator)

        valid_op = valid_op_unary or valid_op_binary or valid_op_rolling or valid_op_pair_rolling or valid_op_get
        valid_dt = self._builder.validate_dt()
        valid_const = self._builder.validate_const()
        valid_getconst = self._builder.validate_getconst()
        valid_feature = self._builder.validate_feature()
        valid_divrule = self._builder.validate_divrule()
        valid_binarydivrule = self._builder.validate_binarydivrule()
        valid_stop = self._builder.is_valid()

        valid_units = self._builder.validate_units()
        ret = {
            'select': [valid_op, valid_feature, valid_const, valid_dt, valid_getconst, valid_divrule, valid_binarydivrule, valid_stop],
            'op': {
                UnaryOperator: valid_op_unary,
                BinaryOperator: valid_op_binary,
                RollingOperator: valid_op_rolling,
                PairRollingOperator: valid_op_pair_rolling,
                GetOperator: valid_op_get,
                Filter: valid_op_filter,
                BinaryFilter: valid_op_binaryfilter,
                DiffOperator: valid_op_diff
            },
            'units': valid_units
        }
        return ret

    def valid_action_types(self) -> dict:
        return self._valid_action_types()

    def render(self, mode='human'):
        pass
