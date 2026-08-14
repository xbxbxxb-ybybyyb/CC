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

public class Saturn_t930_wd_jhk_tot_ask_d_bid
extends BaseFactor {
    public Saturn_t930_wd_jhk_tot_ask_d_bid(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhk_tot_ask_d_bid"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double denominator;
        double value = 5.0;
        Quote lastQuote = this.marketDataManager.getLastQuote();
        if (lastQuote != null && (denominator = lastQuote.getBidVol() * lastQuote.getBid()) != 0.0) {
            value = lastQuote.getAskVol() * lastQuote.getAsk() / denominator;
        }
        this.updateValue(0, value);
    }
}

