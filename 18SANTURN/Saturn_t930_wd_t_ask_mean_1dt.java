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
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t930_wd_t_ask_mean_1dt
extends BaseFactor {
    public Saturn_t930_wd_t_ask_mean_1dt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_t_ask_mean_1dt"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0046;
        TreeMap<Long, Double> map = new TreeMap<Long, Double>();
        double totAmt = 0.0;
        for (Fill fill : this.marketDataManager.getFillList()) {
            map.merge(fill.getSellNo(), fill.getAmt(), Double::sum);
            totAmt += fill.getAmt().doubleValue();
        }
        if (map.size() >= 2) {
            value = map.values().stream().limit(map.size() / 2).mapToDouble(x -> x).average().orElse(Double.NaN) / totAmt;
        }
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0046;
        }
        this.updateValue(0, value);
    }
}

