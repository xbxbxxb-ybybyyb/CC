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

public class Saturn_t931_qyh_T1mtra_r_amt2pct_up_mid
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_r_amt2pct_up_mid(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_r_amt2pct_up_mid"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0).collect(Collectors.toList());
        double mv = this.marketDataManager.getPreClose() * this.marketDataManager.getFreeFloatCapital();
        double preclose = this.marketDataManager.getPreClose();
        HashMap<Long, Double> buy_no_map = new HashMap<Long, Double>();
        HashMap<Long, Double> buy_no_max_px_map = new HashMap<Long, Double>();
        HashMap<Long, Double> buy_no_min_px_map = new HashMap<Long, Double>();
        double total_amt = 0.0;
        for (Fill fill : fillList) {
            if (fill.getSide() != Trade.Side.Bid) continue;
            buy_no_map.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
            buy_no_max_px_map.merge(fill.getBuyNo(), fill.getPrice(), Double::max);
            buy_no_min_px_map.merge(fill.getBuyNo(), fill.getPrice(), Double::min);
        }
        double ret = 0.0;
        for (Long key : buy_no_map.keySet()) {
            double val = (Double)buy_no_map.get(key);
            if (!(val >= 50000.0) || !(val <= 200000.0)) continue;
            ret += ((Double)buy_no_max_px_map.get(key) - (Double)buy_no_min_px_map.get(key)) / preclose;
            total_amt += val;
        }
        double factorValue = 7.0;
        if (Math.abs(ret) < 0.001) {
            ret = 0.001;
        }
        if (Double.isNaN(factorValue = total_amt / ret / 100.0 / mv)) {
            factorValue = 7.0;
        }
        this.updateValue(0, factorValue);
    }
}

