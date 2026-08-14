/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_down_vol_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_down_vol_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_down_vol_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> sellOrders = this.marketDataManager.getLxjjTradeSellMap();
        HashSet buyOrderNoSet = new HashSet();
        HashSet<Long> sellOrderNoSet = new HashSet<Long>();
        for (MarketOrder order : sellOrders.values()) {
            if (order.getMaxPrice() != order.getMinPrice()) continue;
            sellOrderNoSet.add(order.getNo());
            order.getFillList().forEach(fill -> buyOrderNoSet.add(fill.getBuyNo()));
        }
        double value = 2.0;
        if (sellOrderNoSet.size() != 0) {
            value = (double)buyOrderNoSet.size() / (double)sellOrderNoSet.size();
        }
        this.updateValue(0, value);
    }
}

