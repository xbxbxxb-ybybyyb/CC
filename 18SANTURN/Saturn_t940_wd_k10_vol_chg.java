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
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_vol_chg
extends BaseFactor {
    public Saturn_t940_wd_k10_vol_chg(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_vol_chg"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = -0.3;
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        if (tickList != null) {
            ArrayList<Double> volList = new ArrayList<Double>();
            ArrayList<Double> mdList = new ArrayList<Double>();
            double lastVol = Double.NaN;
            for (Tick t : tickList) {
                if (!Double.isNaN(lastVol) && t.getTotalVolumeTrade() - lastVol != 0.0) {
                    volList.add(t.getTotalVolumeTrade() - lastVol);
                    mdList.add(1.0 * (double)t.getMdTime());
                }
                lastVol = t.getTotalVolumeTrade();
            }
            if (mdList.size() != 0) {
                value = Correlation.spearmanCorrelation(mdList, volList);
            }
        }
        this.updateValue(0, Double.isNaN(value) ? -0.3 : value);
    }
}

