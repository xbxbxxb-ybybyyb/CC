/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.util.DecimalUtil
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.util.DecimalUtil;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t940_wd_t10_down_vol_bda
extends BaseFactor {
    public Saturn_t940_wd_t10_down_vol_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_down_vol_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        int sellCount;
        TreeMap<Long, MarketOrder> sellOrders = this.marketDataManager.getLxjjTradeSellMap();
        HashSet<Long> buyOrderNoSet = new HashSet<Long>();
        HashSet<Long> sellOrderNoSet = new HashSet<Long>();
        for (MarketOrder order : sellOrders.values()) {
            if (!DecimalUtil.equal((double)order.getMaxPrice(), (double)order.getMinPrice())) continue;
            sellOrderNoSet.add(order.getNo());
            for (Fill fill : order.getFillList()) {
                buyOrderNoSet.add(fill.getBuyNo());
            }
        }
        double value = 2.0;
        int buyCount = buyOrderNoSet.size();
        if (buyCount + (sellCount = sellOrderNoSet.size()) != 0) {
            value = (double)buyCount * 1.0 / (double)sellCount;
        }
        this.updateValue(0, value);
    }
}

