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

public class Saturn_t930_wd_t_bid1_d_bid10
extends BaseFactor {
    public Saturn_t930_wd_t_bid1_d_bid10(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_t_bid1_d_bid10"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0125;
        double totalValueTrade = -1.0;
        for (Quote quote : this.marketDataManager.getQuoteList()) {
            if (!(quote.getTurnover() > totalValueTrade)) continue;
            if (!DecimalUtil.isZero((double)((QtyPrice)quote.getBids().get(9)).getPrice())) {
                value = ((QtyPrice)quote.getBids().get(0)).getPrice() / ((QtyPrice)quote.getBids().get(9)).getPrice() - 1.0;
            }
            totalValueTrade = quote.getTurnover();
        }
        if (value <= 0.0) {
            value = 0.0125;
        }
        this.updateValue(0, value);
    }
}

