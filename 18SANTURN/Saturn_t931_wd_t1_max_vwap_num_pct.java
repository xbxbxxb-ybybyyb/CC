/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.OrderSide
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.OrderSide;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_max_vwap_num_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_max_vwap_num_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_vwap_num_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Set lxjjTotalOrders = this.marketDataManager.getLxjjTotalOrderMap().keySet();
        Map<OrderSide, Long> countInfo = lxjjTotalOrders.stream().skip(Math.max(0, lxjjTotalOrders.size() - 100)).collect(Collectors.groupingBy(MarketOrder::getSide, Collectors.counting()));
        long size = countInfo.getOrDefault(OrderSide.Buy, 0L) + countInfo.getOrDefault(OrderSide.Sell, 0L);
        long buySize = countInfo.getOrDefault(OrderSide.Buy, 0L);
        double value = 0.7;
        if (size != 0L) {
            value = (double)buySize * 1.0 / (double)size;
        }
        this.updateValue(0, value);
    }
}

