from alphagen.data.expression import *
from alphagen.data.tokens import *
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
            n_args: int = token.operator.n_args()
            children = []
            for _ in range(n_args):
                children.append(self.stack.pop())
            self.stack.append(token.operator(*reversed(children)))  # type: ignore
        elif isinstance(token, ConstantToken):
            self.stack.append(Constant(token.constant))
        elif isinstance(token, DeltaTimeToken):
            self.stack.append(DeltaTime(token.delta_time))
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
        if self.stack[0].is_filtered:  # 四维
            return False
        expr = str(self.stack[0])
        split_str = re.split(r'[(),$]', expr)
        if len(split_str) == 2:
            return False
        return True

    def validate(self, token: Token) -> bool:
        if isinstance(token, OperatorToken):
            return self.validate_op(token.operator)
        elif isinstance(token, DeltaTimeToken):
            return self.validate_dt()
        elif isinstance(token, ConstantToken):
            return self.validate_const()
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
            if not (self.stack[-1].is_featured and self.stack[-2].is_featured):
                return False
            if (isinstance(self.stack[-1], DeltaTime) or
                    isinstance(self.stack[-2], DeltaTime)):
                return False
            if self.stack[-1].is_filtered and self.stack[-2].is_filtered:
                if self.stack[-1].filter_type != self.stack[-2].filter_type:
                    return False
        elif issubclass(op, RollingOperator):
            if not isinstance(self.stack[-1], DeltaTime):
                return False
            if not self.stack[-2].is_featured:
                return False
        elif issubclass(op, PairRollingOperator):
            if not isinstance(self.stack[-1], DeltaTime):
                return False
            if not self.stack[-2].is_featured or not self.stack[-3].is_featured:
                return False
            if self.stack[-2].is_filtered and self.stack[-3].is_filtered:
                if self.stack[-2].filter_type != self.stack[-3].filter_type:
                    return False
        elif issubclass(op, Filter):
            if not isinstance(self.stack[-2], DeltaTime):
                return False
            if not (self.stack[-3].is_featured or not self.stack[-3].is_filtered):
                return False
            if not isinstance(self.stack[-1], DivRule):
                return False
        elif issubclass(op, BinaryFilter):
            if not isinstance(self.stack[-2], DeltaTime):
                return False
            if not self.stack[-3].is_featured or not self.stack[-4].is_featured:
                return False
            if not isinstance(self.stack[-1], BinaryDivRule):
                return False
        else:
            assert False
        return True

    def validate_dt(self) -> bool:
        return len(self.stack) > 0 and self.stack[-1].is_featured

    def validate_const(self) -> bool:
        return len(self.stack) == 0 or self.stack[-1].is_featured

    def validate_divrule(self) -> bool:
        return len(self.stack) > 1 and self.stack[-2].is_featured and not self.stack[-2].is_filtered and isinstance(self.stack[-1], DeltaTime)

    def validate_binarydivrule(self) -> bool:
        return len(self.stack) > 2 and self.stack[-3].is_featured and self.stack[-2].is_featured and isinstance(self.stack[-1], DeltaTime)

    def validate_feature(self) -> bool:
        return not (len(self.stack) >= 1 and isinstance(self.stack[-1], DeltaTime))

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
