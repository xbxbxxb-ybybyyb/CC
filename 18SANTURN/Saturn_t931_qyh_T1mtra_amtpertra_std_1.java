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

public class Saturn_t931_qyh_T1mtra_amtpertra_std_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_amtpertra_std_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_amtpertra_std_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double mv;
        double amtPer = this.marketDataManager.getLxjjTotalAmt() / (double)this.marketDataManager.getLxjjFillList().size();
        double factor = amtPer / (mv = this.marketDataManager.getPreClose() * this.marketDataManager.getFreeFloatCapital());
        this.updateValue(0, Double.isNaN(factor) ? 0.111 : factor);
    }
}

