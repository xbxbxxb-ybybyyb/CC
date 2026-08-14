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

public class Saturn_t930_wd_jh_small_vol_rate_pct
extends BaseFactor {
    public Saturn_t930_wd_jh_small_vol_rate_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_small_vol_rate_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.1;
        Map<Long, MarketOrder> jhjjBuyOrderMap = this.marketDataManager.getJhjjTradeBuyMap();
        if (jhjjBuyOrderMap.size() > 0) {
            double bidQtyMedian = MathUtil.calcMedian(jhjjBuyOrderMap.values().stream().mapToDouble(MarketOrder::getQty).toArray());
            double smallVolSum = jhjjBuyOrderMap.values().stream().filter(order -> order.getQty() <= bidQtyMedian).mapToDouble(MarketOrder::getQty).sum();
            if (smallVolSum != 0.0) {
                factorValue = smallVolSum / this.marketDataManager.getJhjjTotalQty();
            }
        }
        this.updateValue(0, factorValue);
    }
}

