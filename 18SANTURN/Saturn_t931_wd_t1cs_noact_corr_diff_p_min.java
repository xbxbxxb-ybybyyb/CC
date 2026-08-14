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
import com.huatai.strategy.strong.util.Correlation;
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Saturn_t931_wd_t1cs_noact_corr_diff_p_min
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_t1cs_noact_corr_diff_p_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1cs_noact_corr_diff_p_min"};
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
        LocalTime localTime = LocalTime.of(9, 30);
        double currCorr = Double.NaN;
        double min = Double.POSITIVE_INFINITY;
        for (String stock : this.stockSet) {
            TreeMap<Long, Long> timeMap = new TreeMap<Long, Long>();
            ArrayList<Trade> tradeList = new ArrayList<Trade>();
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (!(trade.getPrice() > 0.0) || TimeUtil.UDateToLocalTime(trade.getTimestamp()).isBefore(localTime)) continue;
                long positive = 0L;
                long negative = 0L;
                if (trade.getTradeBuyNo() > trade.getTradeSellNo()) {
                    positive = trade.getTradeBuyNo();
                    negative = trade.getTradeSellNo();
                } else {
                    positive = trade.getTradeSellNo();
                    negative = trade.getTradeBuyNo();
                }
                if (!timeMap.containsKey(positive)) {
                    timeMap.put(positive, TimeUtil.DateToWKT(trade.getTimestamp()));
                }
                if (!timeMap.containsKey(negative)) {
                    timeMap.put(negative, 0L);
                }
                tradeList.add(trade);
            }
            if (timeMap.isEmpty()) continue;
            long time = 93000000L;
            for (Map.Entry entry : timeMap.entrySet()) {
                if ((Long)entry.getValue() == 0L) {
                    entry.setValue(time);
                    continue;
                }
                time = (Long)entry.getValue();
            }
            ArrayList<Double> diff = new ArrayList<Double>();
            ArrayList<Double> arrayList = new ArrayList<Double>();
            for (Trade trade : tradeList) {
                if (trade.getTradeBuyNo() >= trade.getTradeSellNo()) continue;
                diff.add((double)((Long)timeMap.get(trade.getTradeBuyNo())).longValue() - (double)((Long)timeMap.get(trade.getTradeSellNo())).longValue() * 1.0);
                arrayList.add(trade.getPrice());
            }
            double corr = Correlation.spearmanCorrelation(diff, arrayList);
            if (corr < min) {
                min = corr;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currCorr = corr;
        }
        double factorVal = currCorr / min;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? -0.45 : factorVal);
    }
}

