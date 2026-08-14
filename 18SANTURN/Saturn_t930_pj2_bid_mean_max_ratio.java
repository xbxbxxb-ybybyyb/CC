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

public class Saturn_t930_pj2_bid_mean_max_ratio
extends BaseFactor {
    public Saturn_t930_pj2_bid_mean_max_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_bid_mean_max_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.3;
        int count = 0;
        double max = 0.0;
        double sum = 0.0;
        for (Quote quote : this.marketDataManager.getQuoteList()) {
            if (!quote.getTradingPhaseCode().equals("1")) continue;
            double v = (((QtyPrice)quote.getAsks().get(0)).getQuantity() + ((QtyPrice)quote.getAsks().get(1)).getQuantity()) * ((QtyPrice)quote.getAsks().get(0)).getPrice();
            max = Double.max(max, v);
            sum += v;
            ++count;
        }
        if (count > 0 && max != 0.0) {
            value = sum / (double)count / max;
        }
        this.updateValue(0, Double.isNaN(value) ? 0.3 : value);
    }
}

