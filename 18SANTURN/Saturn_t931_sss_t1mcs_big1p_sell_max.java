/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1mcs_big1p_sell_max
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_t1mcs_big1p_sell_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1mcs_big1p_sell_max"};
        for (Map.Entry<String, Integer> entry : marketDataManager.getSaturnAfterNotUlLenMap().entrySet()) {
            if (entry.getValue() <= 10) continue;
            this.stockSet.add(entry.getKey());
        }
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double currPct = Double.NaN;
        double max = Double.NEGATIVE_INFINITY;
        for (String stock : this.stockSet) {
            HashMap<Long, Double> sellMap = new HashMap<Long, Double>();
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (!(trade.getTurnover() > 0.0)) continue;
                sellMap.merge(trade.getTradeSellNo(), trade.getTurnover(), Double::sum);
            }
            if (sellMap.isEmpty()) continue;
            double mean = MathUtil.calculateMean(sellMap.values());
            double std = MathUtil.calculateStd(sellMap.values());
            double sum = MathUtil.calculateSum(sellMap.values());
            double filterSum = 0.0;
            Iterator iterator = sellMap.values().iterator();
            while (iterator.hasNext()) {
                double val = (Double)iterator.next();
                if (!(val < mean + std)) continue;
                filterSum += val;
            }
            double pct = filterSum / sum;
            if (pct > max) {
                max = pct;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct - max;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
    }
}

