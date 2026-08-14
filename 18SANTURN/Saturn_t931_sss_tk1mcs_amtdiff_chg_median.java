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
import java.util.Set;

public class Saturn_t931_sss_tk1mcs_amtdiff_chg_median
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_tk1mcs_amtdiff_chg_median(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1mcs_amtdiff_chg_median"};
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
        double currPct = Double.NaN;
        ArrayList<Double> pcts = new ArrayList<Double>();
        for (String stock : this.stockSet) {
            double pct;
            List tickList = this.marketDataManager.getTickListMap().get((Object)stock);
            if (tickList == null || tickList.isEmpty()) continue;
            double s = Double.NaN;
            for (Tick first : tickList) {
                if (first.getMdTime() < 92500000L || first.getLastPx() == 0.0 || !(first.getTotalBidQty() > 0.0) || !(first.getWeightedAvgBidPx() > 0.0) || !(first.getTotalOfferQty() > 0.0) || !(first.getWeightedAvgOfferPx() > 0.0)) continue;
                s = first.getTotalBidQty() * first.getWeightedAvgBidPx() - first.getTotalOfferQty() * first.getWeightedAvgOfferPx();
                break;
            }
            double e = Double.NaN;
            for (int i = tickList.size() - 1; i >= 0; --i) {
                Tick last = (Tick)tickList.get(i);
                if (last.getMdTime() < 92500000L || last.getLastPx() == 0.0 || !(last.getTotalBidQty() > 0.0) || !(last.getWeightedAvgBidPx() > 0.0) || !(last.getTotalOfferQty() > 0.0) || !(last.getWeightedAvgOfferPx() > 0.0)) continue;
                e = last.getTotalBidQty() * last.getWeightedAvgBidPx() - last.getTotalOfferQty() * last.getWeightedAvgOfferPx();
                break;
            }
            if (Double.isNaN(pct = e - s)) continue;
            pcts.add(pct);
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currPct = pct;
        }
        double factorVal = currPct - MathUtil.calcMedian(pcts.stream().mapToDouble(x -> x).toArray());
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
    }
}

