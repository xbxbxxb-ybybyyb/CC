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

public class Saturn_t931_wd_k1_da_a_corr
extends BaseFactor {
    public Saturn_t931_wd_k1_da_a_corr(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_da_a_corr"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.0;
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        if (tickList != null) {
            ArrayList<Double> deltaAskAmts = new ArrayList<Double>();
            ArrayList<Double> amts = new ArrayList<Double>();
            double lastAskAmt = Double.NaN;
            for (int i = 0; i < tickList.size(); ++i) {
                Tick t = tickList.get(i);
                double amt = i == 0 ? t.getTotalValueTrade() - this.marketDataManager.getJhjjTotalAmt() : t.getTotalValueTrade() - tickList.get(i - 1).getTotalValueTrade();
                if (!(t.getLastPx() > 0.0)) continue;
                double askAmt = t.getTotalOfferQty() * t.getWeightedAvgOfferPx();
                if (!Double.isNaN(askAmt - lastAskAmt) && !Double.isNaN(amt)) {
                    deltaAskAmts.add(askAmt - lastAskAmt);
                    amts.add(amt);
                }
                lastAskAmt = askAmt;
            }
            factorValue = Correlation.spearmanCorrelation(deltaAskAmts, amts);
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }
}

