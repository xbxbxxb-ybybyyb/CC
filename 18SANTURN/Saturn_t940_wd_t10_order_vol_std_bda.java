/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t940_wd_t10_order_vol_std_bda
extends BaseFactor {
    public Saturn_t940_wd_t10_order_vol_std_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_order_vol_std_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double bidStd = MathUtil.calculateStd(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getQty).toArray());
        double askStd = MathUtil.calculateStd(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getQty).toArray());
        double value = 0.8;
        if (askStd != 0.0 && !Double.isNaN(askStd) && !Double.isNaN(bidStd)) {
            value = bidStd / askStd;
        }
        this.updateValue(0, value);
    }
}

