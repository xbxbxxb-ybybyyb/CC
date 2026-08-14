import numpy as np
import pandas as pd

factor_name = 'qyh_heat_20240403_1'
def factor_qyh_heat_20240403_1(df_ori):
    thedata = thedata.fillna(0)
    thedata["institution"] = thedata["institution"].astype(float)
    thedata["individual"] = thedata["individual"].astype(float)
    thedata["period_id"] = thedata["period_id"].astype(int)

    institution = thedata.pivot_table(index='period_id', columns='source_security_code', values='institution',
                                      aggfunc='sum')
    individual = thedata.pivot_table(index='period_id', columns='source_security_code', values='individual',
                                     aggfunc='sum')
    institution.index.name = None
    institution.columns.name = None
    individual.index.name = None
    individual.columns.name = None
    #####################################################
    indi_delta = individual / (individual.shift(1)[individual.shift(1) > 100]) - 1
    indi_idvd_x = indi_delta.rolling(22).mean() / indi_delta.rolling(22).std() * -1

    inst_delta = institution - institution.shift(1)
    inst_delta = inst_delta.T.div(institution.quantile(0.99, axis=1)).T
    indi_inst_x = go_deca_linear_ma(inst_delta, 22)

    factor_x = utils.zscore(indi_idvd_x) + utils.zscore(indi_inst_x)
    return factor_x