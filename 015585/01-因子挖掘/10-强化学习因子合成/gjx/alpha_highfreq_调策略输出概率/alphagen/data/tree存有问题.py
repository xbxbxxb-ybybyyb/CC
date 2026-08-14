from alphagen.data.expression import *
from alphagen.data.tokens import *


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
        elif isinstance(token, FeatureToken):
            self.stack.append(Feature(token.feature))
        elif isinstance(token, GetConstantToken):
            self.stack.append(GetConstant(token.get_constant))
        else:
            assert False

    def is_valid(self) -> bool:
        return len(self.stack) == 1 and self.stack[0].is_featured and not self.stack[0].is_timeserie

    def validate(self, token: Token) -> bool:
        if isinstance(token, OperatorToken):
            return self.validate_op(token.operator)
        elif isinstance(token, DeltaTimeToken):
            return self.validate_dt()
        elif isinstance(token, ConstantToken):
            return self.validate_const()
        elif isinstance(token, GetConstantToken):
            return self.validate_getconst()
        elif isinstance(token, FeatureToken):
            return self.validate_feature()
        else:
            assert False

    def validate_op(self, op: Type[Operator]) -> bool:
        if len(self.stack) < op.n_args():
            return False

        if issubclass(op, UnaryOperator):
            if not self.stack[-1].is_featured:
                return False
        elif issubclass(op, BinaryOperator):
            if not self.stack[-1].is_featured and not self.stack[-2].is_featured:  # 只要有一个就行，就是不能全是常数不然没有意义
                return False
            if self.stack[-1].is_timeserie != self.stack[-2].is_timeserie:
                return False
            if (isinstance(self.stack[-1], DeltaTime) or
                    isinstance(self.stack[-2], DeltaTime)):
                return False
        elif issubclass(op, RollingOperator):
            if not isinstance(self.stack[-1], DeltaTime):
                return False
            if not self.stack[-2].is_featured:
                return False
            if not self.stack[-2].is_timeserie:
                return False
        elif issubclass(op, PairRollingOperator):
            if not isinstance(self.stack[-1], DeltaTime):
                return False
            if not self.stack[-2].is_featured or not self.stack[-3].is_featured:
                return False
            if not self.stack[-2].is_timeserie or not self.stack[-3].is_timeserie:
                return False
        elif issubclass(op, GetOperator):
            if not isinstance(self.stack[-1], GetConstant):
                return False
            if not self.stack[-2].is_featured or not self.stack[-2].is_timeserie:
                return False
        else:
            assert False
        return True

    def validate_dt(self) -> bool:
        return len(self.stack) > 0 and self.stack[-1].is_featured and self.stack[-1].is_timeserie

    def validate_const(self) -> bool:
        if len(self.stack) == 0:
            return True
        elif len(self.stack) == 1 and self.stack[-1].is_featured and self.stack[-1].is_timeserie:
            return True
        else:
            return False
        # return len(self.stack) == 0 or self.stack[-1].is_featured

    def validate_getconst(self) -> bool:  # 前面必须有且仅有一个feature
        if len(self.stack) == 1 and self.stack[-1].is_featured and self.stack[-1].is_timeserie:
            return True
        else:
            return False

    def validate_feature(self) -> bool:
        # return not (len(self.stack) >= 1 and isinstance(self.stack[-1], DeltaTime))
        if len(self.stack) == 0:
            return True
        elif len(self.stack) == 1 and self.stack[-1].is_timeserie:
            return True
        else:
            return False
    # 返回True的情形有：1）已经有一个feature且不是datla；2）还没有东西；


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
