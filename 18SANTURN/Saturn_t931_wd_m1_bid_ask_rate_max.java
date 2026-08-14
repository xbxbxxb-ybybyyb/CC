/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_m1_bid_ask_rate_max
extends BaseFactor {
    private final Set<Long> buyNoSet = new HashSet<Long>();
    private final Set<Long> sellNoSet = new HashSet<Long>();

    public Saturn_t931_wd_m1_bid_ask_rate_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_m1_bid_ask_rate_max"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        this.buyNoSet.add(fill.getBuyNo());
        this.sellNoSet.add(fill.getSellNo());
    }

    @Override
    public void calculate() {
        double value = (double)this.sellNoSet.size() / (double)this.buyNoSet.size();
        if (Double.isNaN(value) || Double.isInfinite(value) || value >= 50.0) {
            value = 1.0;
        }
        this.updateValue(0, value);
    }
}

