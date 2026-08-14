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
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_sss_tk1m_highamt_b2a
extends BaseFactor {
    private Map<Long, Double> amtMap = new HashMap<Long, Double>();

    public Saturn_t931_sss_tk1m_highamt_b2a(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_highamt_b2a"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double lastTotalValueTrade = null;
        Double maxLastPx = null;
        Long maxLastPxTime = null;
        for (Tick tick : this.marketDataManager.getCurrentTickList()) {
            if (lastTotalValueTrade == null) {
                this.amtMap.put(tick.getMdTime(), 0.0);
            } else {
                this.amtMap.put(tick.getMdTime(), tick.getTotalValueTrade() - lastTotalValueTrade);
            }
            lastTotalValueTrade = tick.getTotalValueTrade();
            if (maxLastPx != null && !(tick.getLastPx() > maxLastPx) || tick.getMdTime() <= 93000000L) continue;
            maxLastPx = tick.getLastPx();
            maxLastPxTime = tick.getMdTime();
        }
        double factorValue = 0.0;
        double sumBefore = 1.0;
        double sumAfter = 1.0;
        if (maxLastPxTime != null) {
            for (Tick tick : this.marketDataManager.getLxjjTickList()) {
                if (tick.getMdTime() <= 93000000L || tick.getLastPx() == 0.0) continue;
                if (tick.getMdTime() < maxLastPxTime) {
                    sumBefore += this.amtMap.get(tick.getMdTime()).doubleValue();
                    continue;
                }
                if (tick.getMdTime() <= maxLastPxTime) continue;
                sumAfter += this.amtMap.get(tick.getMdTime()).doubleValue();
            }
            factorValue = Math.log(sumBefore / sumAfter);
        }
        this.updateValue(0, Double.isNaN(factorValue) ? 0.0 : factorValue);
    }
}

