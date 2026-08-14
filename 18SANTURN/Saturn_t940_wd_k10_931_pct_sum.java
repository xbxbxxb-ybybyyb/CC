/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_k10_931_pct_sum
extends BaseFactor {
    public Saturn_t940_wd_k10_931_pct_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_931_pct_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double preLastPx = Double.NaN;
        double value = 0.0;
        for (Tick t : this.marketDataManager.getCurrentTickList()) {
            if (t.getMdTime() > 93100000L) continue;
            if (!Double.isNaN(preLastPx) && t.getLastPx() != 0.0) {
                value += Math.abs(t.getLastPx() / preLastPx - 1.0);
            }
            if (t.getLastPx() != 0.0) {
                preLastPx = t.getLastPx();
                continue;
            }
            preLastPx = Double.NaN;
        }
        this.updateValue(0, value);
    }
}

