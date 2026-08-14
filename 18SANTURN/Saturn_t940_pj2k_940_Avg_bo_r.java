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

public class Saturn_t940_pj2k_940_Avg_bo_r
extends BaseFactor {
    public Saturn_t940_pj2k_940_Avg_bo_r(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2k_940_Avg_bo_r"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        List<Tick> currentTick = this.marketDataManager.getCurrentLxjjTickList();
        if (currentTick != null) {
            int i;
            double[] numerator = new double[currentTick.size()];
            double[] denominator = new double[currentTick.size()];
            for (int i2 = 0; i2 < currentTick.size(); ++i2) {
                numerator[i2] = 0.0;
                denominator[i2] = 0.0;
            }
            ArrayList<Double> res = new ArrayList<Double>();
            for (i = 0; i < currentTick.size(); ++i) {
                for (int j = 0; j < 10; ++j) {
                    int n = i;
                    numerator[n] = numerator[n] + currentTick.get(i).getBuyQtyPrice().get(j).getQuantity();
                    int n2 = i;
                    denominator[n2] = denominator[n2] + currentTick.get(i).getSellQtyPrice().get(j).getQuantity();
                }
            }
            for (i = 0; i < currentTick.size(); ++i) {
                Double r = numerator[i] / denominator[i];
                if (r.isNaN() || r.isInfinite()) continue;
                res.add(r);
            }
            if (res.size() != 0) {
                value = MathUtil.calculateMean(res);
            }
        }
        this.updateValue(0, value);
    }
}

