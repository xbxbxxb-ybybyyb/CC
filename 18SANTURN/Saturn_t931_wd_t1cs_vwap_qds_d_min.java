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
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Saturn_t931_wd_t1cs_vwap_qds_d_min
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_t1cs_vwap_qds_d_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1cs_vwap_qds_d_min"};
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
        double currVal = Double.NaN;
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
            double qAmtSum = 0.0;
            double qQtySum = 0.0;
            double sAmtSum = 0.0;
            double sQtySum = 0.0;
            for (Trade trade : tradeList) {
                double diff = Math.abs((Long)timeMap.get(trade.getTradeBuyNo()) - (Long)timeMap.get(trade.getTradeSellNo()));
                if (diff > 10000.0) {
                    qAmtSum += trade.getTurnover().doubleValue();
                    qQtySum += trade.getQuantity().doubleValue();
                    continue;
                }
                sAmtSum += trade.getTurnover().doubleValue();
                sQtySum += trade.getQuantity().doubleValue();
            }
            double vwap_q = qAmtSum / qQtySum;
            double vwap_s = sAmtSum / sQtySum;
            double value = vwap_q / vwap_s;
            if (stock.startsWith("3")) {
                double preClose = this.marketDataManager.getPreClosePxMap().get(stock);
                value = ((vwap_q / preClose - 1.0) / 2.0 + 1.0) / ((vwap_s / preClose - 1.0) / 2.0 + 1.0);
            }
            if (value < min) {
                min = value;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currVal = value;
        }
        double factorVal = currVal / min;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 1.01 : factorVal);
    }
}

