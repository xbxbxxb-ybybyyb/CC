/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;

public class Saturn_t931_pj2r_931_Minc_minus_mdd
extends BaseFactor {
    private final Map<Long, Double> timeToPriceMap;

    public Saturn_t931_pj2r_931_Minc_minus_mdd(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Minc_minus_mdd"};
        this.updateMode = 1;
        this.timeToPriceMap = new LinkedHashMap<Long, Double>();
    }

    private static double calcMincMinusMdd(Collection<Double> priceList) {
        double maxPrice = -10.0;
        double mdd = 0.0;
        double minPrice = 9999.0;
        double minc = 0.0;
        for (Double price : priceList) {
            maxPrice = Double.max(maxPrice, price);
            mdd = Double.min(mdd, price / maxPrice - 1.0);
            minPrice = Double.min(minPrice, price);
            minc = Double.max(minc, price / minPrice - 1.0);
        }
        return minc - mdd;
    }

    @Override
    public void update(Fill fill) {
        this.timeToPriceMap.put(fill.getMdTime(), fill.getPrice());
    }

    @Override
    public void calculate() {
        double value = this.timeToPriceMap.size() == 0 ? 0.2 : Saturn_t931_pj2r_931_Minc_minus_mdd.calcMincMinusMdd(this.timeToPriceMap.values());
        if (this.marketDataManager.isStartsWith3()) {
            value /= 2.0;
        }
        this.updateValue(0, value);
    }
}

