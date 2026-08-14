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
import java.util.Map;

public class Saturn_t940_wd_k10_bid_d_amt
extends BaseFactor {
    public Saturn_t940_wd_k10_bid_d_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_bid_d_amt"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.45;
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        if (lastTick != null && lastTick.getTotalValueTrade() > 0.0) {
            value = lastTick.getWeightedAvgBidPx() * lastTick.getTotalBidQty() / lastTick.getTotalValueTrade();
        }
        this.updateValue(0, value);
    }
}

