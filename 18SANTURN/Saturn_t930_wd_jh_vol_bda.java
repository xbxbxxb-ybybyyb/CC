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

public class Saturn_t930_wd_jh_vol_bda
extends BaseFactor {
    private final Set<Long> buyNoSet;
    private final Set<Long> sellNoSet;

    public Saturn_t930_wd_jh_vol_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_vol_bda"};
        this.updateMode = 2;
        this.buyNoSet = new HashSet<Long>();
        this.sellNoSet = new HashSet<Long>();
    }

    @Override
    public void update(Fill fill) {
        if (fill.getBuyNo() > fill.getSellNo()) {
            this.buyNoSet.add(fill.getBuyNo());
            this.sellNoSet.add(fill.getSellNo());
        }
    }

    @Override
    public void calculate() {
        double value = 0.5;
        if (this.buyNoSet.size() + this.sellNoSet.size() > 0) {
            value = (double)this.buyNoSet.size() / (double)(this.buyNoSet.size() + this.sellNoSet.size());
        }
        this.updateValue(0, value);
    }
}

