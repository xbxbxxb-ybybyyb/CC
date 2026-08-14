from alphagen.data.expression import Feature, Ref
from alphagen_qlib.stock_data import FeatureType, TargetType


amt = Feature(FeatureType.amt)
close = Feature(FeatureType.close)
free_float_shares = Feature(FeatureType.free_float_shares)
high = Feature(FeatureType.high)
low = Feature(FeatureType.low)
mkt_cap_ard = Feature(FeatureType.mkt_cap_ard)
open_ = Feature(FeatureType.open)
# pct_chg = Feature(FeatureType.pct_chg)
pre_close = Feature(FeatureType.pre_close)
# total_shares = Feature(FeatureType.total_shares)
turn = Feature(FeatureType.turn)
volume = Feature(FeatureType.volume)
open_ = Feature(FeatureType.open)
vwap = Feature(FeatureType.vwap)
# next_close = Feature(TargetType.next_close)
# target = next_close / close - 1

