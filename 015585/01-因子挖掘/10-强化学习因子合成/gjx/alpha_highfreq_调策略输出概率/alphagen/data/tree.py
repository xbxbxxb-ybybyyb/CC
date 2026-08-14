from alphagen.data.expression import *
from alphagen.data.tokens import *
#from alphagen.utils.pytorch_utils import extract_div_rules
import re

class ExpressionBuilder:
    stack: List[Expression]

    def __init__(self):
        self.stack = []

    def get_tree(self) -> Expression:
        if len(self.stack) == 1:
            return self.stack[0]
        else:
            raise InvalidExpressionException(f"Expected only one tree, got {len(self.stack)}")

    def add_token(self, token: Token):
        if not self.validate(token):
            raise InvalidExpressionException(f"Token {token} not allowed here, stack: {self.stack}.")
        if isinstance(token, OperatorToken):
            n_args: int = token.operator.n_args()  # 需要几个参数，feature+deltatime或者是getconstant
            # 这里的token.operator本身就是类了，这些都是跟config.py里面的定义有关的，feature本身就放的类，但是常数，delta_time和get_constant都是值不是类
            children = []
            for _ in range(n_args):
                children.append(self.stack.pop())
            self.stack.append(token.operator(*reversed(children)))  # type: ignore
        elif isinstance(token, ConstantToken):
            self.stack.append(Constant(token.constant))  # token.xxx是具体的东西，然后外面套个类变成实例了
        elif isinstance(token, DeltaTimeToken):
            self.stack.append(DeltaTime(token.delta_time))
        elif isinstance(token, GetConstantToken):
            self.stack.append(GetConstant(token.get_constant))
        elif isinstance(token, BinaryDivRuleToken):
            self.stack.append(BinaryDivRule(token.binary_div_rule))
        elif isinstance(token, DivRuleToken):
            self.stack.append(DivRule(token.div_rule))
        elif isinstance(token, FeatureToken):
            self.stack.append(Feature(token.feature))
        else:
            assert False

    def is_valid(self) -> bool:
        if len(self.stack) != 1:
            return False
        if not self.stack[0].is_featured:
            return False
        if self.stack[0].is_timeserie:
            return False
        expr = str(self.stack[0])
        split_str = re.split(r'[(),$]', expr)
        if len(split_str) == 2:
            return False
        return True

    def validate(self, token: Token) -> bool:
        if isinstance(token, OperatorToken):
            return self.validate_op(token.operator)
        # elif isinstance(token, DeltaTimeToken):
        #     return self.validate_dt()s
        elif isinstance(token, ConstantToken):
            return self.validate_const()
        elif isinstance(token, GetConstantToken):
            return self.validate_getconst()
        elif isinstance(token, FeatureToken):
            return self.validate_feature()
        elif isinstance(token, DivRuleToken):
            return self.validate_divrule()
        elif isinstance(token, BinaryDivRuleToken):
            return self.validate_binarydivrule()
        else:
            assert False

    def validate_op(self, op: Type[Operator]) -> bool:
        if len(self.stack) < op.n_args():
            return False

        if issubclass(op, UnaryOperator):
            if not self.stack[-1].is_featured:
                return False
        elif issubclass(op, BinaryOperator):
            if not (self.stack[-1].is_featured and self.stack[-2].is_featured):  # 只要有一个就行，就是不能全是常数不然没有意义
                return False
            # 得加一个如果是筛选过的话，得保证筛选条件是一样的【前面日频的话得delta和条件都一样才行】
            # if self.stack[-1].is_timeserie and self.stack[-2].is_timeserie:
            # # 一层层剥开，遇到的每个filter的参数的列表必须是左右相等的
            # # 如果没有被筛选过会返回空值列表
            #     div_rule_list1 = extract_div_rule(str(self.stack[-1]))
            #     div_rule_list2 = extract_div_rule(str(self.stack[-2]))
            #     if div_rule_list1 != div_rule_list2:
            #         return False
            if self.stack[-1].filter_type != 'SHOOT' and self.stack[-2].filter_type != 'SHOOT':
                if self.stack[-1].filter_type != self.stack[-2].filter_type:
                    return False
        elif issubclass(op, RollingOperator):
            if not self.stack[-1].is_featured:
                return False
            if not self.stack[-1].is_timeserie:
                return False
        elif issubclass(op, PairRollingOperator):
            if not self.stack[-2].is_featured or not self.stack[-1].is_featured:
                return False
            if not self.stack[-2].is_timeserie or not self.stack[-1].is_timeserie:
                return False
            if self.stack[-1].filter_type != self.stack[-2].filter_type:
                return False
        elif issubclass(op, GetOperator):
            if not isinstance(self.stack[-1], GetConstant):
                return False
            if not self.stack[-2].is_featured or not self.stack[-2].is_timeserie:
                return False
        elif issubclass(op, Filter):
            if not (self.stack[-2].is_featured and self.stack[-2].is_timeserie):
                return False
            if not isinstance(self.stack[-1], DivRule):
                return False
        elif issubclass(op, BinaryFilter):
            if not (self.stack[-2].is_featured and self.stack[-2].is_timeserie) or not (self.stack[-3].is_featured and self.stack[-3].is_timeserie):
                return False
            # 得判断一下是同一个筛选指标【不然是无效搜索空间】，如果两个输入都是被筛选过的，得保证它们之前被筛选的条件是一样的
            if self.stack[-2].filter_type != self.stack[-3].filter_type:
                return False
                # div_rule_list1 = extract_div_rule(str(self.stack[-2]))
                # div_rule_list2 = extract_div_rule(str(self.stack[-3]))
                # if div_rule_list1 != div_rule_list2:
                #     return False
            if not isinstance(self.stack[-1], BinaryDivRule):
                return False
        elif issubclass(op, DiffOperator):
            if not (self.stack[-1].is_featured and self.stack[-1].is_timeserie):
                return False
        else:
            assert False
        return True

    # 这里要把len(stack)的判断放前面是因为如果长度不大于0，那就不能用[-1]索引值

    def validate_const(self) -> bool:
        return len(self.stack) == 0 or (self.stack[-1].is_featured and  self.stack[-1].is_timeserie)

    def validate_getconst(self) -> bool:  # 前面必须有且仅有一个feature
        return len(self.stack) > 0 and self.stack[-1].is_featured and self.stack[-1].is_timeserie

    def validate_dt(self) -> bool:  # 高频里没用到dalta_time
        return True

    def validate_divrule(self) -> bool:
        return len(self.stack) > 0 and self.stack[-1].is_featured and self.stack[-1].is_timeserie

    def validate_binarydivrule(self) -> bool:
        return len(self.stack) > 1 and self.stack[-1].is_featured and self.stack[-2].is_featured and self.stack[-1].is_timeserie and self.stack[-2].is_timeserie

    def validate_feature(self) -> bool:
        return len(self.stack) ==0 or (not isinstance(self.stack[-1], DivRule)) or (not isinstance(self.stack[-1], BinaryDivRule))

    def validate_units(self) -> bool:
        try:
            if self.stack[-2].feature_units != self.stack[-1].feature_units:
                return False
            else:
                return True
        except:
            return True


class InvalidExpressionException(ValueError):
    pass


if __name__ == '__main__':
    tokens = [
        FeatureToken(FeatureType.LOW),
        OperatorToken(Abs),
        DeltaTimeToken(-10),
        OperatorToken(Ref),
        FeatureToken(FeatureType.HIGH),
        FeatureToken(FeatureType.CLOSE),
        OperatorToken(Div),
        OperatorToken(Add),
    ]

    builder = ExpressionBuilder()
    for token in tokens:
        builder.add_token(token)

    print(f'res: {str(builder.get_tree())}')
    print(f'ref: Add(Ref(Abs($low),-10),Div($high,$close))')
