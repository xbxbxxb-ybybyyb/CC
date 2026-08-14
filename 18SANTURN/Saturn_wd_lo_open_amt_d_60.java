/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_wd_lo_open_amt_d_60
extends BaseFactor {
    private final double last60AvgOpenAmount;

    public Saturn_wd_lo_open_amt_d_60(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_wd_lo_open_amt_d_60"};
        this.last60AvgOpenAmount = marketDataManager.getParams().getLast60AvgOpenAmt();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double jhjjTotalAmt = this.marketDataManager.getJhjjTotalAmt();
        double factorValue = jhjjTotalAmt == 0.0 ? 0.0 : this.last60AvgOpenAmount / jhjjTotalAmt;
        this.updateValue(0, factorValue);
    }
}

