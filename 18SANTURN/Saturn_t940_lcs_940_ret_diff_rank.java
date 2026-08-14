/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

public class Saturn_t940_lcs_940_ret_diff_rank
extends BaseFactor {
    public Saturn_t940_lcs_940_ret_diff_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_lcs_940_ret_diff_rank"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getSaturnAfterNotUlLenMap().containsKey(this.marketDataManager.getSymbol()) && this.marketDataManager.getSaturnAfterNotUlLenMap().get(this.marketDataManager.getSymbol()) > 10) {
            HashSet<String> filteredStocks = new HashSet<String>();
            for (String symbol : this.marketDataManager.getSaturnStockSet()) {
                if (this.marketDataManager.getSaturnAfterNotUlLenMap().get(symbol) <= 10) continue;
                filteredStocks.add(symbol);
            }
            double currentRetDiff = 0.0;
            ArrayList<Double> retDiff = new ArrayList<Double>();
            for (String s : filteredStocks) {
                List tickList = this.marketDataManager.getTickListMap().get((Object)s);
                if (null == tickList || tickList.isEmpty()) continue;
                Tick tickLast = (Tick)tickList.get(tickList.size() - 1);
                Tick tickOpen = (Tick)tickList.get(tickList.size() - 1);
                for (Tick t : tickList) {
                    if (t.getMdTime() < 92500000L || t.getLastPx() == 0.0) continue;
                    tickOpen = t;
                    break;
                }
                double csRetDif = (tickLast.getLastPx() - tickOpen.getLastPx()) / this.marketDataManager.getLastTickMap().get(s).getPreviousClosingPx();
                retDiff.add(csRetDif);
                if (!s.equals(this.marketDataManager.getSymbol())) continue;
                currentRetDiff = csRetDif;
            }
            value = 1.0 * (double)(MathUtil.findDownIdx(retDiff, currentRetDiff).size() + 1 + MathUtil.findDownEqualIdx(retDiff, currentRetDiff).size()) / 2.0 / (double)filteredStocks.size();
        }
        this.updateValue(0, value);
    }
}

