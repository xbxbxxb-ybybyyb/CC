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
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_nrise_vid_cor
extends BaseFactor {
    public Saturn_t931_wd_t1_nrise_vid_cor(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_nrise_vid_cor"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> fillList;
        double factorValue = 0.0;
        ArrayList<Long> riseOrderList = new ArrayList<Long>();
        TreeMap<Long, MarketOrder> lxjjTradeBuyMap = this.marketDataManager.getLxjjTradeBuyMap();
        if (lxjjTradeBuyMap != null) {
            for (Long orderNo : lxjjTradeBuyMap.keySet()) {
                if (((MarketOrder)lxjjTradeBuyMap.get(orderNo)).getMaxPrice() == ((MarketOrder)lxjjTradeBuyMap.get(orderNo)).getMinPrice()) continue;
                riseOrderList.add(orderNo);
            }
        }
        if ((fillList = this.marketDataManager.getLxjjFillList()) != null) {
            HashMap<Long, Double> amtMap = new HashMap<Long, Double>();
            HashMap<Long, Double> qtyMap = new HashMap<Long, Double>();
            for (Fill f : fillList) {
                if (riseOrderList.contains(f.getBuyNo())) continue;
                amtMap.merge(f.getSellNo(), f.getAmt(), Double::sum);
                qtyMap.merge(f.getSellNo(), f.getQty(), Double::sum);
            }
            ArrayList<Double> vwaps = new ArrayList<Double>();
            List tradeSellNo = amtMap.keySet().stream().sorted().collect(Collectors.toList());
            for (Long sellNo : tradeSellNo) {
                double vwap = (Double)amtMap.get(sellNo) / (Double)qtyMap.get(sellNo);
                vwaps.add(BigDecimal.valueOf(vwap).setScale(4, 4).doubleValue());
            }
            factorValue = Correlation.spearmanCorrelation(vwaps, tradeSellNo.stream().map(e -> 1.0 * (double)e.longValue()).collect(Collectors.toList()));
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }
}

