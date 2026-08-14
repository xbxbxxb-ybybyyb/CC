/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.Ordering
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.Ordering;
import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_t1_big_um_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_big_um_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_big_um_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Ordering ordering = Ordering.from(Comparator.comparing(MarketOrder::getQty).thenComparing(MarketOrder::getNo));
        int length = Math.min(100, this.marketDataManager.getLxjjTradeBuyMap().size());
        List buyOrder = ordering.leastOf(this.marketDataManager.getLxjjTradeBuyMap().values(), length);
        double median = MathUtil.calcMedian(buyOrder.stream().mapToDouble(MarketOrder::getAmt).toArray());
        double sum = 0.0;
        double filterSum = 0.0;
        for (MarketOrder marketOrder : buyOrder) {
            if (marketOrder.getAmt() > median) {
                filterSum += marketOrder.getAmt().doubleValue();
            }
            sum += marketOrder.getAmt().doubleValue();
        }
        double value = filterSum / sum;
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.5 : value);
    }
}

