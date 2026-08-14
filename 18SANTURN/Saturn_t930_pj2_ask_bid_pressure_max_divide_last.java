/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Quote
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Quote;
import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_pj2_ask_bid_pressure_max_divide_last
extends BaseFactor {
    public Saturn_t930_pj2_ask_bid_pressure_max_divide_last(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_ask_bid_pressure_max_divide_last"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        Double max = null;
        double div = 0.0;
        for (Quote quote : this.marketDataManager.getQuoteList()) {
            double res;
            if (!quote.getTradingPhaseCode().equals("1") || Double.isInfinite(res = (((QtyPrice)quote.getBids().get(0)).getQuantity() + ((QtyPrice)quote.getBids().get(1)).getQuantity()) / (((QtyPrice)quote.getAsks().get(0)).getQuantity() + ((QtyPrice)quote.getAsks().get(1)).getQuantity())) || Double.isNaN(res)) continue;
            max = null == max ? res : Double.max(max, res);
            div = res;
        }
        if (null != max && div != 0.0) {
            value = max / div;
        }
        this.updateValue(0, value);
    }
}

