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
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_shift_sds
extends BaseFactor {
    public Saturn_t931_wd_t1_shift_sds(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_shift_sds"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.5;
        ArrayList<Double> tradeQty = new ArrayList<Double>();
        TreeMap<Long, MarketOrder> lxjjTradeSellMap = this.marketDataManager.getLxjjTradeSellMap();
        if (lxjjTradeSellMap != null) {
            for (MarketOrder order : lxjjTradeSellMap.values()) {
                tradeQty.add(order.getQty());
            }
        }
        double median = MathUtil.calculateSortedMedian(tradeQty.stream().sorted().collect(Collectors.toList()));
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        if (fillList != null) {
            ArrayList<Double> tradePriceList = new ArrayList<Double>();
            for (Fill fill : fillList) {
                if (lxjjTradeSellMap.get(fill.getSellNo()) == null || ((MarketOrder)lxjjTradeSellMap.get(fill.getSellNo())).getQty() > median) continue;
                tradePriceList.add(fill.getPrice());
            }
            double sum1 = 0.0;
            double sum2 = 0.0;
            for (int i = 1; i < tradePriceList.size(); ++i) {
                double delta = (Double)tradePriceList.get(i) - (Double)tradePriceList.get(i - 1);
                if (delta > 0.0) {
                    sum1 += delta;
                }
                sum2 += Math.abs(delta);
            }
            factorValue = sum1 / sum2;
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.5 : factorValue);
    }
}

