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

public class Saturn_t940_wd_k10_rise_vwap_d_p
extends BaseFactor {
    public Saturn_t940_wd_k10_rise_vwap_d_p(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_rise_vwap_d_p"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.9996;
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (lxjjTickList != null) {
            ArrayList<Double> values = new ArrayList<Double>();
            for (int i = 1; i < lxjjTickList.size(); ++i) {
                if (!(lxjjTickList.get(i).getLastPx() >= lxjjTickList.get(i - 1).getLastPx())) continue;
                double amt = lxjjTickList.get(i).getTotalValueTrade() - lxjjTickList.get(i - 1).getTotalValueTrade();
                double vol = lxjjTickList.get(i).getTotalVolumeTrade() - lxjjTickList.get(i - 1).getTotalVolumeTrade();
                if (vol == 0.0) {
                    vol = Double.NaN;
                }
                values.add(amt / vol / lxjjTickList.get(i).getLastPx());
            }
            double v = MathUtil.calcNaNMean(values);
            if (!Double.isNaN(v) && !Double.isInfinite(v)) {
                value = v;
            }
        }
        this.updateValue(0, value);
    }
}

