/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_wd_t1_act_rate_in_no_rise
extends BaseFactor {
    public Saturn_t931_wd_t1_act_rate_in_no_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_act_rate_in_no_rise"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double buyQty = 0.0;
        double sellQty = 0.0;
        for (MarketOrder order : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (order.getMaxPrice() != order.getMinPrice()) continue;
            double actBuy = order.getFillList().stream().filter(fill -> fill.getSide() == Trade.Side.Bid).mapToDouble(Fill::getQty).sum();
            buyQty += actBuy;
            sellQty += order.getQty() - actBuy;
        }
        double value = sellQty > 0.0 ? buyQty / sellQty : 0.64;
        this.updateValue(0, value);
    }
}

