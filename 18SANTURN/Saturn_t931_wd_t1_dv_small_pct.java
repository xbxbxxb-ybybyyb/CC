/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_dv_small_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_dv_small_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_dv_small_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.04;
        double median = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
        double total = 0.0;
        double filter = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (!(marketOrder.getVwap() < median)) continue;
            total += marketOrder.getAmt().doubleValue();
            if (!(marketOrder.getAmt() < 10000.0 & marketOrder.getSideSet().contains(Trade.Side.Bid))) continue;
            filter += marketOrder.getAmt().doubleValue();
        }
        if (total != 0.0) {
            value = filter / total;
        }
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.04;
        }
        this.updateValue(0, value);
    }
}

