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
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_wd_k1_warm_rise
extends BaseFactor {
    public Saturn_t931_wd_k1_warm_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_warm_rise"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.1;
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (lxjjTickList != null) {
            double[] pctArray = IntStream.range(1, lxjjTickList.size()).mapToDouble(i -> ((Tick)lxjjTickList.get(i)).getLastPx() / ((Tick)lxjjTickList.get(i - 1)).getLastPx() - 1.0).toArray();
            double pctStd = MathUtil.calculateStd(pctArray);
            value = Arrays.stream(pctArray).filter(pct -> pct >= 0.0 && pct <= 2.0 * pctStd).sum();
        }
        this.updateValue(0, Double.isNaN(value) ? 0.1 : value);
    }
}

