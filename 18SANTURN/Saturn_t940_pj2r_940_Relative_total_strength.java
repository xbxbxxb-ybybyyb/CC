/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t940_pj2r_940_Relative_total_strength
extends BaseFactor {
    private final Map<Long, Double> tsQty = new HashMap<Long, Double>();
    private final Map<Long, Double> tsPrice = new HashMap<Long, Double>();

    public Saturn_t940_pj2r_940_Relative_total_strength(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_940_Relative_total_strength"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            this.tsQty.merge(mdTime, fill.getQty(), Double::sum);
            this.tsPrice.put(mdTime, fill.getPrice());
        }
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            List TradeQty = this.tsQty.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
            double jhjj_price = this.marketDataManager.getJhjjPrice();
            if (this.marketDataManager.getFillList().size() == this.marketDataManager.getLxjjFillList().size()) {
                jhjj_price = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            }
            double prePx = jhjj_price;
            List TradePrice = this.tsPrice.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
            double totalQty = this.marketDataManager.getTotalQty();
            ArrayList<Double> arr = new ArrayList<Double>();
            for (int i = 0; i < TradeQty.size(); ++i) {
                arr.add((Double)TradeQty.get(i) * 100.0 * ((Double)TradePrice.get(i) - prePx) / this.marketDataManager.getLastQuote().getPreviousClosingPx());
                prePx = (Double)TradePrice.get(i);
            }
            if (totalQty != 0.0) {
                value = MathUtil.calculateSum(arr) / totalQty;
            }
        }
        this.updateValue(0, value);
    }
}

