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

public class Saturn_t930_wd_jhcs_bid_amt_rank
extends BaseFactor {
    public Saturn_t930_wd_jhcs_bid_amt_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhcs_bid_amt_rank"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        if (null != lastTick) {
            double last = lastTick.getTotalBidQty() * lastTick.getWeightedAvgBidPx();
            int equalLessCount = 0;
            int lessCount = 0;
            Map<String, Tick> lastTickMap = this.marketDataManager.getLastTickMap();
            for (Tick tick : lastTickMap.values()) {
                double toCompare = tick.getTotalBidQty() * tick.getWeightedAvgBidPx();
                if (toCompare < last) {
                    ++lessCount;
                    ++equalLessCount;
                    continue;
                }
                if (toCompare != last) continue;
                ++equalLessCount;
            }
            value = ((double)(equalLessCount + lessCount) + 1.0) / 2.0 / (double)lastTickMap.size();
        }
        this.updateValue(0, value);
    }
}

