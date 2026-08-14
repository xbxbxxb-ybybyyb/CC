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
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1mcs_1peramtm_buy_min
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_t1mcs_1peramtm_buy_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1mcs_1peramtm_buy_min"};
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
        LocalTime time930 = LocalTime.of(9, 30);
        double currCorr = Double.NaN;
        double min = Double.POSITIVE_INFINITY;
        for (String stock : this.stockSet) {
            HashMap<Long, Double> buyMap = new HashMap<Long, Double>();
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (!(trade.getTurnover() > 0.0) || !TimeUtil.UDateToLocalTime(trade.getTimestamp()).isAfter(time930)) continue;
                buyMap.merge(trade.getTradeBuyNo(), trade.getTurnover(), Double::sum);
            }
            double median = Double.NaN;
            if (buyMap.isEmpty()) continue;
            median = MathUtil.calcMedian(buyMap.values().stream().mapToDouble(x -> x).toArray());
            if (median < min) {
                min = median;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currCorr = median;
        }
        double factorVal = currCorr - min;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
    }
}

