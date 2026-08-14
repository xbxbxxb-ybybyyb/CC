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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_warm_rise
extends BaseFactor {
    public Saturn_t940_wd_k10_warm_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_warm_rise"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.1;
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (lxjjTickList != null) {
            ArrayList<Double> pctList = new ArrayList<Double>();
            for (int i = 1; i < lxjjTickList.size(); ++i) {
                if (lxjjTickList.get(i).getLastPx() == 0.0 || lxjjTickList.get(i - 1).getLastPx() == 0.0) continue;
                pctList.add(lxjjTickList.get(i).getLastPx() / lxjjTickList.get(i - 1).getLastPx() - 1.0);
            }
            double pct_std = MathUtil.calculateStd(pctList);
            value = 0.0;
            for (Double aDouble : pctList) {
                if (!(aDouble <= 2.0 * pct_std) || !(aDouble >= 0.0)) continue;
                value += aDouble.doubleValue();
            }
        }
        this.updateValue(0, value);
    }
}

