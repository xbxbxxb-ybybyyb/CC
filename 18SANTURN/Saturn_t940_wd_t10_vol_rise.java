/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_t10_vol_rise
extends BaseFactor {
    private double lastPx;
    private double riseQty;
    private double noneRiseQty;

    public Saturn_t940_wd_t10_vol_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_vol_rise"};
        this.updateMode = 1;
        this.lastPx = 0.0;
        this.riseQty = 0.0;
        this.noneRiseQty = 0.0;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            if (this.lastPx == 0.0) {
                if (fill.getSide() == Trade.Side.Bid) {
                    this.noneRiseQty += fill.getQty().doubleValue();
                }
            } else if (fill.getPrice() > this.lastPx) {
                if (fill.getSide() == Trade.Side.Bid) {
                    this.riseQty += fill.getQty().doubleValue();
                }
            } else if (fill.getSide() == Trade.Side.Bid) {
                this.noneRiseQty += fill.getQty().doubleValue();
            }
            this.lastPx = fill.getPrice();
        }
    }

    @Override
    public void calculate() {
        double value = 0.5;
        if (this.noneRiseQty != 0.0) {
            value = this.riseQty / this.noneRiseQty;
        }
        this.updateValue(0, value);
    }
}

