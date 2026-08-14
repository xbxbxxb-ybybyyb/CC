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

public class Saturn_t931_wd_t1cs_big_bid_pct_d_mean
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_t1cs_big_bid_pct_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1cs_big_bid_pct_d_mean"};
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
        Map<String, Double> totalAmtMap = this.marketDataManager.getTotalLxjjAmtSum();
        double pctSum = 0.0;
        double pctCnt = 0.0;
        double currPct = Double.NaN;
        for (String stock : this.stockSet) {
            Double totalAmt;
            Map<Long, OrderInfo> buyMap = buyOrderLxjj.get(stock);
            double amtBuySum = 0.0;
            if (buyMap != null && !buyMap.isEmpty()) {
                for (OrderInfo orderInfo : buyMap.values()) {
                    if (!(orderInfo.getAmt() > 200000.0)) continue;
                    amtBuySum += orderInfo.getAmt().doubleValue();
                }
            }
            if ((totalAmt = totalAmtMap.get(stock)) == null || totalAmt == 0.0) continue;
            double pct = amtBuySum / totalAmt;
            pctSum += pct;
            pctCnt += 1.0;
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct / pctSum * pctCnt;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 1.0 : factorVal);
    }
}

