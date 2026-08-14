

from FactorTest import FactorTest
ft = FactorTest()

program = dict(
    program_code='''
    
    pn_condition2(
        dt_max(dt_lwm(turn_trade_buy, 4), 3), 
        dt_cumsum(log(ds_cumsum(adj_high)))
        )
    
    ''',

    program_complex=False,
    program_manual=False,

    program_author='016835',
    program_class='机器挖掘',
    program_reference='无知无畏',
    program_logic='无知无畏',
    )


ft.simulate_test_factor(program)

