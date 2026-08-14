/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_vwap_high_low_std
extends BaseFactor {
    private final Map<Long, Double> highMap;
    private final Map<Long, Double> lowMap;
    private final Map<Long, Double> qtyMap;
    private final Map<Long, Double> amtMap;

    public Saturn_t940_wd_m10_vwap_high_low_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_vwap_high_low_std"};
        this.updateMode = 1;
        this.highMap = new HashMap<Long, Double>();
        this.lowMap = new HashMap<Long, Double>();
        this.qtyMap = new HashMap<Long, Double>();
        this.amtMap = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            long minute = mdTime / 100000L;
            this.qtyMap.merge(minute, fill.getQty(), Double::sum);
            this.amtMap.merge(minute, fill.getAmt(), Double::sum);
            this.highMap.merge(minute, fill.getPrice(), Double::max);
            this.lowMap.merge(minute, fill.getPrice(), Double::min);
        }
    }

    @Override
    public void calculate() {
        double value = 5.7E-4;
        if (this.qtyMap.size() != 0) {
            ArrayList<Double> res = new ArrayList<Double>();
            for (long m : this.qtyMap.keySet()) {
                res.add(this.amtMap.get(m) / this.qtyMap.get(m) / (this.highMap.get(m) + this.lowMap.get(m)));
            }
            value = MathUtil.calculateStd(res);
        }
        this.updateValue(0, value);
    }
}

