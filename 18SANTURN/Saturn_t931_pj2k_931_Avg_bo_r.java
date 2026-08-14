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
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_pj2k_931_Avg_bo_r
extends BaseFactor {
    public Saturn_t931_pj2k_931_Avg_bo_r(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_Avg_bo_r"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        List<Tick> currentTick = this.marketDataManager.getCurrentLxjjTickList();
        if (currentTick != null) {
            value = currentTick.stream().map(tick -> {
                List<QtyPrice> bids = tick.getBuyQtyPrice();
                List<QtyPrice> asks = tick.getSellQtyPrice();
                Double buyQtySum = IntStream.range(0, 10).mapToDouble(i -> ((QtyPrice)bids.get(i)).getQuantity()).sum();
                Double sellQtySum = IntStream.range(0, 10).mapToDouble(i -> ((QtyPrice)asks.get(i)).getQuantity()).sum();
                return buyQtySum / sellQtySum;
            }).filter(r -> !r.isNaN() && !r.isInfinite()).mapToDouble(Double::doubleValue).average().orElse(1.0);
        }
        this.updateValue(0, value);
    }
}

