/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_hdl_firstd10
extends BaseFactor {
    private final Map<Long, Double> hiMap;
    private final Map<Long, Double> lowMap;
    private long smallestMinute;

    public Saturn_t940_wd_m10_hdl_firstd10(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_hdl_firstd10"};
        this.updateMode = 1;
        this.hiMap = new HashMap<Long, Double>();
        this.lowMap = new HashMap<Long, Double>();
        this.smallestMinute = 940L;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L) {
            long minute = mdTime / 100000L;
            if (minute < this.smallestMinute) {
                this.smallestMinute = minute;
            }
            this.hiMap.merge(minute, fill.getPrice(), Double::max);
            this.lowMap.merge(minute, fill.getPrice(), Double::min);
        }
    }

    @Override
    public void calculate() {
        double value = 1.01;
        if (this.hiMap.size() != 0) {
            double smallestRatio = Double.MAX_VALUE;
            for (Long mdTime : this.hiMap.keySet()) {
                if (!(this.hiMap.get(mdTime) / this.lowMap.get(mdTime) < smallestRatio)) continue;
                smallestRatio = this.hiMap.get(mdTime) / this.lowMap.get(mdTime);
            }
            if (smallestRatio != 0.0) {
                value = this.hiMap.get(this.smallestMinute) / this.lowMap.get(this.smallestMinute) / smallestRatio;
            }
        }
        this.updateValue(0, value);
    }
}

