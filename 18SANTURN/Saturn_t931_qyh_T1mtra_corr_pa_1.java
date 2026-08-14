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
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_qyh_T1mtra_corr_pa_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_corr_pa_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_corr_pa_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0 && a.getSide() != Trade.Side.Unknown).collect(Collectors.toList());
        HashMap<Double, Double> price_amt_map = new HashMap<Double, Double>();
        for (Fill fill : fillList) {
            price_amt_map.merge(fill.getPrice(), fill.getAmt(), Double::sum);
        }
        ArrayList<Double> priceList = new ArrayList<Double>();
        ArrayList<Double> amtList = new ArrayList<Double>();
        for (Double key : price_amt_map.keySet()) {
            priceList.add(key);
            amtList.add((Double)price_amt_map.get(key));
        }
        double factorValue = Correlation.pearsonCorrelation(priceList, amtList);
        if (Double.isNaN(factorValue)) {
            factorValue = 0.0;
        }
        this.updateValue(0, factorValue);
    }
}

