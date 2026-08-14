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

public class Saturn_t940_wd_t10_act_bid_rate
extends BaseFactor {
    Double totalTradeQty = 0.0;
    Double actTradeQty = 0.0;

    public Saturn_t940_wd_t10_act_bid_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_act_bid_rate"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            Saturn_t940_wd_t10_act_bid_rate saturn_t940_wd_t10_act_bid_rate;
            if (fill.getSide() == Trade.Side.Bid) {
                saturn_t940_wd_t10_act_bid_rate = this;
                saturn_t940_wd_t10_act_bid_rate.actTradeQty = saturn_t940_wd_t10_act_bid_rate.actTradeQty + fill.getQty();
            }
            saturn_t940_wd_t10_act_bid_rate = this;
            saturn_t940_wd_t10_act_bid_rate.totalTradeQty = saturn_t940_wd_t10_act_bid_rate.totalTradeQty + fill.getQty();
        }
    }

    @Override
    public void calculate() {
        double value = 0.5;
        if (this.totalTradeQty != 0.0) {
            value = this.actTradeQty / this.totalTradeQty;
        }
        this.updateValue(0, value);
    }
}

