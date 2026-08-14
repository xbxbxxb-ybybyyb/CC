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

public class Saturn_t940_wd_t10_vwap_1d5
extends BaseFactor {
    private double m1Amt;
    private double m1Qty;
    private double m5Amt;
    private double m5Qty;

    public Saturn_t940_wd_t10_vwap_1d5(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_vwap_1d5"};
        this.updateMode = 1;
    }

    @Override
    public void update(Trade trade) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime >= 93500000L) {
            this.m5Amt += trade.getTurnover().doubleValue();
            this.m5Qty += trade.getQuantity().doubleValue();
            if (mdTime >= 93900000L) {
                this.m1Amt += trade.getTurnover().doubleValue();
                this.m1Qty += trade.getQuantity().doubleValue();
            }
        }
    }

    @Override
    public void calculate() {
        double value = 1.01;
        if (this.m1Qty != 0.0 && (value = this.m1Amt / this.m1Qty / (this.m5Amt / this.m5Qty)) < 1.0) {
            value = 1.0 / value;
        }
        this.updateValue(0, value);
    }
}

