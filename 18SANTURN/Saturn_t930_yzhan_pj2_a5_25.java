/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.Correlation;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t930_yzhan_pj2_a5_25
extends BaseFactor {
    private final List<Double> cumTradeQty2List;
    private double cumTradeQty2 = 0.0;

    public Saturn_t930_yzhan_pj2_a5_25(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_yzhan_pj2_a5_25"};
        this.updateMode = 2;
        this.cumTradeQty2List = new ArrayList<Double>();
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() != Trade.Side.Bid) {
            this.cumTradeQty2 += fill.getQty().doubleValue();
        }
        this.cumTradeQty2List.add(this.cumTradeQty2);
    }

    @Override
    public void calculate() {
        double value;
        List<Fill> fillList = this.marketDataManager.getFillList();
        if (fillList.size() > 0) {
            double totalAmt = this.marketDataManager.getTotalAmt();
            double totalVol = this.marketDataManager.getTotalQty();
            double lastValue = this.cumTradeQty2List.get(this.cumTradeQty2List.size() - 1);
            ArrayList<Double> volList = new ArrayList<Double>();
            ArrayList<Double> amtList = new ArrayList<Double>();
            for (int i = fillList.size() - 1; i >= 0; --i) {
                Fill fill = fillList.get(i);
                volList.add(fill.getQty() / totalVol);
                amtList.add(fill.getAmt() / totalAmt);
                if (this.cumTradeQty2List.get(i) / lastValue < 0.5) break;
            }
            value = Correlation.calcNaNCov(volList, amtList);
        } else {
            value = 0.0;
        }
        this.updateValue(0, Double.isNaN(value) ? 0.0 : value);
    }
}

