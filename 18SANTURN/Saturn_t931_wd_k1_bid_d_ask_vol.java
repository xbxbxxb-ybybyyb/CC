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
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_k1_bid_d_ask_vol
extends BaseFactor {
    public Saturn_t931_wd_k1_bid_d_ask_vol(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_bid_d_ask_vol"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        List<Tick> currentTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (currentTickList != null && currentTickList.size() > 0 && currentTickList.get(0).getTotalOfferQty() != 0.0) {
            value = currentTickList.get(0).getTotalBidQty() / currentTickList.get(0).getTotalOfferQty();
        }
        this.updateValue(0, value);
    }
}

