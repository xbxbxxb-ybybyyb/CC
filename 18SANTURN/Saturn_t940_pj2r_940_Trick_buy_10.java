/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t940_pj2r_940_Trick_buy_10
extends BaseFactor {
    public Saturn_t940_pj2r_940_Trick_buy_10(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Trick_buy_10"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> buyMap = this.marketDataManager.getLxjjTradeBuyMap();
        TreeMap<Long, MarketOrder> sellMap = this.marketDataManager.getLxjjTradeSellMap();
        double passive_large_sell_order_10 = 0.0;
        for (MarketOrder mkOrder : sellMap.values()) {
            if (!(mkOrder.getAmt() > 100000.0) || !mkOrder.getSideSet().contains(Trade.Side.Offer)) continue;
            passive_large_sell_order_10 += mkOrder.getQty().doubleValue();
        }
        double value = 0.5;
        if (passive_large_sell_order_10 != 0.0) {
            double active_small_buy_orders_10 = 0.0;
            for (MarketOrder mkOrder : buyMap.values()) {
                if (!(mkOrder.getAmt() <= 100000.0) || !mkOrder.getSideSet().contains(Trade.Side.Bid)) continue;
                active_small_buy_orders_10 += mkOrder.getQty().doubleValue();
            }
            value = active_small_buy_orders_10 / passive_large_sell_order_10;
        }
        this.updateValue(0, value);
    }
}

