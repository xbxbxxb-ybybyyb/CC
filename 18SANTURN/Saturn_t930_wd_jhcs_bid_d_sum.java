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

public class Saturn_t930_wd_jhcs_bid_d_sum
extends BaseFactor {
    public Saturn_t930_wd_jhcs_bid_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhcs_bid_d_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sum;
        double value = 5.0E-4;
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        if (lastTick != null && (sum = this.marketDataManager.getLastTickMap().values().stream().mapToDouble(t -> t.getTotalBidQty() * t.getWeightedAvgBidPx()).sum()) != 0.0) {
            value = lastTick.getTotalBidQty() * lastTick.getWeightedAvgBidPx() / sum;
        }
        this.updateValue(0, value);
    }
}

