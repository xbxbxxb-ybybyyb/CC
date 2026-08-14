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
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t930_wd_jtcs_big_bda_d_mean
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t930_wd_jtcs_big_bda_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_big_bda_d_mean"};
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
        Map<String, Map<Long, Double>> sellSum = this.marketDataManager.getSellOrderJhjjAmtSum();
        Map<String, Map<Long, Double>> buySum = this.marketDataManager.getBuyOrderJhjjAmtSum();
        double bdsSum = 0.0;
        double bdsCnt = 0.0;
        double currBds = 0.0;
        for (String stock : this.stockSet) {
            double totalBuyAmt = 0.0;
            Map<Long, Double> valMap = buySum.get(stock);
            if (valMap != null) {
                for (Double val : valMap.values()) {
                    if (!(val > 100000.0)) continue;
                    totalBuyAmt += val.doubleValue();
                }
            }
            double totalSellAmt = 0.0;
            Map<Long, Double> sellMap = sellSum.get(stock);
            if (sellMap != null) {
                for (Double val : sellMap.values()) {
                    if (!(val > 100000.0)) continue;
                    totalSellAmt += val.doubleValue();
                }
            }
            if (totalSellAmt != 0.0) {
                bdsSum += totalBuyAmt / totalSellAmt;
                bdsCnt += 1.0;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currBds = totalBuyAmt / totalSellAmt;
        }
        this.updateValue(0, bdsSum != 0.0 ? currBds / bdsSum * bdsCnt : 1.0);
    }
}

