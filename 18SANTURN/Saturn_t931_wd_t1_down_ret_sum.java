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
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_down_ret_sum
extends BaseFactor {
    public Saturn_t931_wd_t1_down_ret_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_down_ret_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = -1.0;
        TreeMap<Long, MarketOrder> lxjjBuyOrders = this.marketDataManager.getLxjjTradeBuyMap();
        if (lxjjBuyOrders.size() > 1) {
            value = 0.0;
            Double preVwap = null;
            for (MarketOrder buyOrder : lxjjBuyOrders.values()) {
                double logR;
                if (preVwap != null && (logR = Math.log(buyOrder.getPrice() / preVwap)) < 0.0) {
                    value += logR;
                }
                preVwap = buyOrder.getPrice();
            }
            if (this.marketDataManager.isStartsWith3()) {
                value /= 2.0;
            }
        }
        this.updateValue(0, value);
    }
}

