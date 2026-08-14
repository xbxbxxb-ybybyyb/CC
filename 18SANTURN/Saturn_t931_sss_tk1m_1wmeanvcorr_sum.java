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
import java.util.Map;

public class Saturn_t931_sss_tk1m_1wmeanvcorr_sum
extends BaseFactor {
    public Saturn_t931_sss_tk1m_1wmeanvcorr_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_1wmeanvcorr_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> buy_q = new ArrayList<Double>();
        ArrayList<Double> sell_q = new ArrayList<Double>();
        ArrayList<Double> buy = new ArrayList<Double>();
        ArrayList<Double> sell = new ArrayList<Double>();
        for (Tick t : this.marketDataManager.getLxjjTickList()) {
            if (t.getMdTime() <= 93000000L) continue;
            if (t.getTotalBidQty() != 0.0 && t.getWeightedAvgBidPx() != 0.0) {
                buy.add(t.getWeightedAvgBidPx());
                buy_q.add(t.getTotalBidQty());
            }
            if (t.getTotalOfferQty() == 0.0 || t.getWeightedAvgOfferPx() == 0.0) continue;
            sell.add(t.getWeightedAvgOfferPx());
            sell_q.add(t.getTotalOfferQty());
        }
        double value = Correlation.pearsonCorrelation(buy, buy_q) + Correlation.pearsonCorrelation(sell, sell_q);
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0;
        }
        this.updateValue(0, value);
    }
}

