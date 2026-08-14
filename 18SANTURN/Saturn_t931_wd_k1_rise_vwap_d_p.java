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

public class Saturn_t931_wd_k1_rise_vwap_d_p
extends BaseFactor {
    public Saturn_t931_wd_k1_rise_vwap_d_p(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_rise_vwap_d_p"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.9996;
        List<Tick> lxjjTickList = this.marketDataManager.getCurrentLxjjTickList();
        if (lxjjTickList != null) {
            value = IntStream.range(1, lxjjTickList.size()).mapToDouble(i -> {
                Tick tick = (Tick)lxjjTickList.get(i);
                Tick preTick = (Tick)lxjjTickList.get(i - 1);
                if (tick.getLastPx() >= preTick.getLastPx()) {
                    double vol = tick.getTotalVolumeTrade() - preTick.getTotalVolumeTrade();
                    return vol == 0.0 ? Double.NaN : (tick.getTotalValueTrade() - preTick.getTotalValueTrade()) / vol / tick.getLastPx();
                }
                return Double.NaN;
            }).filter(e -> !Double.isNaN(e)).average().orElse(0.9996);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.9996 : value);
    }
}

