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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t940_wd_t10_big_bid_rise_pct
extends BaseFactor {
    public Saturn_t940_wd_t10_big_bid_rise_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_big_bid_rise_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.02;
        TreeMap<Long, MarketOrder> fillMap = this.marketDataManager.getLxjjTradeBuyMap();
        if (!fillMap.isEmpty()) {
            double medianQty = MathUtil.calculateSortedMedian(fillMap.values().stream().mapToDouble(MarketOrder::getQty).sorted().toArray());
            ArrayList<Double> risePctList = new ArrayList<Double>();
            for (MarketOrder mkOrder : fillMap.values()) {
                if (!(mkOrder.getQty() <= medianQty)) continue;
                risePctList.add(mkOrder.getMaxPrice() / mkOrder.getMinPrice() - 1.0);
            }
            value = risePctList.stream().sorted(Comparator.reverseOrder()).limit(5L).mapToDouble(e -> e).sum();
        }
        this.updateValue(0, value);
    }
}

