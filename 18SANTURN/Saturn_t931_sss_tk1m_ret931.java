/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_sss_tk1m_ret931
extends BaseFactor {
    public Saturn_t931_sss_tk1m_ret931(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_ret931"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List tickList = this.marketDataManager.getCurrentLxjjTickList().stream().filter(a -> a.getLastPx() > 0.0).collect(Collectors.toList());
        double factorValue = 0.0;
        if (tickList.size() > 0) {
            factorValue = ((Tick)tickList.get(tickList.size() - 1)).getLastPx() / ((Tick)tickList.get(0)).getLastPx() - 1.0;
        }
        if (this.marketDataManager.getSymbol().startsWith("3")) {
            factorValue /= 2.0;
        }
        this.updateValue(0, factorValue);
    }
}

