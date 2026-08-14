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
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_corr_p_ask
extends BaseFactor {
    public Saturn_t940_wd_k10_corr_p_ask(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_corr_p_ask"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        double value = 0.75;
        if (lxjjTickList != null && lxjjTickList.size() > 10) {
            ArrayList<Double> lastPxList = new ArrayList<Double>();
            ArrayList<Double> weighedAvgOfferPx = new ArrayList<Double>();
            for (Tick t : lxjjTickList) {
                if (t.getWeightedAvgOfferPx() == 0.0) continue;
                weighedAvgOfferPx.add(t.getWeightedAvgOfferPx());
                lastPxList.add(t.getLastPx());
            }
            value = Correlation.spearmanCorrelation(lastPxList, weighedAvgOfferPx);
        }
        this.updateValue(0, Double.isNaN(value) ? 0.75 : value);
    }
}

