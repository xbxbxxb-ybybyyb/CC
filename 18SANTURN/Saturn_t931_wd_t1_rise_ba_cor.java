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
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_rise_ba_cor
extends BaseFactor {
    public Saturn_t931_wd_t1_rise_ba_cor(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_rise_ba_cor"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> fillList;
        double factorValue = 0.8;
        ArrayList<Long> riseOrderList = new ArrayList<Long>();
        TreeMap<Long, MarketOrder> lxjjTradeBuyMap = this.marketDataManager.getLxjjTradeBuyMap();
        if (lxjjTradeBuyMap != null) {
            for (Long orderNo : lxjjTradeBuyMap.keySet()) {
                if (((MarketOrder)lxjjTradeBuyMap.get(orderNo)).getMaxPrice() == ((MarketOrder)lxjjTradeBuyMap.get(orderNo)).getMinPrice()) continue;
                riseOrderList.add(orderNo);
            }
        }
        if ((fillList = this.marketDataManager.getLxjjFillList()) != null) {
            ArrayList<Double> tradeBuyNoList = new ArrayList<Double>();
            ArrayList<Double> tradeSellNoList = new ArrayList<Double>();
            for (Fill f : fillList) {
                if (!riseOrderList.contains(f.getBuyNo())) continue;
                tradeBuyNoList.add(1.0 * (double)f.getBuyNo());
                tradeSellNoList.add(1.0 * (double)f.getSellNo());
            }
            factorValue = Correlation.spearmanCorrelation(tradeBuyNoList, tradeSellNoList);
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.8 : factorValue);
    }
}

