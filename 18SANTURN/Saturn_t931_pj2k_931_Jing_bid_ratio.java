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
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_pj2k_931_Jing_bid_ratio
extends BaseFactor {
    public Saturn_t931_pj2k_931_Jing_bid_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_Jing_bid_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double totalVolumeTradeMax;
        double value = 0.5;
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        if (tickList != null && tickList.size() > 1 && (totalVolumeTradeMax = this.marketDataManager.getLastQuote().getTotalVolume().doubleValue()) != 0.0) {
            double sum = IntStream.range(1, tickList.size()).mapToDouble(i -> ((Tick)tickList.get(i)).getTotalBidQty() - ((Tick)tickList.get(i - 1)).getTotalBidQty()).sum();
            if ((sum += tickList.get(0).getTotalBidQty() + totalVolumeTradeMax) != 0.0 && (value = Math.log(sum / totalVolumeTradeMax)) == 0.0) {
                value = 0.5;
            }
        }
        this.updateValue(0, value);
    }
}

