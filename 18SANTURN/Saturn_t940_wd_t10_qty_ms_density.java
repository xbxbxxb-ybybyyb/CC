/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_t10_qty_ms_density
extends BaseFactor {
    private final HashMap<Integer, Double> secondQtyMap;

    public Saturn_t940_wd_t10_qty_ms_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_qty_ms_density"};
        this.updateMode = 1;
        this.secondQtyMap = new HashMap();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L && fill.getBuyNo() > fill.getSellNo()) {
            int dotSec = (int)(mdTime % 1000L / 100L);
            this.secondQtyMap.merge(dotSec, fill.getQty(), Double::sum);
        }
    }

    @Override
    public void calculate() {
        double sum = this.secondQtyMap.values().stream().mapToDouble(Double::doubleValue).sum();
        double value = 0.15;
        if (!this.secondQtyMap.isEmpty()) {
            value = 0.0;
            for (Map.Entry<Integer, Double> entry : this.secondQtyMap.entrySet()) {
                double tmp = entry.getValue() / sum;
                if (!(tmp > value)) continue;
                value = tmp;
            }
        }
        this.updateValue(0, value);
    }
}

