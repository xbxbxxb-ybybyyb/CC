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
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_sss_t1m_quickp2amtp_down
extends BaseFactor {
    private final Map<Integer, Double> priceCumAmtList;
    private final Map<Integer, Double> priceDiffList;
    private final Map<Integer, Double> priceList;

    public Saturn_t931_sss_t1m_quickp2amtp_down(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_quickp2amtp_down"};
        this.priceCumAmtList = new HashMap<Integer, Double>();
        this.priceDiffList = new HashMap<Integer, Double>();
        this.priceList = new HashMap<Integer, Double>();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double threshold = -this.marketDataManager.getPreClose().doubleValue() * 0.002 * (double)(this.marketDataManager.isStartsWith3() ? 2 : 1);
        double priceQuickDownSum = 0.0;
        double priceSum = 0.0;
        double lastPrice = 0.0;
        int cumNum = 0;
        for (Fill fill : this.marketDataManager.getFillList()) {
            if (!(fill.getPrice() > 0.0)) continue;
            if (TimeUtil.DateToWKT(fill.getTimestamp()) > 93000000L) {
                if (fill.getPrice() != lastPrice) {
                    ++cumNum;
                }
                this.priceDiffList.putIfAbsent(cumNum, fill.getPrice() - lastPrice);
                this.priceList.putIfAbsent(cumNum, fill.getPrice());
                this.priceCumAmtList.merge(cumNum, fill.getAmt(), Double::sum);
            }
            lastPrice = fill.getPrice();
        }
        for (Integer i : this.priceDiffList.keySet()) {
            double tmp = this.priceCumAmtList.get(i);
            if (this.priceDiffList.get(i) < threshold) {
                priceQuickDownSum += tmp;
            }
            priceSum += tmp;
        }
        double factorValue = priceQuickDownSum / priceSum;
        this.updateValue(0, Double.isNaN(factorValue) ? 0.0 : factorValue);
    }
}

