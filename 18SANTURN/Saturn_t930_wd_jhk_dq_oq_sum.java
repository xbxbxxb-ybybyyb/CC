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
import java.util.List;
import java.util.Map;

public class Saturn_t930_wd_jhk_dq_oq_sum
extends BaseFactor {
    public Saturn_t930_wd_jhk_dq_oq_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhk_dq_oq_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List tickList = this.marketDataManager.getTickListMap().get((Object)this.marketDataManager.getSymbol());
        Tick openTick = null;
        for (Tick tick : tickList) {
            if (!(tick.getTotalValueTrade() > 0.0)) continue;
            openTick = tick;
            break;
        }
        double value = Double.NaN;
        if (openTick != null) {
            double openQty = openTick.getTotalVolumeTrade();
            long openMdTime = openTick.getMdTime();
            HashMap<Long, Double> sumMap = new HashMap<Long, Double>();
            HashMap<Long, Integer> countMap = new HashMap<Long, Integer>();
            for (Tick tick : tickList) {
                if (tick.getMdTime() >= openMdTime || !(tick.getBidQty(0) + tick.getAskQty(0) > 0.0)) continue;
                long by10s = tick.getMdTime() / 10000L;
                sumMap.merge(by10s, tick.getBidQty(0), Double::sum);
                countMap.merge(by10s, 1, Integer::sum);
            }
            value = 0.0;
            for (Long key : sumMap.keySet()) {
                value += (Double)sumMap.get(key) / (double)((Integer)countMap.get(key)).intValue();
            }
            value /= openQty;
        }
        this.updateValue(0, Double.isNaN(value) ? 20.0 : value);
    }
}

