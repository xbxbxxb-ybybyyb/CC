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
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t930_wd_jtcs_act_qty_d_mean
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t930_wd_jtcs_act_qty_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_act_qty_d_mean"};
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
        HashMap<String, Double> buySum = new HashMap<String, Double>();
        for (String stock : this.stockSet) {
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (!(trade.getPrice() > 0.0) || trade.getTradeBuyNo() <= trade.getTradeSellNo()) continue;
                buySum.merge(trade.getSymbol(), trade.getQuantity(), Double::sum);
            }
        }
        Map<String, Double> totalSum = this.marketDataManager.getTotalJhjjQtySum();
        double totalPct = 0.0;
        double currSumPct = 0.0;
        for (Map.Entry entry : buySum.entrySet()) {
            Double sum = totalSum.get(entry.getKey());
            if (sum == null || sum == 0.0) continue;
            double pct = (Double)entry.getValue() / sum;
            totalPct += pct;
            if (!((String)entry.getKey()).equals(this.marketDataManager.getSymbol())) continue;
            currSumPct = pct;
        }
        this.updateValue(0, totalPct != 0.0 ? currSumPct / totalPct * (double)this.stockSet.size() : 1.0);
    }
}

