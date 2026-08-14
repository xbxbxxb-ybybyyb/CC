/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Quote
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Quote;
import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_wd_jhk_tot_bid_pct
extends BaseFactor {
    public Saturn_t930_wd_jhk_tot_bid_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhk_tot_bid_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        Quote quote = this.marketDataManager.getLastQuote();
        if (quote != null) {
            double bidVol = quote.getBidVol();
            double totalTradeVol = quote.getTotalVolume();
            if (totalTradeVol != 0.0) {
                value = bidVol / totalTradeVol;
            }
        }
        this.updateValue(0, value);
    }
}

