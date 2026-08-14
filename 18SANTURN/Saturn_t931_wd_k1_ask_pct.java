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

public class Saturn_t931_wd_k1_ask_pct
extends BaseFactor {
    public Saturn_t931_wd_k1_ask_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_ask_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.06;
        List<Tick> currentTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (currentTickList != null) {
            Double preClose = this.marketDataManager.getPreClose();
            value = currentTickList.stream().filter(tick -> tick.getWeightedAvgOfferPx() != 0.0).mapToDouble(tick -> tick.getWeightedAvgOfferPx() / preClose).average().orElse(Double.NaN);
            if (this.marketDataManager.isStartsWith3()) {
                value = (value - 1.0) / 2.0 + 1.0;
            }
        }
        this.updateValue(0, Double.isNaN(value) ? 1.06 : value);
    }
}

