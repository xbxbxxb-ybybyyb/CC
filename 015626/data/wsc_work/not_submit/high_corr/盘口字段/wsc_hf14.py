from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



def replace_inf(data, x=np.nan):
    '''replace inf to a predefined number for the input data
    parameters
    --------------------------------------------------
    data: dataframe, series or ndarray
        the data which contains inf
    x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    --------------------------------------------------  
    return
    --------------------------------------------------
    data: input data whose inf has been replaced
        the data whose inf is replaced
    --------------------------------------------------
    '''
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'the data structure of input is illegal'
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        data = data.replace([-np.inf, np.inf], x)
    elif isinstance(data, np.ndarray):
        data[np.isinf(data)] = x
    return data

    
class wsc_hf14(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf14, self).__init__(required_columns=['BidV0_500', 'BidV1_500', 'BidV2_500', 'weight_500'],
                                      lookback_bars=3000)

    def on_bar(self, hf_data):
        # 
        bidv0 = hf_data['BidV0_500']
        bidv1 = hf_data['BidV1_500']
        bidv2 = hf_data['BidV2_500']
        weight_500 = hf_data['weight_500']
        x = bidv0 / (bidv0+bidv1+bidv2)
        x = replace_inf(x)
        factor_raw = (x*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor