/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_pj2k_931_sb_10_wish_mean
extends BaseFactor {
    public Saturn_t931_pj2k_931_sb_10_wish_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_sb_10_wish_mean"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue;
        ArrayList<Double> wishDiff = new ArrayList<Double>();
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        if (tickList != null) {
            for (int i = 0; i < tickList.size(); ++i) {
                double sellQtySum;
                Tick tick = tickList.get(i);
                double vol = i == 0 ? tick.getTotalVolumeTrade() - this.marketDataManager.getJhjjTotalQty() : tick.getTotalVolumeTrade() - tickList.get(i - 1).getTotalVolumeTrade();
                List<QtyPrice> bids = tick.getBuyQtyPrice();
                List<QtyPrice> asks = tick.getSellQtyPrice();
                double buyQtySum = IntStream.range(0, 10).mapToDouble(x -> ((QtyPrice)bids.get(x)).getQuantity()).sum();
                double diff = vol / buyQtySum - vol / (sellQtySum = IntStream.range(0, 10).mapToDouble(x -> ((QtyPrice)asks.get(x)).getQuantity()).sum());
                if (Double.isNaN(diff) || Double.isInfinite(diff)) {
                    diff = 0.0;
                }
                wishDiff.add(diff);
            }
        }
        this.updateValue(0, Double.isNaN(factorValue = MathUtil.calculateMean(wishDiff)) ? 0.0 : factorValue);
    }
}

