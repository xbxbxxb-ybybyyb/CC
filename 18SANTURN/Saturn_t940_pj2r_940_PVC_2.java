/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_pj2r_940_PVC_2
extends BaseFactor {
    private final Map<Double, Double> priceQtyMap;

    public Saturn_t940_pj2r_940_PVC_2(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_PVC_2"};
        this.updateMode = 2;
        this.priceQtyMap = new HashMap<Double, Double>();
    }

    @Override
    public void update(Fill fill) {
        this.priceQtyMap.merge(fill.getPrice(), fill.getQty(), Double::sum);
    }

    @Override
    public void calculate() {
        double[] highestPxQty = this.priceQtyMap.entrySet().stream().sorted(Map.Entry.comparingByKey(Comparator.reverseOrder())).mapToDouble(Map.Entry::getValue).toArray();
        double sum = 0.0;
        for (int i = 0; i < Math.min(2, highestPxQty.length); ++i) {
            sum += Math.pow(highestPxQty[i], 2.0);
        }
        double value = 0.0;
        double totalsum = this.priceQtyMap.values().stream().mapToDouble(e -> Math.pow(e, 2.0)).sum();
        if (totalsum != 0.0) {
            value = sum / totalsum;
        }
        this.updateValue(0, value);
    }
}

