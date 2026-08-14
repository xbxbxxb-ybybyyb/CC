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

public class Saturn_t931_qyh_T1mtra_power_inout_num_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_power_inout_num_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_power_inout_num_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double buy = this.marketDataManager.getLxjjTradeBuyMap().size();
        double sell = this.marketDataManager.getLxjjTradeSellMap().size();
        double factor = 1.0;
        if (buy > 0.0) {
            factor = sell / buy;
        }
        this.updateValue(0, factor);
    }
}

