/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_max_time
extends BaseFactor {
    private long highTime = 0L;
    private Double maxTradePrice = 0.0;

    public Saturn_t931_wd_t1_max_time(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_time"};
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
    }

    @Override
    public void calculate() {
        double factorValue = this.highTime < 92900000L ? -0.1 : (double)TimeUtil.calTimeDelta(93000000L, this.highTime) / 60.0 / 1000.0;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.5 : factorValue);
    }
}

