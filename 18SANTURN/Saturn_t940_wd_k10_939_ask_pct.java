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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.Map;

public class Saturn_t940_wd_k10_939_ask_pct
extends BaseFactor {
    public Saturn_t940_wd_k10_939_ask_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_939_ask_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double preClose = this.marketDataManager.getLastQuote().getPreviousClosingPx();
        ArrayList<Double> weightedAvgOfferPx = new ArrayList<Double>();
        for (Tick t : this.marketDataManager.getCurrentLxjjTickList()) {
            if (t.getMdTime() < 93900000L || t.getWeightedAvgOfferPx() == 0.0) continue;
            weightedAvgOfferPx.add(t.getWeightedAvgOfferPx());
        }
        double value = 1.06;
        if (weightedAvgOfferPx.size() > 0) {
            value = MathUtil.calculateMean(weightedAvgOfferPx) / preClose;
        }
        this.updateValue(0, value);
    }
}

