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
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1mcs_peramt_sell_rank
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_t1mcs_peramt_sell_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1mcs_peramt_sell_rank"};
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
        int index = -1;
        ArrayList<Double> pcts = new ArrayList<Double>();
        for (String stock : this.stockSet) {
            HashSet<Long> sellNo = new HashSet<Long>();
            double amtSum = 0.0;
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (!(trade.getTurnover() > 0.0)) continue;
                amtSum += trade.getTurnover().doubleValue();
                sellNo.add(trade.getTradeSellNo());
            }
            if (sellNo.isEmpty()) continue;
            pcts.add(amtSum / (double)sellNo.size());
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            index = pcts.size() - 1;
        }
        double factorVal = 0.0;
        List<Double> ranks = MathUtil.calcRankData(pcts, true);
        if (index != -1) {
            factorVal = ranks.get(index) - 0.5;
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
    }
}

