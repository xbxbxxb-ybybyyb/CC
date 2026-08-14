/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_um_med_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_um_med_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_um_med_bda"};
        this.updateMode = 1;
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double m1 = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getQty).toArray());
        double m2 = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getQty).toArray());
        double b = Math.log(MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(e -> e.getQty() > m1).mapToDouble(MarketOrder::getAmt).toArray()));
        double a = Math.log(MathUtil.calcMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().filter(e -> e.getQty() > m2).mapToDouble(MarketOrder::getAmt).toArray()));
        double value = 0.49;
        if (a + b != 0.0) {
            value = b / (a + b);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.49 : value);
    }
}

