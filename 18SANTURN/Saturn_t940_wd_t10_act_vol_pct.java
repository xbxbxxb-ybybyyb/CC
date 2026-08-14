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

public class Saturn_t940_wd_t10_act_vol_pct
extends BaseFactor {
    private Double buyQty = 0.0;
    private Double totalQty = 0.0;

    public Saturn_t940_wd_t10_act_vol_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_act_vol_pct"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        long time = this.marketDataManager.getLastFill().getMdTime();
        if (time < 94000000L) {
            Saturn_t940_wd_t10_act_vol_pct saturn_t940_wd_t10_act_vol_pct;
            if (fill.getSide() == Trade.Side.Bid) {
                saturn_t940_wd_t10_act_vol_pct = this;
                saturn_t940_wd_t10_act_vol_pct.buyQty = saturn_t940_wd_t10_act_vol_pct.buyQty + fill.getQty();
            }
            saturn_t940_wd_t10_act_vol_pct = this;
            saturn_t940_wd_t10_act_vol_pct.totalQty = saturn_t940_wd_t10_act_vol_pct.totalQty + fill.getQty();
        }
    }

    @Override
    public void calculate() {
        Double value = this.buyQty / this.totalQty;
        if (value.isNaN() || value.isInfinite()) {
            value = 0.5;
        }
        this.updateValue(0, value);
    }
}

