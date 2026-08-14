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

public class Saturn_t930_pj2_longest_sell_order
extends BaseFactor {
    public Saturn_t930_pj2_longest_sell_order(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_longest_sell_order"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        int max = this.marketDataManager.getJhjjTradeSellMap().values().stream().mapToInt(e -> e.getFillList().size()).max().orElse(0);
        this.updateValue(0, max);
    }
}

