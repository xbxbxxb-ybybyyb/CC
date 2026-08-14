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

public class Saturn_t930_wd_jhk_tot_bid_m_ask_rate
extends BaseFactor {
    public Saturn_t930_wd_jhk_tot_bid_m_ask_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhk_tot_bid_m_ask_rate"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Quote quote = this.marketDataManager.getLastQuote();
        double value = quote != null ? (quote.getBidVol() - quote.getAskVol()) / this.marketDataManager.getFreeFloatCapital() : 0.0;
        this.updateValue(0, Double.isInfinite(value) || Double.isNaN(value) ? 0.0 : value);
    }
}

