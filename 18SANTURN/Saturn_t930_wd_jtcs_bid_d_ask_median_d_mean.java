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
import java.util.Map;
import java.util.Set;

public class Saturn_t930_wd_jtcs_bid_d_ask_median_d_mean
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t930_wd_jtcs_bid_d_ask_median_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_bid_d_ask_median_d_mean"};
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
        double totalPct = 0.0;
        double pctCnt = 0.0;
        double currSumPct = Double.NaN;
        for (String symbol : this.stockSet) {
            double sell;
            HashMap<Long, Double> sellSum = new HashMap<Long, Double>();
            HashMap<Long, Double> buySum = new HashMap<Long, Double>();
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(symbol)) {
                if (!(trade.getPrice() > 0.0)) continue;
                sellSum.merge(trade.getTradeSellNo(), trade.getQuantity(), Double::sum);
                buySum.merge(trade.getTradeBuyNo(), trade.getQuantity(), Double::sum);
            }
            double buy = MathUtil.calcMedian(buySum.values().stream().mapToDouble(x -> x).toArray());
            double pct = buy / (sell = MathUtil.calcMedian(sellSum.values().stream().mapToDouble(x -> x).toArray()));
            if (Double.isNaN(pct)) continue;
            pctCnt += 1.0;
            totalPct += pct;
            if (!symbol.equals(this.marketDataManager.getSymbol())) continue;
            currSumPct = pct;
        }
        this.updateValue(0, totalPct == 0.0 || Double.isNaN(currSumPct) ? 0.04 : currSumPct / totalPct * pctCnt);
    }
}

