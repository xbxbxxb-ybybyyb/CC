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
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_biga_qty_ms_density
extends BaseFactor {
    public Saturn_t931_wd_t1_biga_qty_ms_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_biga_qty_ms_density"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> lxjjSellOrderMap = this.marketDataManager.getLxjjTradeSellMap();
        double[] qtyArray = lxjjSellOrderMap.values().stream().mapToDouble(MarketOrder::getQty).sorted().toArray();
        double median = MathUtil.calculateSortedMedian(qtyArray);
        double totalQty = 0.0;
        HashMap secondQtySum = new HashMap();
        for (MarketOrder sellOrder : lxjjSellOrderMap.values()) {
            if (!(sellOrder.getQty() > median)) continue;
            sellOrder.getFillList().forEach(fill -> secondQtySum.merge((int)(fill.getMdTime() % 1000L) / 100, fill.getQty(), Double::sum));
            totalQty += sellOrder.getQty().doubleValue();
        }
        double finalTotalQty = totalQty;
        double max = secondQtySum.isEmpty() ? 0.2 : secondQtySum.values().stream().mapToDouble(qty -> qty / finalTotalQty).max().orElse(0.2);
        this.updateValue(0, max);
    }
}

