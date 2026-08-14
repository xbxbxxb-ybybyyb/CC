/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t940_pj2r_940_Distance_to_vwap_qty_weighted_sum_v2_abs
extends BaseFactor {
    private final Map<Long, Double> qty_walk;
    private final Map<Long, Double> amt_walk;

    public Saturn_t940_pj2r_940_Distance_to_vwap_qty_weighted_sum_v2_abs(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Distance_to_vwap_qty_weighted_sum_v2_abs"};
        this.updateMode = 2;
        this.qty_walk = new HashMap<Long, Double>();
        this.amt_walk = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L) {
            this.qty_walk.merge(mdTime, fill.getQty(), Double::sum);
            this.amt_walk.merge(mdTime, fill.getAmt(), Double::sum);
        }
    }

    @Override
    public void calculate() {
        double preClose = this.marketDataManager.getPreClose();
        List qty_walk_list = this.qty_walk.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
        List amt_walk_list = this.amt_walk.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
        double pre_qty = 0.0;
        double pre_amt = 0.0;
        double vwap_qty_weighted_sum = 0.0;
        for (int i = 0; i < qty_walk_list.size(); ++i) {
            vwap_qty_weighted_sum += (Double)qty_walk_list.get(i) * ((Double)amt_walk_list.get(i) / (Double)qty_walk_list.get(i) / preClose - 1.0 - ((pre_amt += ((Double)amt_walk_list.get(i)).doubleValue()) / (pre_qty += ((Double)qty_walk_list.get(i)).doubleValue()) / preClose - 1.0));
        }
        double value = qty_walk_list.size() <= 2 ? 0.0 : vwap_qty_weighted_sum / this.marketDataManager.getLxjjTotalQty();
        this.updateValue(0, value);
    }
}

