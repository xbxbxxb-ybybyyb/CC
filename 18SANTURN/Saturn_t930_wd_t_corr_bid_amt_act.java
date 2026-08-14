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
import com.huatai.strategy.strong.util.Correlation;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t930_wd_t_corr_bid_amt_act
extends BaseFactor {
    public Saturn_t930_wd_t_corr_bid_amt_act(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_t_corr_bid_amt_act"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, Double> orderAmtMap = new TreeMap<Long, Double>();
        TreeMap<Long, Double> orderActMap = new TreeMap<Long, Double>();
        for (Fill fill : this.marketDataManager.getFillList()) {
            double act = fill.getBuyNo() > fill.getSellNo() ? 1.0 : 0.0;
            orderAmtMap.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
            orderActMap.merge(fill.getBuyNo(), act, Double::max);
        }
        double value = 0.0;
        if (orderAmtMap.size() > 5) {
            value = Correlation.spearmanCorrelation(orderAmtMap.values().stream().map(x -> BigDecimal.valueOf(x).setScale(3, RoundingMode.HALF_UP).doubleValue()).collect(Collectors.toList()), orderActMap.values().stream().collect(Collectors.toList()));
        }
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0;
        }
        this.updateValue(0, value);
    }
}

