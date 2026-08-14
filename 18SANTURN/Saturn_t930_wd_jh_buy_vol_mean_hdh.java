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

public class Saturn_t930_wd_jh_buy_vol_mean_hdh
extends BaseFactor {
    public Saturn_t930_wd_jh_buy_vol_mean_hdh(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_buy_vol_mean_hdh"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value;
        Map<Long, MarketOrder> buyOrders = this.marketDataManager.getJhjjTradeBuyMap();
        int firstHalf = buyOrders.size() / 2;
        int lastHalf = buyOrders.size() - firstHalf;
        if (firstHalf > 0 && lastHalf > 0) {
            double firstHalfQty = buyOrders.values().stream().sorted(Comparator.comparing(MarketOrder::getNo)).limit(firstHalf).mapToDouble(MarketOrder::getQty).sum();
            double lastHalfQty = this.marketDataManager.getJhjjTotalQty() - firstHalfQty;
            value = (firstHalfQty /= (double)firstHalf) / (firstHalfQty + (lastHalfQty /= (double)lastHalf));
        } else {
            value = 0.4;
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.4 : value);
    }
}

