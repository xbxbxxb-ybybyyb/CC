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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_pj3r_931_pa_0_1_TradeMoney_mean_mult
extends BaseFactor {
    private final List<Double> totNormalTradeMoneyList;
    private final List<Double> totPassTradeMoneyList;

    public Saturn_t931_pj3r_931_pa_0_1_TradeMoney_mean_mult(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj3r_931_pa_0_1_TradeMoney_mean_mult"};
        this.updateMode = 1;
        this.totNormalTradeMoneyList = new ArrayList<Double>();
        this.totPassTradeMoneyList = new ArrayList<Double>();
    }

    @Override
    public void update(Fill fill) {
        this.totNormalTradeMoneyList.add(fill.getAmt());
        if (fill.getSide() == Trade.Side.Bid) {
            this.totPassTradeMoneyList.add(fill.getAmt());
        }
    }

    @Override
    public void calculate() {
        double factorValue = this.cr_mean(this.totNormalTradeMoneyList) * this.cr_mean(this.totPassTradeMoneyList);
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }

    private double cr_mean(List<Double> x) {
        ArrayList<Double> x_new = new ArrayList<Double>();
        for (double d : x) {
            if (Double.isNaN(d) || Double.isInfinite(d)) continue;
            x_new.add(d);
        }
        return MathUtil.calcNaNMean(x_new);
    }
}

