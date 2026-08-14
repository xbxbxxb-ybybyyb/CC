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

public class Saturn_t930_wd_jh_order_mean_bda
extends BaseFactor {
    public Saturn_t930_wd_jh_order_mean_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_order_mean_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<Long, MarketOrder> buyOrders = this.marketDataManager.getJhjjTradeBuyMap();
        Map<Long, MarketOrder> sellOrders = this.marketDataManager.getJhjjTradeSellMap();
        double buyQtyAvg = buyOrders.values().stream().mapToDouble(MarketOrder::getQty).sum();
        double sellQtyAvg = sellOrders.values().stream().mapToDouble(MarketOrder::getQty).sum();
        double value = (buyQtyAvg /= (double)buyOrders.size()) / (sellQtyAvg /= (double)sellOrders.size());
        this.updateValue(0, Double.isInfinite(value) || Double.isNaN(value) ? 1.0 : value);
    }
}

