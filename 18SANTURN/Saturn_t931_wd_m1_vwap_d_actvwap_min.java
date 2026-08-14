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

public class Saturn_t931_wd_m1_vwap_d_actvwap_min
extends BaseFactor {
    private double actTradeMoney = 0.0;
    private double actTradeQty = 0.0;

    public Saturn_t931_wd_m1_vwap_d_actvwap_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_m1_vwap_d_actvwap_min"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() == Trade.Side.Bid) {
            this.actTradeMoney += fill.getAmt().doubleValue();
            this.actTradeQty += fill.getQty().doubleValue();
        }
    }

    @Override
    public void calculate() {
        double value = 0.098;
        if (this.marketDataManager.getLxjjTotalQty() != 0.0 && this.actTradeQty != 0.0) {
            value = this.marketDataManager.getLxjjTotalAmt() / this.marketDataManager.getLxjjTotalQty() / (this.actTradeMoney / this.actTradeQty);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.098 : value);
    }
}

