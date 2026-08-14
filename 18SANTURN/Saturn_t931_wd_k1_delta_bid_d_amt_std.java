/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_k1_delta_bid_d_amt_std
extends BaseFactor {
    public Saturn_t931_wd_k1_delta_bid_d_amt_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_delta_bid_d_amt_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 1.0;
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        if (tickList.size() > 0) {
            ArrayList<Double> serList = new ArrayList<Double>(tickList.size());
            ArrayList<Double> bidAmtList = new ArrayList<Double>(tickList.size());
            Tick preTick = null;
            for (Tick tick : tickList) {
                if (null != preTick && tick.getMdTime() >= 93000000L && tick.getLastPx() > 0.0) {
                    double bidAmt = tick.getTotalBidQty() * tick.getWeightedAvgBidPx();
                    double amt = tick.getTotalValueTrade() - preTick.getTotalValueTrade();
                    if (bidAmtList.size() > 0 && amt != 0.0) {
                        serList.add((bidAmt - (Double)bidAmtList.get(bidAmtList.size() - 1)) / amt);
                    }
                    bidAmtList.add(bidAmt);
                }
                preTick = tick;
            }
            factorValue = MathUtil.calculateStd(serList);
            factorValue = factorValue == 0.0 ? 1.0 : Math.log(factorValue);
        }
        this.updateValue(0, factorValue);
    }
}

