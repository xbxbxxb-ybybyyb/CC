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
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_cst1_bid_1dt_d_mean
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_cst1_bid_1dt_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cst1_bid_1dt_d_mean"};
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
        Map<String, Double> amtMap = this.marketDataManager.getTotalLxjjAmtSum();
        double currPct = Double.NaN;
        double totalPct = 0.0;
        double cnt = 0.0;
        for (String stock : this.stockSet) {
            Map<Long, OrderInfo> orderMap = buyOrderLxjj.get(stock);
            if (orderMap == null || orderMap.size() < 2) continue;
            int length = orderMap.size() / 2;
            int i = 0;
            double amtSum = 0.0;
            for (OrderInfo orderInfo : orderMap.values()) {
                if (i >= length) break;
                amtSum += orderInfo.getAmt().doubleValue();
                ++i;
            }
            double pct = amtSum / (double)i / amtMap.get(stock);
            totalPct += pct;
            cnt += 1.0;
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct / totalPct * cnt;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.25 : factorVal);
    }
}

