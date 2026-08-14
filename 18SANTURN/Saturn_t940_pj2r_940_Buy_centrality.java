/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t940_pj2r_940_Buy_centrality
extends BaseFactor {
    public Saturn_t940_pj2r_940_Buy_centrality(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Buy_centrality"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        if (this.marketDataManager.getLxjjFillList().size() > 0) {
            double tradeQtySum = 0.0;
            double tradeQtySumSquare = 0.0;
            TreeMap<Long, MarketOrder> buyOrder = this.marketDataManager.getLxjjTradeBuyMap();
            for (MarketOrder mkOrder : buyOrder.values()) {
                tradeQtySum += mkOrder.getQty().doubleValue();
                tradeQtySumSquare += Math.pow(mkOrder.getQty(), 2.0);
            }
            value = tradeQtySum == 0.0 ? 0.0 : tradeQtySumSquare / Math.pow(tradeQtySum, 2.0);
        }
        this.updateValue(0, value);
    }
}

