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
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;

public class Saturn_t931_sss_t1m_1meanp_bs
extends BaseFactor {
    public Saturn_t931_sss_t1m_1meanp_bs(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_1meanp_bs"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        HashMap<Long, Double> buyOrderAmtMap = new HashMap<Long, Double>();
        HashMap<Long, Double> sellOrderAmtMap = new HashMap<Long, Double>();
        double amt = 0.0;
        for (Fill f : this.marketDataManager.getLxjjFillList()) {
            if (TimeUtil.DateToWKT(f.getTimestamp()) <= 93000000L) continue;
            buyOrderAmtMap.merge(f.getBuyNo(), f.getAmt(), Double::sum);
            sellOrderAmtMap.merge(f.getSellNo(), f.getAmt(), Double::sum);
            amt += f.getAmt().doubleValue();
        }
        double lxjjBuyOrderAmtMean = MathUtil.calculateMean(buyOrderAmtMap.values().stream().mapToDouble(e -> e).toArray());
        double lxjjSellOrderAmtMean = MathUtil.calculateMean(sellOrderAmtMap.values().stream().mapToDouble(e -> e).toArray());
        HashSet<Long> smallBuyOrder = new HashSet<Long>();
        HashSet<Long> smallSellOrder = new HashSet<Long>();
        Iterator iterator = buyOrderAmtMap.keySet().iterator();
        while (iterator.hasNext()) {
            long buyNo = (Long)iterator.next();
            if (!((Double)buyOrderAmtMap.get(buyNo) < lxjjBuyOrderAmtMean)) continue;
            smallBuyOrder.add(buyNo);
        }
        iterator = sellOrderAmtMap.keySet().iterator();
        while (iterator.hasNext()) {
            long sellNo = (Long)iterator.next();
            if (!((Double)sellOrderAmtMap.get(sellNo) < lxjjSellOrderAmtMean)) continue;
            smallSellOrder.add(sellNo);
        }
        double smallOrderTotalAmt = 0.0;
        for (Fill f : this.marketDataManager.getLxjjFillList()) {
            if (TimeUtil.DateToWKT(f.getTimestamp()) <= 93000000L || !smallBuyOrder.contains(f.getBuyNo()) && !smallSellOrder.contains(f.getSellNo())) continue;
            smallOrderTotalAmt += f.getAmt().doubleValue();
        }
        double factorValue = smallOrderTotalAmt / amt;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }
}

