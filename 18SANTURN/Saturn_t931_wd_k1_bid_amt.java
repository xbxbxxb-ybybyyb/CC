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

public class Saturn_t931_wd_k1_bid_amt
extends BaseFactor {
    public Saturn_t931_wd_k1_bid_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_bid_amt"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 8000000.0;
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        if (lastTick != null && lastTick.getLastPx() > 0.0) {
            value = lastTick.getTotalBidQty() * lastTick.getWeightedAvgBidPx();
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 8000000.0 : value);
    }
}

