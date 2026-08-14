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

public class Saturn_t931_sss_tk1m_cl2hl
extends BaseFactor {
    public Saturn_t931_sss_tk1m_cl2hl(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_cl2hl"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List tickList = this.marketDataManager.getCurrentTickList().stream().filter(a -> a.getLastPx() > 0.0).collect(Collectors.toList());
        double factorValue = 0.5;
        if (tickList.size() > 0) {
            double max_last_px = Double.MIN_VALUE;
            double min_last_px = Double.MAX_VALUE;
            for (Tick tick : tickList) {
                max_last_px = Math.max(max_last_px, tick.getLastPx());
                min_last_px = Math.min(min_last_px, tick.getLastPx());
            }
            factorValue = (((Tick)tickList.get(tickList.size() - 1)).getLastPx() - min_last_px) / (max_last_px - min_last_px);
        }
        this.updateValue(0, factorValue);
    }
}

