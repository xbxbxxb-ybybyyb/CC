/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.Ordering
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.Ordering;
import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.OrderInfo;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_cst1_big_money_pct
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_cst1_big_money_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cst1_big_money_pct"};
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
        Map<String, Map<Long, OrderInfo>> buyOrders = this.marketDataManager.getBuyOrderLxjj();
        double currPct = Double.NaN;
        double max = Double.NEGATIVE_INFINITY;
        for (String stock : this.stockSet) {
            Map<Long, OrderInfo> orderMap = buyOrders.get(stock);
            if (orderMap == null || orderMap.isEmpty()) continue;
            double median = MathUtil.calcMedian(orderMap.values().stream().mapToDouble(OrderInfo::getQty).toArray());
            ArrayList<Double> amts = new ArrayList<Double>();
            double sum = 0.0;
            for (OrderInfo orderInfo : orderMap.values()) {
                if (!(orderInfo.getQty() > median)) continue;
                double amt = orderInfo.getAmt();
                amts.add(amt);
                sum += amt;
            }
            int limit = (int)Math.ceil(0.2 * (double)amts.size());
            if (limit == 0) continue;
            Ordering ordering = Ordering.from(Double::compareTo);
            double filterSum = ordering.greatestOf(amts, limit).stream().mapToDouble(x -> x).sum();
            double pct = filterSum / sum;
            if (pct > max && sum != 0.0) {
                max = pct;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct / max;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.7 : factorVal);
    }
}

