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
import java.util.List;
import java.util.Map;

public class Saturn_t931_sss_t1m_1onehand10_diff
extends BaseFactor {
    private final Map<Long, Double> buyNoQtyList;
    private final Map<Long, Double> sellNoQtyList;
    private final Map<Long, Double> buyNoAmtList;
    private final Map<Long, Double> sellNoAmtList;

    public Saturn_t931_sss_t1m_1onehand10_diff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_1onehand10_diff"};
        this.buyNoQtyList = new HashMap<Long, Double>();
        this.sellNoQtyList = new HashMap<Long, Double>();
        this.buyNoAmtList = new HashMap<Long, Double>();
        this.sellNoAmtList = new HashMap<Long, Double>();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> lxjjFillList = this.marketDataManager.getLxjjFillList();
        for (Fill fill : lxjjFillList) {
            if (TimeUtil.DateToWKT(fill.getTimestamp()) <= 93000000L) continue;
            this.buyNoQtyList.merge(fill.getBuyNo(), fill.getQty(), Double::sum);
            this.sellNoQtyList.merge(fill.getSellNo(), fill.getQty(), Double::sum);
            this.buyNoAmtList.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
            this.sellNoAmtList.merge(fill.getSellNo(), fill.getAmt(), Double::sum);
        }
        double buy = 0.0;
        double sell = 0.0;
        for (long t : this.buyNoQtyList.keySet()) {
            if (!(this.buyNoQtyList.get(t) < 1001.0)) continue;
            buy += this.buyNoAmtList.get(t).doubleValue();
        }
        for (long t : this.sellNoQtyList.keySet()) {
            if (!(this.sellNoQtyList.get(t) < 1001.0)) continue;
            sell += this.sellNoAmtList.get(t).doubleValue();
        }
        double factorValue = buy - sell;
        this.updateValue(0, Double.isNaN(factorValue) ? 0.0 : factorValue);
    }
}

