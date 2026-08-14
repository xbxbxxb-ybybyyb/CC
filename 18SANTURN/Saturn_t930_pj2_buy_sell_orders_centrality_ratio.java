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

public class Saturn_t930_pj2_buy_sell_orders_centrality_ratio
extends BaseFactor {
    public Saturn_t930_pj2_buy_sell_orders_centrality_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_buy_sell_orders_centrality_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sum1 = this.marketDataManager.getJhjjTradeBuyMap().values().stream().mapToDouble(o -> Math.pow(o.getQty(), 2.0)).sum();
        double sum2 = this.marketDataManager.getJhjjTradeSellMap().values().stream().mapToDouble(o -> Math.pow(o.getQty(), 2.0)).sum();
        double value = sum2 == 0.0 ? 0.0 : sum1 / sum2;
        this.updateValue(0, Double.isInfinite(value) || Double.isNaN(value) ? 0.0 : value);
    }
}

