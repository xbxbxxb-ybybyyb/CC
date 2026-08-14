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

public class Saturn_t931_qyh_T1mtra_amtpertra_in_s_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_amtpertra_in_s_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_amtpertra_in_s_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double std = MathUtil.calculateStd(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getAmt).toArray());
        this.updateValue(0, Double.isNaN(std) ? 137000.0 : std);
    }
}

