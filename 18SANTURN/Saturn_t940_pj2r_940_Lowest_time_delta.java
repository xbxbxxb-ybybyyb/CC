/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;

public class Saturn_t940_pj2r_940_Lowest_time_delta
extends BaseFactor {
    double lowestPx = Double.MAX_VALUE;
    double lowestTimeDelta = 0.0;

    public Saturn_t940_pj2r_940_Lowest_time_delta(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Lowest_time_delta"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L && fill.getPrice() < this.lowestPx) {
            this.lowestPx = fill.getPrice();
            this.lowestTimeDelta = TimeUtil.calTimeDelta(93000000L, mdTime);
        }
    }

    @Override
    public void calculate() {
        if (this.marketDataManager.getLxjjFillList().size() == 0) {
            this.lowestTimeDelta = 30000.0;
        }
        this.updateValue(0, this.lowestTimeDelta);
    }
}

