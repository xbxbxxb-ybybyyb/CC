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
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_t1cs_small_rate_d_q10
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_t1cs_small_rate_d_q10(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1cs_small_rate_d_q10"};
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
        ArrayList<Double> pcts = new ArrayList<Double>();
        for (String stock : this.stockSet) {
            Map<Long, OrderInfo> orderMap = buyOrderLxjj.get(stock);
            if (orderMap == null || orderMap.isEmpty()) continue;
            double amtSum = 0.0;
            double filterSum = 0.0;
            for (OrderInfo orderInfo : orderMap.values()) {
                if (orderInfo.getAmt() < 10000.0) {
                    filterSum += orderInfo.getAmt().doubleValue();
                }
                amtSum += orderInfo.getAmt().doubleValue();
            }
            if (amtSum != 0.0) {
                pcts.add(filterSum / amtSum);
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = filterSum / amtSum;
        }
        double factorVal = currPct / MathUtil.calcPercentile(pcts, 10.0);
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 2.0 : factorVal);
    }
}

