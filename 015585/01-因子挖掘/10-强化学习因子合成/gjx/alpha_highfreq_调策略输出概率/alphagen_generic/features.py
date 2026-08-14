from alphagen.data.expression import Feature
from alphagen_qlib.stock_data import FeatureType, TargetType


numtrades = Feature(FeatureType.NumTrades)
totalvolumetrade = Feature(FeatureType.TotalVolumeTrade)
totalvaluetrade = Feature(FeatureType.TotalValueTrade)
lastpx = Feature(FeatureType.LastPx)
highpx = Feature(FeatureType.HighPx)
lowpx = Feature(FeatureType.LowPx)
totalbidqty = Feature(FeatureType.TotalBidQty)
totalofferqty = Feature(FeatureType.TotalOfferQty)
weightedavgbidpx = Feature(FeatureType.WeightedAvgBidPx)
weightedavgofferpx = Feature(FeatureType.WeightedAvgOfferPx)
buy1price = Feature(FeatureType.Buy1Price)
buy2price = Feature(FeatureType.Buy2Price)
sell1price = Feature(FeatureType.Sell1Price)
sell2price = Feature(FeatureType.Sell2Price)
buy1orderqty = Feature(FeatureType.Buy1OrderQty)
buy2orderqty = Feature(FeatureType.Buy2OrderQty)
sell1orderqty = Feature(FeatureType.Sell1OrderQty)
sell2orderqty = Feature(FeatureType.Sell2OrderQty)
buy1numorders = Feature(FeatureType.Buy1NumOrders)
buy2numorders = Feature(FeatureType.Buy2NumOrders)
sell1numorders = Feature(FeatureType.Sell1NumOrders)
sell2numorders = Feature(FeatureType.Sell2NumOrders)
pre_close = Feature(FeatureType.pre_close)
ff_shares = Feature(FeatureType.ff_shares)


