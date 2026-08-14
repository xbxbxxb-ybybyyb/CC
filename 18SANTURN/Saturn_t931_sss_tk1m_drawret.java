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
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_sss_tk1m_drawret
extends BaseFactor {
    public Saturn_t931_sss_tk1m_drawret(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_drawret"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List lastPriceList = this.marketDataManager.getCurrentLxjjTickList().stream().filter(a -> a.getMdTime() > 93000000L && a.getLastPx() > 0.0).map(Tick::getLastPx).collect(Collectors.toList());
        double cummax = Double.MIN_VALUE;
        double drawmax = Double.MIN_VALUE;
        Iterator iterator = lastPriceList.iterator();
        while (iterator.hasNext()) {
            double price = (Double)iterator.next();
            cummax = Math.max(cummax, price);
            drawmax = Math.max(drawmax, 1.0 - price / cummax);
        }
        if (Double.isNaN(drawmax)) {
            drawmax = 0.0;
        }
        this.updateValue(0, drawmax);
    }
}

