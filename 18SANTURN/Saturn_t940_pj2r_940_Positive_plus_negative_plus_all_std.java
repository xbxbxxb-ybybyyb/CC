/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_pj2r_940_Positive_plus_negative_plus_all_std
extends BaseFactor {
    private final List<Double> priceChangeList;
    private double lastPx;
    private long currentMdTime;
    private double currentPx;
    private boolean hasJhjjPx;

    public Saturn_t940_pj2r_940_Positive_plus_negative_plus_all_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Positive_plus_negative_plus_all_std"};
        this.updateMode = 1;
        this.hasJhjjPx = false;
        this.lastPx = 0.0;
        this.currentMdTime = 0L;
        this.currentPx = 0.0;
        this.priceChangeList = new ArrayList<Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L) {
            if (!this.hasJhjjPx) {
                this.lastPx = this.marketDataManager.getJhjjPrice();
                this.currentMdTime = mdTime;
                this.currentPx = fill.getPrice();
                this.hasJhjjPx = true;
            } else {
                if (mdTime != this.currentMdTime) {
                    this.priceChangeList.add(this.currentPx - this.lastPx);
                    this.lastPx = this.currentPx;
                    this.currentMdTime = mdTime;
                }
                this.currentPx = fill.getPrice();
            }
        }
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            this.priceChangeList.add(this.currentPx - this.lastPx);
            double preClose = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            ArrayList<Double> downList = new ArrayList<Double>();
            ArrayList<Double> upList = new ArrayList<Double>();
            for (double pxChange : this.priceChangeList) {
                if (pxChange > 0.0) {
                    downList.add(pxChange);
                    continue;
                }
                if (!(pxChange < 0.0)) continue;
                upList.add(pxChange);
            }
            value = (MathUtil.calculateStd(downList) + MathUtil.calculateStd(upList) + MathUtil.calculateStd(this.priceChangeList)) / preClose;
            if (Double.isNaN(value) || Double.isInfinite(value)) {
                value = 0.1;
            }
        }
        this.updateValue(0, value);
    }
}

