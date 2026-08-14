/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  org.apache.commons.lang3.tuple.MutablePair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.tuple.MutablePair;

public class Saturn_t931_wd_t1_down_med_rise_sum
extends BaseFactor {
    public Saturn_t931_wd_t1_down_med_rise_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_down_med_rise_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value;
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        if (fillList.size() == 0) {
            value = 0.01;
        } else {
            double medPrice = (fillList.get(0).getPrice() + fillList.get(fillList.size() - 1).getPrice()) / 2.0;
            HashMap<Long, MutablePair> maxAndMinPriceMap = new HashMap<Long, MutablePair>();
            for (Fill fill : fillList) {
                if (!(fill.getPrice() < medPrice)) continue;
                MutablePair maxAndMinPrice = maxAndMinPriceMap.computeIfAbsent(fill.getSellNo(), k -> MutablePair.of((Object)Double.MIN_VALUE, (Object)Double.MAX_VALUE));
                maxAndMinPrice.left = Double.max((Double)maxAndMinPrice.left, fill.getPrice());
                maxAndMinPrice.right = Double.min((Double)maxAndMinPrice.right, fill.getPrice());
            }
            value = maxAndMinPriceMap.values().stream().map(pair -> (Double)pair.left / (Double)pair.right - 1.0).sorted(Comparator.reverseOrder()).limit(5L).mapToDouble(Double::doubleValue).sum();
        }
        this.updateValue(0, Double.isNaN(value) ? 0.01 : value);
    }
}

