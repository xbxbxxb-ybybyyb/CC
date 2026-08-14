from ApplicationNonFixCondition import Application


def init_Calculator(date, send_strategy_log=None):
    return Application(date, log=send_strategy_log)
