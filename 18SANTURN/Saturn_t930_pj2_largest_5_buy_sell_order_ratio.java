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
import java.util.Comparator;
import java.util.Map;

public class Saturn_t930_pj2_largest_5_buy_sell_order_ratio
extends BaseFactor {
    public Saturn_t930_pj2_largest_5_buy_sell_order_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_largest_5_buy_sell_order_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sum1 = this.marketDataManager.getJhjjTradeBuyMap().values().stream().map(MarketOrder::getQty).sorted(Comparator.reverseOrder()).limit(5L).reduce(Double::sum).orElse(0.0);
        double sum2 = this.marketDataManager.getJhjjTradeSellMap().values().stream().map(MarketOrder::getQty).sorted(Comparator.reverseOrder()).limit(5L).reduce(Double::sum).orElse(0.0);
        double value = sum2 == 0.0 ? 0.0 : sum1 / sum2;
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.0 : value);
    }
}

