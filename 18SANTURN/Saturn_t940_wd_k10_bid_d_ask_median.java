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
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_bid_d_ask_median
extends BaseFactor {
    public Saturn_t940_wd_k10_bid_d_ask_median(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_bid_d_ask_median"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.6;
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (lxjjTickList != null) {
            ArrayList<Double> resList = new ArrayList<Double>();
            for (Tick tick : lxjjTickList) {
                if (tick.getTotalBidQty() == 0.0 || tick.getTotalOfferQty() == 0.0) continue;
                resList.add(tick.getTotalBidQty() / tick.getTotalOfferQty());
            }
            double mddian = MathUtil.calculateSortedMedian(MathUtil.sort(resList));
            if (!Double.isNaN(mddian)) {
                value = mddian;
            }
        }
        this.updateValue(0, value);
    }
}

