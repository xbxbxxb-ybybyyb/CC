from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf7(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf7, self).__init__(required_columns=['BidP0_500', 'BidP1_500', 'BidP2_500', 'BidP3_500', 'BidP4_500', 'BidV0_500', 'BidV1_500', 'BidV2_500', 'BidV3_500', 'BidV4_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # 计算五档盘口的算术平均价格和挂单数量加权平均价格的比值
        bidp0 = data['BidP0_500']
        bidp1 = data['BidP1_500']
        bidp2 = data['BidP2_500']
        bidp3 = data['BidP3_500']
        bidp4 = data['BidP4_500']
        bidv0 = data['BidV0_500']
        bidv1 = data['BidV1_500']
        bidv2 = data['BidV2_500']
        bidv3 = data['BidV3_500']
        bidv4 = data['BidV4_500']
        bida0 = data['BidP0_500'] * data['BidV0_500']
        bida1 = data['BidP1_500'] * data['BidV1_500']
        bida2 = data['BidP2_500'] * data['BidV2_500']
        bida3 = data['BidP3_500'] * data['BidV3_500']
        bida4 = data['BidP4_500'] * data['BidV4_500']
        weight_500 = data['weight_500']
        price1 = ((bidp0+bidp1+bidp2+bidp3+bidp4)/5*weight_500).sum(axis=1)
        price2 = ((bida0+bida1+bida2+bida3+bida4)/(bidv0+bidv1+bidv2+bidv3+bidv4)*weight_500).sum(axis=1)
        price2[abs(price2)<1e-8] = np.nan
        factor_raw = price1 / price2
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        factor[factor>=0] = 0
        return factor