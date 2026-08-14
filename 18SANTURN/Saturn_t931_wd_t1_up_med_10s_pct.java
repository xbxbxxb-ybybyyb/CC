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
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_up_med_10s_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_up_med_10s_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_up_med_10s_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, Long> firstActiveFillTimeMap = new TreeMap<Long, Long>();
        for (Fill f : this.marketDataManager.getLxjjFillList()) {
            long activeNo = Math.max(f.getSellNo(), f.getBuyNo());
            long passiveNo = Math.min(f.getSellNo(), f.getBuyNo());
            if (!firstActiveFillTimeMap.containsKey(activeNo) || firstActiveFillTimeMap.get(activeNo) == null) {
                firstActiveFillTimeMap.put(activeNo, TimeUtil.DateToWKT(f.getTimestamp()));
            }
            if (firstActiveFillTimeMap.containsKey(passiveNo)) continue;
            firstActiveFillTimeMap.put(passiveNo, null);
        }
        TreeMap<Long, Double> timeDeltaMap = new TreeMap<Long, Double>();
        long lastActiveFillTime = 93000000L;
        for (Long t1 : firstActiveFillTimeMap.keySet()) {
            if (firstActiveFillTimeMap.get(t1) == null) {
                firstActiveFillTimeMap.put(t1, lastActiveFillTime);
            } else {
                lastActiveFillTime = (Long)firstActiveFillTimeMap.get(t1);
            }
            timeDeltaMap.put(t1, 1.0 * (double)TimeUtil.calTimeDelta(93000000L, (Long)firstActiveFillTimeMap.get(t1)) / 1000.0);
        }
        double medianPrice = MathUtil.calcMedian(this.marketDataManager.getLxjjFillList().stream().mapToDouble(Fill::getPrice).toArray());
        double sum1 = 0.0;
        double sum2 = 0.0;
        for (Fill fill : this.marketDataManager.getLxjjFillList()) {
            if (!(fill.getPrice() >= medianPrice)) continue;
            double diff = (Double)timeDeltaMap.get(fill.getBuyNo()) - (Double)timeDeltaMap.get(fill.getSellNo());
            if (Math.abs(diff) < 10.0) {
                sum1 += fill.getQty().doubleValue();
            }
            sum2 += fill.getQty().doubleValue();
        }
        double factorValue = Double.NaN;
        if (sum2 != 0.0) {
            factorValue = sum1 / sum2;
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.85 : factorValue);
    }
}

