/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.util.DecimalUtil
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.util.DecimalUtil;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_t10_non_time_bid_pct
extends BaseFactor {
    public Saturn_t940_wd_t10_non_time_bid_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_non_time_bid_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double sum1 = 0.0;
        Double sum2 = 0.0;
        for (MarketOrder order : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (DecimalUtil.isZero((double)order.getFillTimeDelta())) {
                sum1 = sum1 + order.getQty();
            }
            sum2 = sum2 + order.getQty();
        }
        double value = sum1 / sum2;
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.8;
        }
        this.updateValue(0, value);
    }
}

