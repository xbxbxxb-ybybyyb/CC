/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t930_wd_jh_act_big_vol_rate
extends BaseFactor {
    public Saturn_t930_wd_jh_act_big_vol_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_act_big_vol_rate"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.5;
        Map<Long, MarketOrder> jhjjBuyOrderMap = this.marketDataManager.getJhjjTradeBuyMap();
        if (jhjjBuyOrderMap.size() > 0) {
            double bidQtyMedian = MathUtil.calcMedian(jhjjBuyOrderMap.values().stream().mapToDouble(MarketOrder::getQty).toArray());
            double activeBuyQtySum = 0.0;
            for (MarketOrder buyOrder : jhjjBuyOrderMap.values()) {
                if (!(buyOrder.getQty() > bidQtyMedian)) continue;
                activeBuyQtySum += buyOrder.getFillList().stream().filter(fill -> fill.getBuyNo() > fill.getSellNo()).mapToDouble(Fill::getQty).sum();
            }
            if (this.marketDataManager.getJhjjTotalQty() != 0.0) {
                factorValue = activeBuyQtySum / this.marketDataManager.getJhjjTotalQty();
            }
        }
        this.updateValue(0, factorValue);
    }
}

