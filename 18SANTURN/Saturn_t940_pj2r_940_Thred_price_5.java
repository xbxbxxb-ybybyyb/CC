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

public class Saturn_t940_pj2r_940_Thred_price_5
extends BaseFactor {
    private final Map<Double, Double> priceQtyMap;

    public Saturn_t940_pj2r_940_Thred_price_5(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Thred_price_5"};
        this.updateMode = 2;
        this.priceQtyMap = new HashMap<Double, Double>();
    }

    @Override
    public void update(Fill fill) {
        this.priceQtyMap.merge(fill.getPrice(), fill.getQty(), Double::sum);
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getFillList().size() > 1) {
            double preClose = this.marketDataManager.getPreClose();
            double jhjjPx = this.marketDataManager.getFillList().size() == this.marketDataManager.getLxjjFillList().size() ? (this.marketDataManager.getFillList().size() != 0 ? this.marketDataManager.getFillList().get(0).getPrice() : preClose) : this.marketDataManager.getFillList().get(0).getPrice();
            double totQty = this.marketDataManager.getTotalQty();
            double qtyThred = totQty * 0.6;
            List priceQty = this.priceQtyMap.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
            List prices = this.priceQtyMap.keySet().stream().sorted().collect(Collectors.toList());
            double thredPx = 0.0;
            double preQty = 0.0;
            for (int i = 0; i < priceQty.size(); ++i) {
                if (!((preQty += ((Double)priceQty.get(i)).doubleValue()) >= qtyThred)) continue;
                thredPx = (Double)prices.get(i);
                break;
            }
            value = (thredPx - jhjjPx) / preClose * 100.0;
        }
        this.updateValue(0, value);
    }
}

