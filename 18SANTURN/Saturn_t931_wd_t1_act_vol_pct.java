/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_wd_t1_act_vol_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_act_vol_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_act_vol_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        if (this.marketDataManager.getLxjjTotalQty() != 0.0) {
            double actBuyQty = this.marketDataManager.getLxjjFillList().stream().filter(fill -> fill.getSide() == Trade.Side.Bid).mapToDouble(Fill::getQty).sum();
            value = actBuyQty / this.marketDataManager.getLxjjTotalQty();
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.5 : value);
    }
}

