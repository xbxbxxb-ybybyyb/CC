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

public class Saturn_t930_wd_jh_vol_bds
extends BaseFactor {
    public Saturn_t930_wd_jh_vol_bds(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_vol_bds"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<Long, MarketOrder> buyOrders = this.marketDataManager.getJhjjTradeBuyMap();
        double[] qty = buyOrders.values().stream().mapToDouble(MarketOrder::getQty).sorted().toArray();
        double median = MathUtil.calculateSortedMedian(qty);
        double tran1 = 0.0;
        double tran2 = 0.0;
        for (MarketOrder order : buyOrders.values()) {
            if (order.getQty() > median) {
                tran1 += order.getFillList().stream().filter(f -> f.getBuyNo() > f.getSellNo()).mapToDouble(Fill::getQty).sum();
                continue;
            }
            tran2 += order.getFillList().stream().filter(f -> f.getBuyNo() > f.getSellNo()).mapToDouble(Fill::getQty).sum();
        }
        double value = 0.95;
        if (tran1 + tran2 != 0.0) {
            value = tran1 / (tran1 + tran2);
        }
        this.updateValue(0, value);
    }
}

