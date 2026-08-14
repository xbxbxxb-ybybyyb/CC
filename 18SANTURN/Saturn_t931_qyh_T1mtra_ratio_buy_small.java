/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_qyh_T1mtra_ratio_buy_small
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_ratio_buy_small(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_ratio_buy_small"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0).collect(Collectors.toList());
        HashMap<Long, Double> buy_no_map = new HashMap<Long, Double>();
        double total_amt = 0.0;
        for (Fill fill : fillList) {
            if (fill.getSide() == Trade.Side.Bid) {
                buy_no_map.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
            }
            if (fill.getSide() == Trade.Side.Unknown) continue;
            total_amt += fill.getAmt().doubleValue();
        }
        double buy_small_amt = 0.0;
        for (Long key : buy_no_map.keySet()) {
            double val = (Double)buy_no_map.get(key);
            if (!(val <= 50000.0)) continue;
            buy_small_amt += val;
        }
        double factorValue = 0.2;
        if (Math.abs(total_amt) >= 0.001) {
            factorValue = buy_small_amt / total_amt;
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.2;
        }
        this.updateValue(0, factorValue);
    }
}

