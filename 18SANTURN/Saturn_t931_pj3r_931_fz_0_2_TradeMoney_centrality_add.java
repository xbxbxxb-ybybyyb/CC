/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_pj3r_931_fz_0_2_TradeMoney_centrality_add
extends BaseFactor {
    public Saturn_t931_pj3r_931_fz_0_2_TradeMoney_centrality_add(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj3r_931_fz_0_2_TradeMoney_centrality_add"};
    }

    @Override
    public void calculate() {
        double factorValue = 1.0;
        double zTPrice = this.marketDataManager.getHighPrice();
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        if (fillList != null) {
            double firstZtTime = Double.NaN;
            for (Fill f : fillList) {
                if (f.getPrice() != zTPrice) continue;
                firstZtTime = f.getMdTime();
                break;
            }
            double finalFirstZtTime = firstZtTime;
            factorValue = this.cr_centrality(fillList.stream().map(Fill::getAmt).collect(Collectors.toList())) + this.cr_centrality(fillList.stream().filter(x -> (double)x.getMdTime() > finalFirstZtTime).map(Fill::getAmt).collect(Collectors.toList()));
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 1.0 : factorValue);
    }

    private double cr_centrality(List<Double> x) {
        ArrayList<Double> x_new = new ArrayList<Double>();
        for (double d : x) {
            if (Double.isNaN(d) || Double.isInfinite(d)) continue;
            x_new.add(d);
        }
        return x_new.stream().mapToDouble(e -> Math.pow(e, 2.0)).sum() / Math.pow(x_new.stream().mapToDouble(e -> e).sum(), 2.0);
    }
}

