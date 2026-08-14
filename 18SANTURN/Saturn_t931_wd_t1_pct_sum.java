/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_pct_sum
extends BaseFactor {
    private final TreeMap<Long, Double> tradeMoneyMap = new TreeMap();
    private final TreeMap<Long, Double> tradeQtyMap = new TreeMap();

    public Saturn_t931_wd_t1_pct_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_pct_sum"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        this.tradeMoneyMap.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
        this.tradeQtyMap.merge(fill.getMdTime() / 1000L, fill.getQty(), Double::sum);
    }

    @Override
    public void calculate() {
        double preVwap = 0.0;
        double pctSum = 0.0;
        for (long t : this.tradeMoneyMap.keySet()) {
            double pct;
            Double money = this.tradeMoneyMap.get(t);
            Double qty = this.tradeQtyMap.get(t);
            double vwap = money / qty;
            if (preVwap != 0.0 && !Double.isNaN(pct = vwap / preVwap - 1.0)) {
                pctSum += Math.abs(pct);
            }
            preVwap = vwap;
        }
        double factorValue = pctSum;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.1 : factorValue);
    }
}

