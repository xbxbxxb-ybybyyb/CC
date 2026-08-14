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
import java.util.Map;

public class Saturn_t930_wd_jh_big_order_sum_bda
extends BaseFactor {
    public Saturn_t930_wd_jh_big_order_sum_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_big_order_sum_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sellQtySum;
        double buyQtySum = this.marketDataManager.getJhjjTradeBuyMap().values().stream().filter(x -> x.getAmt() > 50000.0).mapToDouble(MarketOrder::getQty).sum();
        double value = buyQtySum + (sellQtySum = this.marketDataManager.getJhjjTradeSellMap().values().stream().filter(x -> x.getAmt() > 50000.0).mapToDouble(MarketOrder::getQty).sum()) == 0.0 ? 1.0 : buyQtySum / (buyQtySum + sellQtySum);
        this.updateValue(0, value);
    }
}

