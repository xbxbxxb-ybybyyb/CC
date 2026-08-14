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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_t10_down_med_px_rise
extends BaseFactor {
    public Saturn_t940_wd_t10_down_med_px_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_down_med_px_rise"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        double medianPx = MathUtil.calculateSortedMedian(fillList.stream().mapToDouble(Fill::getPrice).sorted().toArray());
        HashMap<Long, Double> maxMap = new HashMap<Long, Double>();
        HashMap<Long, Double> minMap = new HashMap<Long, Double>();
        for (Fill fill : fillList) {
            if (!(fill.getPrice() <= medianPx)) continue;
            maxMap.merge(fill.getBuyNo(), fill.getPrice(), Double::max);
            minMap.merge(fill.getBuyNo(), fill.getPrice(), Double::min);
        }
        ArrayList<Double> risePctList = new ArrayList<Double>();
        for (Long number : maxMap.keySet()) {
            risePctList.add((Double)maxMap.get(number) / (Double)minMap.get(number) - 1.0);
        }
        double d = risePctList.stream().sorted(Comparator.reverseOrder()).limit(5L).mapToDouble(e -> e).sum();
        this.updateValue(0, d);
    }
}

