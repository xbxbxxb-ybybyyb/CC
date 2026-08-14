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

public class Saturn_t940_pj2r_940_AP_mean_diff
extends BaseFactor {
    private final List<Double> activeNoRatio;
    private final List<Double> passiveNoRatio;

    public Saturn_t940_pj2r_940_AP_mean_diff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_AP_mean_diff"};
        this.updateMode = 1;
        this.activeNoRatio = new ArrayList<Double>();
        this.passiveNoRatio = new ArrayList<Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            if (fill.getSide() == Trade.Side.Bid) {
                this.activeNoRatio.add(1.0 * (double)fill.getSellNo() / (double)fill.getBuyNo());
            } else {
                this.passiveNoRatio.add(1.0 * (double)fill.getBuyNo() / (double)fill.getSellNo());
            }
        }
    }

    @Override
    public void calculate() {
        double activeNoRatioMean = this.activeNoRatio.size() != 0 ? MathUtil.calculateMean(this.activeNoRatio) : 1.0;
        double passiveNoRatioMean = this.passiveNoRatio.size() != 0 ? MathUtil.calculateMean(this.passiveNoRatio) : 1.0;
        double apMeanDiff = activeNoRatioMean - passiveNoRatioMean;
        this.updateValue(0, apMeanDiff);
    }
}

