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

public class Saturn_t931_qyh_T1mtra_r_amt2pct_down_small_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_r_amt2pct_down_small_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_r_amt2pct_down_small_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0).collect(Collectors.toList());
        double mv = this.marketDataManager.getPreClose() * this.marketDataManager.getFreeFloatCapital();
        double preclose = this.marketDataManager.getPreClose();
        HashMap<Long, Double> sell_no_map = new HashMap<Long, Double>();
        HashMap<Long, Double> sell_no_min_px_map = new HashMap<Long, Double>();
        HashMap<Long, Double> sell_no_first_last_px_map = new HashMap<Long, Double>();
        double last_px = this.marketDataManager.getJhjjPrice();
        for (Fill fill : fillList) {
            if (fill.getSide() == Trade.Side.Offer) {
                sell_no_map.merge(fill.getSellNo(), fill.getAmt(), Double::sum);
                sell_no_min_px_map.merge(fill.getSellNo(), fill.getPrice(), Double::min);
                sell_no_first_last_px_map.putIfAbsent(fill.getSellNo(), last_px);
            }
            last_px = fill.getPrice();
        }
        double ret = 0.0;
        double down_sum = 0.0;
        boolean flag = false;
        for (Long key : sell_no_map.keySet()) {
            double val = (Double)sell_no_map.get(key);
            if (!(val < 50000.0)) continue;
            ret += ((Double)sell_no_min_px_map.get(key) - (Double)sell_no_first_last_px_map.get(key)) / preclose;
            down_sum += ((Double)sell_no_map.get(key)).doubleValue();
            flag = true;
        }
        double factorValue = -0.44;
        if (flag) {
            if (Math.abs(ret) < 0.001) {
                ret = 0.001;
            }
            factorValue = down_sum / ret / 100.0 / mv;
        }
        if (Double.isNaN(factorValue)) {
            factorValue = -0.44;
        }
        this.updateValue(0, factorValue);
    }
}

