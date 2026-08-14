/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_t10_high_price_pct_sum
extends BaseFactor {
    public Saturn_t940_wd_t10_high_price_pct_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_high_price_pct_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.15;
        List<Fill> lxjjFillList = this.marketDataManager.getLxjjFillList();
        if (lxjjFillList.size() > 0) {
            double medPx = (lxjjFillList.get(0).getPrice() + lxjjFillList.get(lxjjFillList.size() - 1).getPrice()) / 2.0;
            HashMap<Long, Double> maxPxMap = new HashMap<Long, Double>();
            HashMap<Long, Double> minPxMap = new HashMap<Long, Double>();
            for (Fill f : lxjjFillList) {
                if (!(f.getPrice() < medPx)) continue;
                maxPxMap.merge(f.getSellNo(), f.getPrice(), Double::max);
                minPxMap.merge(f.getSellNo(), f.getPrice(), Double::min);
            }
            value = 0.0;
            for (Long sellNo : maxPxMap.keySet()) {
                value += (Double)maxPxMap.get(sellNo) / (Double)minPxMap.get(sellNo) - 1.0;
            }
        }
        this.updateValue(0, value);
    }
}

