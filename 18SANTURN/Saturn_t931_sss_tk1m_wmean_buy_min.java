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

public class Saturn_t931_sss_tk1m_wmean_buy_min
extends BaseFactor {
    public Saturn_t931_sss_tk1m_wmean_buy_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_wmean_buy_min"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        double preClose = this.marketDataManager.getPreClose();
        double factorValue = 0.0;
        factorValue = this.marketDataManager.isStartsWith3() ? tickList.stream().filter(tick -> tick.getWeightedAvgBidPx() > 0.0).mapToDouble(tick -> Math.log((tick.getWeightedAvgBidPx() / preClose - 1.0) / 2.0 + 1.0)).min().orElse(0.0) * 100.0 : tickList.stream().filter(tick -> tick.getWeightedAvgBidPx() > 0.0).mapToDouble(tick -> Math.log(tick.getWeightedAvgBidPx() / preClose)).min().orElse(0.0) * 100.0;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }
}

