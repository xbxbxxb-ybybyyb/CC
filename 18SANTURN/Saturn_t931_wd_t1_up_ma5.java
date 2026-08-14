/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.EvictingQueue
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.EvictingQueue;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Collection;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_up_ma5
extends BaseFactor {
    private final TreeMap<Long, Double> tradeMoneyMap = new TreeMap();
    private final TreeMap<Long, Double> tradeQtyMap = new TreeMap();

    public Saturn_t931_wd_t1_up_ma5(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_up_ma5"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        this.tradeMoneyMap.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
        this.tradeQtyMap.merge(fill.getMdTime() / 1000L, fill.getQty(), Double::sum);
    }

    @Override
    public void calculate() {
        EvictingQueue queue = EvictingQueue.create((int)5);
        double count = 0.0;
        double totalCount = 0.0;
        for (long t : this.tradeMoneyMap.navigableKeySet()) {
            Double money = this.tradeMoneyMap.get(t);
            Double qty = this.tradeQtyMap.get(t);
            double vwap = money / qty;
            queue.add((Object)vwap);
            if (queue.size() >= 4) {
                double roundMa5;
                Double ma5 = MathUtil.calcNaNMean((Collection<Double>)queue);
                double roundVwap = MathUtil.roundDecimal(vwap, 10);
                if (roundVwap > (roundMa5 = MathUtil.roundDecimal(ma5, 10))) {
                    count += 1.0;
                }
            }
            totalCount += 1.0;
        }
        double factorValue = totalCount == 0.0 ? Double.NaN : count / totalCount;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.5 : factorValue);
    }
}

