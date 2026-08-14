/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.OrderInfo;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_t1cs_umv_weight_t_d_min
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_t1cs_umv_weight_t_d_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1cs_umv_weight_t_d_min"};
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
        Map<String, Map<Long, OrderInfo>> buyOrderLxjj = this.marketDataManager.getBuyOrderLxjj();
        double currPct = Double.NaN;
        double min = Double.POSITIVE_INFINITY;
        for (String stock : this.stockSet) {
            Map<Long, OrderInfo> orderMap = buyOrderLxjj.get(stock);
            if (orderMap == null || orderMap.isEmpty()) continue;
            double median = MathUtil.calcMedian(orderMap.values().stream().mapToDouble(OrderInfo::getVwap).toArray());
            double vwapSum = 0.0;
            double timeVwapSum = 0.0;
            for (OrderInfo orderInfo : orderMap.values()) {
                double vwap = orderInfo.getVwap();
                if (!(vwap > median)) continue;
                vwapSum += vwap;
                timeVwapSum += (double)orderInfo.getStartTime().longValue() * vwap;
            }
            double pct = timeVwapSum / vwapSum;
            if (pct < min) {
                min = pct;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct / min;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 1.0002 : factorVal);
    }
}

