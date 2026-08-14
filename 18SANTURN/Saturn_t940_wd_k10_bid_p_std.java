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
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_bid_p_std
extends BaseFactor {
    public Saturn_t940_wd_k10_bid_p_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_bid_p_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.001;
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        if (currentTickList != null) {
            ArrayList<Double> weightedAvgBidPxList = new ArrayList<Double>();
            for (Tick tick : currentTickList) {
                if (tick.getMdTime() < 93000000L) continue;
                weightedAvgBidPxList.add(tick.getWeightedAvgBidPx());
            }
            ArrayList<Double> weightedAvgBidPxDiv = new ArrayList<Double>();
            for (int i = 1; i < weightedAvgBidPxList.size(); ++i) {
                weightedAvgBidPxDiv.add((Double)weightedAvgBidPxList.get(i) / (Double)weightedAvgBidPxList.get(i - 1));
            }
            value = MathUtil.calculateStd(weightedAvgBidPxDiv);
        }
        this.updateValue(0, value);
    }
}

