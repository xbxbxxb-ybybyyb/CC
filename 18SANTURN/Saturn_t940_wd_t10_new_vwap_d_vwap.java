/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_t10_new_vwap_d_vwap
extends BaseFactor {
    private double newAmt;
    private double newQty;
    private double oldAmt;
    private double oldQty;

    public Saturn_t940_wd_t10_new_vwap_d_vwap(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_new_vwap_d_vwap"};
        this.updateMode = 1;
        this.newAmt = 0.0;
        this.newQty = 0.0;
        this.oldAmt = 0.0;
        this.oldQty = 0.0;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            if (mdTime >= 93500000L) {
                this.newAmt += fill.getAmt().doubleValue();
                this.newQty += fill.getQty().doubleValue();
            } else {
                this.oldAmt += fill.getAmt().doubleValue();
                this.oldQty += fill.getQty().doubleValue();
            }
        }
    }

    @Override
    public void calculate() {
        double newvwap = this.newAmt / this.newQty;
        double oldvwap = this.oldAmt / this.oldQty;
        double value = Double.max(newvwap, oldvwap) / Double.min(newvwap, oldvwap);
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 1.02;
        }
        this.updateValue(0, value);
    }
}

