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

public class Saturn_t930_pj2_number_buy_orders
extends BaseFactor {
    public Saturn_t930_pj2_number_buy_orders(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_number_buy_orders"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        this.updateValue(0, this.marketDataManager.getJhjjTradeBuyMap().size());
    }
}

