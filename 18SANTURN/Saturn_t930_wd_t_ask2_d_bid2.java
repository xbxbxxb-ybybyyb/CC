/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Quote
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 *  com.huatai.common.util.DecimalUtil
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Quote;
import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.common.util.DecimalUtil;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_wd_t_ask2_d_bid2
extends BaseFactor {
    public Saturn_t930_wd_t_ask2_d_bid2(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_t_ask2_d_bid2"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0035;
        double totalValueTrade = -1.0;
        for (Quote quote : this.marketDataManager.getQuoteList()) {
            if (!(quote.getTurnover() > totalValueTrade)) continue;
            if (!DecimalUtil.isZero((double)((QtyPrice)quote.getBids().get(1)).getPrice())) {
                value = ((QtyPrice)quote.getAsks().get(1)).getPrice() / ((QtyPrice)quote.getBids().get(1)).getPrice() - 1.0;
            }
            totalValueTrade = quote.getTurnover();
        }
        if (value > 0.1 || value < -0.1) {
            value = 0.0035;
        }
        this.updateValue(0, value);
    }
}

