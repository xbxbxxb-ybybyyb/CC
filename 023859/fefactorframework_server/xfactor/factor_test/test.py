from loguru import logger
from xfactor.factor_test.JupiterEuropaFactorTest import StrongFactorTest as JupiterEuropaFactorTest
from xfactor.factor_test.SaturnSellFactorTest import FactorTest as SaturnSellFactorTest
from xfactor.factor_test.MimasFactorTest import pj2FactorTest as MimasFactorTest
from xfactor.factor_test.MetisFactorTest import strongFactorTest as MetisFactorTest
from xfactor.factor_test.MercuryFactorTest import FactorTest as MercuryFactorTest
from xfactor.factor_test.NeptuneFactorTest import FactorTest as NeptuneFactorTest
from xfactor.factor_test.NeptunelongFactorTest import FactorTest as NeptunelongFactorTest
import settings
import xfactor.FactorUtil as FactorUtil

func_map = {
    "jupiter": JupiterEuropaFactorTest,
    "europa": JupiterEuropaFactorTest,
    "saturn": SaturnSellFactorTest,
    "mercury": MercuryFactorTest,
    "sell": SaturnSellFactorTest,
    "mimas": MimasFactorTest,
    "metis": MetisFactorTest,
    "neptune": NeptuneFactorTest,
    "neptunelong": NeptunelongFactorTest,
}


def get_tester(strategy, kls, start_date, end_date, local_evaluator_path):
    if local_evaluator_path != "":
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "FactorTest", local_evaluator_path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)

        if strategy in settings.valid_strategy_names:
            start_date_new = int(start_date)
            if (FactorUtil.check_tday_tick1s_full(kls)) and (start_date_new < 20170101):
                start_date_new = 20170101
            if (FactorUtil.check_xdb_tick_1s_full(kls)) and (start_date_new < 20170110):
                start_date_new = 20170110
            return foo.FactorTest(start_date_new, int(end_date), strategy_name=strategy)

        else:
            logger.error("Strategy name not correct! input={}".format(strategy))
            raise RuntimeError("Strategy name not correct")

    else:
        if strategy in settings.valid_strategy_names:
            start_date_new = int(start_date)
            if (FactorUtil.check_tday_tick1s_full(kls)) and (start_date_new < 20170101):
                start_date_new = 20170101
            if (FactorUtil.check_xdb_tick_1s_full(kls)) and (start_date_new < 20170110):
                start_date_new = 20170110
            return func_map[strategy](start_date_new, int(end_date), strategy_name=strategy)
        else:
            logger.error("Strategy name not correct! input={}".format(strategy))
            raise RuntimeError("Strategy name not correct")
