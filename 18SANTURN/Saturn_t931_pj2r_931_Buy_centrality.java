/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_pj2r_931_Buy_centrality
extends BaseFactor {
    public Saturn_t931_pj2r_931_Buy_centrality(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Buy_centrality"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        if (this.marketDataManager.getLxjjFillList().size() > 0) {
            double tradeQtySum = this.marketDataManager.getLxjjTotalQty();
            double tradeQtySumSquare = this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(order -> Math.pow(order.getQty(), 2.0)).sum();
            value = tradeQtySum == 0.0 ? 0.0 : tradeQtySumSquare / Math.pow(tradeQtySum, 2.0);
        }
        this.updateValue(0, value);
    }
}

