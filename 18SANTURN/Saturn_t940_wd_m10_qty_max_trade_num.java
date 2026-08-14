/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_qty_max_trade_num
extends BaseFactor {
    private final Map<Long, Double> qtyMap;
    private final Map<Long, Integer> numMap;

    public Saturn_t940_wd_m10_qty_max_trade_num(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_qty_max_trade_num"};
        this.updateMode = 1;
        this.qtyMap = new HashMap<Long, Double>();
        this.numMap = new HashMap<Long, Integer>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            long minute = mdTime / 100000L;
            this.qtyMap.merge(minute, fill.getQty(), Double::sum);
            this.numMap.merge(minute, 1, Integer::sum);
        }
    }

    @Override
    public void calculate() {
        double value = 3.25;
        if (this.qtyMap.size() != 0) {
            double[] countList = this.numMap.values().stream().sorted().mapToDouble(e -> e.intValue()).toArray();
            double medianCount = MathUtil.calculateSortedMedian(countList);
            double maxM1 = 0.0;
            double maxM2 = 0.0;
            for (Long mdTime : this.qtyMap.keySet()) {
                if ((double)this.numMap.get(mdTime).intValue() > medianCount) {
                    if (!(this.qtyMap.get(mdTime) > maxM1)) continue;
                    maxM1 = this.qtyMap.get(mdTime);
                    continue;
                }
                if (!(this.qtyMap.get(mdTime) > maxM2)) continue;
                maxM2 = this.qtyMap.get(mdTime);
            }
            if (maxM1 != 0.0 && maxM2 != 0.0) {
                value = maxM1 / maxM2;
            }
        }
        this.updateValue(0, value);
    }
}

