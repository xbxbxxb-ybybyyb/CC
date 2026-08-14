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

public class Saturn_t931_qyh_T1mtra_initiative_buy_big
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_initiative_buy_big(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_initiative_buy_big"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0 && a.getSide() != Trade.Side.Unknown).collect(Collectors.toList());
        HashMap<Long, Double> buy_no_map = new HashMap<Long, Double>();
        HashMap<Long, Double> buy_ini_no_map = new HashMap<Long, Double>();
        for (Fill fill : fillList) {
            buy_no_map.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
            if (fill.getSide() != Trade.Side.Bid) continue;
            buy_ini_no_map.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
        }
        double buy_big = 0.0;
        double buy_big_ini = 0.0;
        for (Long key : buy_no_map.keySet()) {
            double val = (Double)buy_no_map.get(key);
            if (!(val > 200000.0)) continue;
            buy_big += ((Double)buy_no_map.get(key)).doubleValue();
            Double val2 = (Double)buy_ini_no_map.get(key);
            if (val2 == null) continue;
            buy_big_ini += val2.doubleValue();
        }
        double factorValue = 0.55;
        if (buy_big > 100.0) {
            factorValue = buy_big_ini / buy_big;
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.55;
        }
        this.updateValue(0, factorValue);
    }
}

