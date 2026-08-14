/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.List;
import java.util.Map;

public class Saturn_t931_pj2r_931_ret2o
extends BaseFactor {
    public Saturn_t931_pj2r_931_ret2o(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_ret2o"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.0;
        List<Fill> fillList = this.marketDataManager.getFillList();
        if (fillList.size() > 0) {
            Double lastPrice = fillList.get(fillList.size() - 1).getPrice();
            Double firstPrice = fillList.get(0).getPrice();
            factorValue = (lastPrice - firstPrice) / this.marketDataManager.getPreClose() * 100.0;
        }
        if (this.marketDataManager.isStartsWith3()) {
            factorValue /= 2.0;
        }
        factorValue = Double.isNaN(factorValue) ? 0.0 : factorValue;
        this.updateValue(0, factorValue);
    }
}

