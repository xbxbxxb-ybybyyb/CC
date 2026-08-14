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
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_wd_k1_bid_p_std
extends BaseFactor {
    public Saturn_t931_wd_k1_bid_p_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_bid_p_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.001;
        List<Tick> currentTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (currentTickList != null) {
            double[] resArray = IntStream.range(1, currentTickList.size()).mapToDouble(i -> ((Tick)currentTickList.get(i)).getWeightedAvgBidPx() / ((Tick)currentTickList.get(i - 1)).getWeightedAvgBidPx()).toArray();
            value = MathUtil.calculateStd(resArray);
        }
        this.updateValue(0, Double.isNaN(value) ? 0.001 : value);
    }
}

