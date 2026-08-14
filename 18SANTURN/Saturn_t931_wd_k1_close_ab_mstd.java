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
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_wd_k1_close_ab_mstd
extends BaseFactor {
    public Saturn_t931_wd_k1_close_ab_mstd(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_close_ab_mstd"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double closeAbStd;
        double factorValue = 1.2;
        List<Tick> tickList = this.marketDataManager.getLxjjTickList();
        List<Double> closeAbList = tickList.stream().filter(tick -> tick.getLastPx() > 0.0).map(tick -> {
            double buy1Price = tick.getBuyQtyPrice().get(0).getPrice();
            double sell1Price = tick.getSellQtyPrice().get(0).getPrice();
            return tick.getLastPx() - buy1Price > sell1Price - tick.getLastPx() ? 1.0 : 0.0;
        }).collect(Collectors.toList());
        if (closeAbList.size() > 3 && (closeAbStd = MathUtil.calculateStd(closeAbList)) != 0.0) {
            factorValue = MathUtil.calculateMean(closeAbList) / closeAbStd;
        }
        this.updateValue(0, factorValue);
    }
}

