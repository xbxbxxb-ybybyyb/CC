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

public class Saturn_T_o2pre
extends BaseFactor {
    public Saturn_T_o2pre(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_T_o2pre"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double tO2pre = this.marketDataManager.getOpenToPreCloseRatioMap().get(this.marketDataManager.getSymbol());
        double newO2pre = this.marketDataManager.isStartsWith3() ? tO2pre / 2.0 : tO2pre;
        this.updateValue(0, newO2pre);
    }
}

