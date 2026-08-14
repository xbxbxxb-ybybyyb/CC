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
import java.util.List;
import java.util.Map;

public class Saturn_t930_wd_jtcs_small_ask_amt_rank
extends BaseFactor {
    public Saturn_t930_wd_jtcs_small_ask_amt_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_small_ask_amt_rank"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<String, Map<Long, Double>> sellSum = this.marketDataManager.getSellOrderJhjjAmtSum();
        int index = -1;
        ArrayList<Double> amtList = new ArrayList<Double>(sellSum.size());
        for (Map.Entry<String, Map<Long, Double>> entry : sellSum.entrySet()) {
            double totalAmt = 0.0;
            for (Double val : entry.getValue().values()) {
                if (!(val <= 100000.0)) continue;
                totalAmt += val.doubleValue();
            }
            amtList.add(totalAmt);
            if (!entry.getKey().equals(this.marketDataManager.getSymbol())) continue;
            index = amtList.size() - 1;
        }
        double factorVal = 0.0;
        if (index != -1) {
            List<Double> ranks = MathUtil.calcRankData(amtList, true);
            factorVal = ranks.get(index);
        }
        this.updateValue(0, factorVal);
    }
}

