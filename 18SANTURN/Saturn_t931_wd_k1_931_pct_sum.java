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
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_wd_k1_931_pct_sum
extends BaseFactor {
    public Saturn_t931_wd_k1_931_pct_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_931_pct_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        if (currentTickList != null) {
            value = IntStream.range(1, currentTickList.size()).mapToDouble(i -> {
                Double lastPx = ((Tick)currentTickList.get(i)).getLastPx();
                Double preLastPx = ((Tick)currentTickList.get(i - 1)).getLastPx();
                return lastPx == 0.0 || preLastPx == 0.0 ? 0.0 : Math.abs(lastPx / preLastPx - 1.0);
            }).sum();
        }
        if (this.marketDataManager.isStartsWith3()) {
            value /= 2.0;
        }
        this.updateValue(0, value);
    }
}

