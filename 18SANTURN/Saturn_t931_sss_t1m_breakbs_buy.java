/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1m_breakbs_buy
extends BaseFactor {
    public Saturn_t931_sss_t1m_breakbs_buy(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_breakbs_buy"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        HashMap buyno_price_map = new HashMap();
        ArrayList<Fill> actBuyTradeList = new ArrayList<Fill>();
        for (Fill fill : this.marketDataManager.getLxjjFillList()) {
            if (TimeUtil.DateToWKT(fill.getTimestamp()) <= 93000000L || fill.getBuyNo() <= fill.getSellNo()) continue;
            if (!buyno_price_map.containsKey(fill.getBuyNo())) {
                buyno_price_map.put(fill.getBuyNo(), new HashSet());
            }
            ((Set)buyno_price_map.get(fill.getBuyNo())).add(fill.getPrice());
            actBuyTradeList.add(fill);
        }
        ArrayList<Long> buynobreakList = new ArrayList<Long>();
        for (Long buyno : buyno_price_map.keySet()) {
            if (((Set)buyno_price_map.get(buyno)).size() <= 1) continue;
            buynobreakList.add(buyno);
        }
        HashSet<Long> hashSet = new HashSet<Long>();
        HashSet<Long> tradeBuyNoSet = new HashSet<Long>();
        for (Fill fill : actBuyTradeList) {
            if (!buynobreakList.contains(fill.getBuyNo())) continue;
            hashSet.add(fill.getSellNo());
            tradeBuyNoSet.add(fill.getBuyNo());
        }
        double factorValue = 1.0 * (double)(hashSet.size() + 1) / (double)(tradeBuyNoSet.size() + 1);
        this.updateValue(0, Double.isNaN(factorValue) ? 0.0 : factorValue);
    }
}

