/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_t10_trade_ms_density
extends BaseFactor {
    private final HashMap<Integer, Integer> secondCountMap;

    public Saturn_t940_wd_t10_trade_ms_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_trade_ms_density"};
        this.updateMode = 1;
        this.secondCountMap = new HashMap();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L && mdTime >= 93000000L && fill.getBuyNo() > fill.getSellNo()) {
            int dotSec = (int)(mdTime % 1000L / 100L);
            this.secondCountMap.merge(dotSec, 1, Integer::sum);
        }
    }

    @Override
    public void calculate() {
        int sum = this.secondCountMap.values().stream().mapToInt(Integer::intValue).sum();
        double value = 0.0;
        if (!this.secondCountMap.isEmpty()) {
            for (Map.Entry<Integer, Integer> entry : this.secondCountMap.entrySet()) {
                double tmp = (double)entry.getValue().intValue() / (double)sum;
                if (!(tmp > value)) continue;
                value = tmp;
            }
        } else {
            value = 0.12;
        }
        this.updateValue(0, value);
    }
}

