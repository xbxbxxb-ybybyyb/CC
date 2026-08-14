/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_max_min_delta
extends BaseFactor {
    private long highTime = 0L;
    private long lowTime = 0L;
    private Double maxTradePrice = 0.0;
    private Double minTradePrice = Double.MAX_VALUE;

    public Saturn_t931_wd_t1_max_min_delta(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_min_delta"};
        this.updateMode = 2;
    }

    @Override
    public void update(Fill fill) {
        Double price = fill.getPrice();
        long mdTime = fill.getMdTime();
        if (price >= this.maxTradePrice) {
            this.maxTradePrice = price;
            this.highTime = mdTime;
        }
        if (price <= this.minTradePrice) {
            this.minTradePrice = price;
            this.lowTime = mdTime;
        }
    }

    @Override
    public void calculate() {
        double factorValue;
        double maxTime = -0.1;
        if (this.highTime >= 92900000L) {
            maxTime = (double)TimeUtil.calTimeDelta(93000000L, this.highTime) / 60.0 / 1000.0;
        }
        double minTime = -0.1;
        if (this.lowTime >= 92900000L) {
            minTime = (double)TimeUtil.calTimeDelta(93000000L, this.lowTime) / 60.0 / 1000.0;
        }
        this.updateValue(0, Double.isNaN(factorValue = maxTime - minTime) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }
}

