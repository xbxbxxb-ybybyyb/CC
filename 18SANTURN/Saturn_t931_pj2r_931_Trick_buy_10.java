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

public class Saturn_t931_pj2r_931_Trick_buy_10
extends BaseFactor {
    public Saturn_t931_pj2r_931_Trick_buy_10(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Trick_buy_10"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double passiveLargeSellOrder10 = this.marketDataManager.getLxjjTradeSellMap().values().stream().filter(order -> order.getAmt() > 100000.0 && order.getSideSet().contains(Trade.Side.Offer)).mapToDouble(MarketOrder::getQty).sum();
        double value = 0.5;
        if (passiveLargeSellOrder10 != 0.0) {
            double activeSmallBuyOrders10 = this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(order -> order.getAmt() <= 100000.0 && order.getSideSet().contains(Trade.Side.Bid)).mapToDouble(MarketOrder::getQty).sum();
            value = activeSmallBuyOrders10 / passiveLargeSellOrder10;
        }
        this.updateValue(0, value);
    }
}

