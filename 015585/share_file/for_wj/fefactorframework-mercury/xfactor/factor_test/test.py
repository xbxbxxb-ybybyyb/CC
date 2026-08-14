from loguru import logger
from xfactor.factor_test.JupiterEuropaFactorTest import StrongFactorTest as JupiterEuropaFactorTest
from xfactor.factor_test.SaturnSellFactorTest import FactorTest as SaturnSellFactorTest
from xfactor.factor_test.MimasFactorTest import pj2FactorTest as MimasFactorTest
from xfactor.factor_test.MetisFactorTest import strongFactorTest as MetisFactorTest
from xfactor.factor_test.MercuryFactorTest import FactorTest as MercuryFactorTest
import settings
import xfactor.FactorUtil as FactorUtil

func_map = {
    "jupiter": JupiterEuropaFactorTest,
    "europa": JupiterEuropaFactorTest,
    "saturn": SaturnSellFactorTest,
    "mercury": MercuryFactorTest,
    "sell": SaturnSellFactorTest,
    "mimas": MimasFactorTest,
    "metis": MetisFactorTest
}


def get_tester(strategy, kls, start_date, end_date, local_evaluator_path):
    if local_evaluator_path != "":
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "FactorTest", local_evaluator_path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)

        if strategy in settings.valid_single_strategy_names:
            if FactorUtil.check_xdb_tick_1s_full(kls):
                return foo.FactorTest(20170110, end_date, strategy_name=strategy)
            else:
                return foo.FactorTest(start_date, end_date, strategy_name=strategy)
        else:
            logger.error("Strategy name not correct! input={}".format(strategy))
            raise RuntimeError("Strategy name not correct")

    else:
        if strategy in settings.valid_single_strategy_names:
            if FactorUtil.check_xdb_tick_1s_full(kls):
                return func_map[strategy](20170110, end_date, strategy_name=strategy)
            else:
                return func_map[strategy](start_date, end_date, strategy_name=strategy)
        else:
            logger.error("Strategy name not correct! input={}".format(strategy))
            raise RuntimeError("Strategy name not correct")
