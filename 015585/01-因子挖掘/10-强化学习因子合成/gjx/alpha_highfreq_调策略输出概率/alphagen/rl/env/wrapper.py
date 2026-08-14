from typing import Tuple
import gymnasium as gym
import numpy as np

from alphagen.config import *
from alphagen.data.tokens import *
from alphagen.models.alpha_pool import AlphaPoolBase, AlphaPool
from alphagen.rl.env.core import AlphaEnvCore

SIZE_NULL = 1
SIZE_OP = len(OPERATORS)
SIZE_FEATURE = len(FeatureType)
SIZE_DELTA_TIME = len(DELTA_TIMES)
SIZE_CONSTANT = len(CONSTANTS)
SIZE_GET_CONSTANTS = len(GET_CONSTANTS)
SIZE_DIV_RULE = len(DIV_RULE)
SIZE_BINARY_DIV_RULE = len(BINARY_DIV_RULE)
SIZE_SEP = 1

SIZE_ALL = SIZE_NULL + SIZE_OP + SIZE_FEATURE + SIZE_DELTA_TIME + SIZE_CONSTANT + SIZE_GET_CONSTANTS +SIZE_SEP+ SIZE_DIV_RULE + SIZE_BINARY_DIV_RULE
SIZE_ACTION = SIZE_ALL - SIZE_NULL

OFFSET_OP = SIZE_NULL
OFFSET_FEATURE = OFFSET_OP + SIZE_OP
OFFSET_DELTA_TIME = OFFSET_FEATURE + SIZE_FEATURE
OFFSET_CONSTANT = OFFSET_DELTA_TIME + SIZE_DELTA_TIME
OFFSET_GET_CONSTANTS = OFFSET_CONSTANT + SIZE_CONSTANT
OFFSET_DIV_RULE = OFFSET_GET_CONSTANTS + SIZE_GET_CONSTANTS
OFFSET_BINARY_DIV_RULE= OFFSET_DIV_RULE + SIZE_DIV_RULE
OFFSET_SEP = OFFSET_BINARY_DIV_RULE + SIZE_BINARY_DIV_RULE

# 需要考虑输入的单位是否一致的算子所在的位置：
Add_IDX = OPERATORS.index(Add) + OFFSET_OP
Sub_IDX = OPERATORS.index(Sub) + OFFSET_OP
Greater_IDX = OPERATORS.index(Greater) + OFFSET_OP
Less_IDX = OPERATORS.index(Less) + OFFSET_OP
ads_IDX = OPERATORS.index(AddDivSub) + OFFSET_OP

def action2token(action_raw: int) -> Token:
    action = action_raw + 1
    if action < OFFSET_OP:
        raise ValueError
    elif action < OFFSET_FEATURE:
        return OperatorToken(OPERATORS[action - OFFSET_OP])
    elif action < OFFSET_DELTA_TIME:
        return FeatureToken(FeatureType(action - OFFSET_FEATURE))
    elif action < OFFSET_CONSTANT:
        return DeltaTimeToken(DELTA_TIMES[action - OFFSET_DELTA_TIME])
    elif action < OFFSET_GET_CONSTANTS:
        return ConstantToken(CONSTANTS[action - OFFSET_CONSTANT])
    elif action < OFFSET_DIV_RULE:
        return GetConstantToken(GET_CONSTANTS[action - OFFSET_GET_CONSTANTS])
    elif action < OFFSET_BINARY_DIV_RULE:
        return DivRuleToken(DIV_RULE[action - OFFSET_DIV_RULE])
    elif action < OFFSET_SEP:
        return BinaryDivRuleToken(BINARY_DIV_RULE[action - OFFSET_BINARY_DIV_RULE])
    elif action == OFFSET_SEP:
        return SequenceIndicatorToken(SequenceIndicatorType.SEP)
    else:
        assert False


class AlphaEnvWrapper(gym.Wrapper):
    state: np.ndarray
    env: AlphaEnvCore
    action_space: gym.spaces.Discrete
    observation_space: gym.spaces.Box
    counter: int

    def __init__(self, env: AlphaEnvCore):
        super().__init__(env)
        self.action_space = gym.spaces.Discrete(SIZE_ACTION)
        self.observation_space = gym.spaces.Box(low=0, high=SIZE_ALL - 1, shape=(MAX_EXPR_LENGTH, ), dtype=np.uint8)

    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]:
        self.counter = 0
        self.state = np.zeros(MAX_EXPR_LENGTH, dtype=np.uint8)
        self.env.reset()
        return self.state, {}

    def step(self, action: int):
        _, reward, done, truncated, info = self.env.step(self.action(action))
        if not done:
            self.state[self.counter] = action
            self.last_action = action
            self.counter += 1
        else:
            self.last_action = -1 # 以免下面做判断的时候被前一个表达式的所影响
        return self.state, self.reward(reward), done, truncated, info

    def action(self, action: int) -> Token:
        return action2token(action)

    def reward(self, reward: float) -> float:
        return reward + REWARD_PER_STEP

    def action_masks(self) -> np.ndarray:
        res = np.zeros(SIZE_ACTION, dtype=bool)
        valid = self.env.valid_action_types()
        for i in range(OFFSET_OP, OFFSET_OP + SIZE_OP):
             if valid['op'][OPERATORS[i - OFFSET_OP].category_type()]:  # operator各个类的逻辑不一样，所以要分开判断是否可行
                res[i - 1] = True
                if i-1 == self.last_action and OPERATORS[i - OFFSET_OP].category_type() is UnaryOperator :
                    res[i - 1] = False  # 不允许连续重复的一员截面算子
        if valid['select'][1]:  # FEATURE
            for i in range(OFFSET_FEATURE, OFFSET_FEATURE + SIZE_FEATURE):
                res[i - 1] = True
        if valid['select'][2]:  # CONSTANT
            for i in range(OFFSET_CONSTANT, OFFSET_CONSTANT + SIZE_CONSTANT):
                res[i - 1] = True
        if valid['select'][3]:  # DELTA_TIME
            for i in range(OFFSET_DELTA_TIME, OFFSET_DELTA_TIME + SIZE_DELTA_TIME):
                res[i - 1] = True
        if valid['select'][4]:  # GET_CONSTANT
            for i in range(OFFSET_GET_CONSTANTS, OFFSET_GET_CONSTANTS + SIZE_GET_CONSTANTS):
                res[i - 1] = True
        if valid['select'][5]:  # DIV_RULE
            for i in range(OFFSET_DIV_RULE, OFFSET_DIV_RULE + SIZE_DIV_RULE):
                res[i - 1] = True
        if valid['select'][6]:  # BINARY_DIV_RULE
            for i in range(OFFSET_BINARY_DIV_RULE, OFFSET_BINARY_DIV_RULE+ SIZE_BINARY_DIV_RULE):
                res[i - 1] = True
        if valid['select'][7]:  # SEP
            res[OFFSET_SEP - 1] = True
        if valid['units'] == False:
            res[Add_IDX - 1] = False
            res[Sub_IDX - 1] = False
            res[Greater_IDX - 1] = False
            res[Less_IDX - 1] = False
            res[ads_IDX - 1] = False
        return res


def AlphaEnv(pool: AlphaPoolBase, **kwargs):
    return AlphaEnvWrapper(AlphaEnvCore(pool=pool, **kwargs))
