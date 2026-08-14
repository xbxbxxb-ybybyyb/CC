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

public class Saturn_t940_wd_t10_big_bid_vol_pct
extends BaseFactor {
    public Saturn_t940_wd_t10_big_bid_vol_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_big_bid_vol_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double tradeQty1 = 0.0;
        Double tradeQty2 = 0.0;
        for (MarketOrder order : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (order.getAmt() > 50000.0) {
                tradeQty1 = tradeQty1 + order.getQty();
            }
            tradeQty2 = tradeQty2 + order.getQty();
        }
        Double value = tradeQty1 / tradeQty2;
        if (value.isNaN() || value.isInfinite()) {
            value = 0.8;
        }
        this.updateValue(0, value);
    }
}

