/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t931_pj3r_931_bin_2_3_corr
extends BaseFactor {
    public Saturn_t931_pj3r_931_bin_2_3_corr(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj3r_931_bin_2_3_corr"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> lxjjTradeBuyMap = this.marketDataManager.getLxjjTradeBuyMap();
        double factorValue = this.cr_corr(lxjjTradeBuyMap.values().stream().map(MarketOrder::getMaxPrice).collect(Collectors.toList()), lxjjTradeBuyMap.values().stream().map(e -> e.getFirstFillMdTime() - 9.3E7).collect(Collectors.toList()));
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }

    private double cr_corr(List<Double> x, List<Double> y) {
        ArrayList<Double> x_new = new ArrayList<Double>();
        ArrayList<Double> y_new = new ArrayList<Double>();
        for (int i = 0; i < x.size(); ++i) {
            if (Double.isInfinite(x.get(i)) || Double.isNaN(x.get(i)) || Double.isInfinite(y.get(i)) || Double.isNaN(y.get(i))) continue;
            x_new.add(x.get(i));
            y_new.add(y.get(i));
        }
        return Correlation.pearsonCorrelation(x_new, y_new);
    }
}

