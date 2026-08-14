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
import java.util.Map;

public class Saturn_t940_pj2_lxjj_price_volatility
extends BaseFactor {
    private Map<Long, Double> normalTradesZfWalk;

    public Saturn_t940_pj2_lxjj_price_volatility(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2_lxjj_price_volatility"};
        this.updateMode = 1;
        this.normalTradesZfWalk = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            if (this.normalTradesZfWalk.get(mdTime) == null) {
                this.normalTradesZfWalk.put(mdTime, fill.getPrice());
            } else if (this.normalTradesZfWalk.get(mdTime) < fill.getPrice()) {
                this.normalTradesZfWalk.put(mdTime, fill.getPrice());
            }
        }
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.normalTradesZfWalk.size() > 0) {
            double preClose = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            ArrayList<Double> normalTradesZfWalkList = new ArrayList<Double>();
            for (Double px : this.normalTradesZfWalk.values()) {
                normalTradesZfWalkList.add((px / preClose - 1.0) * 100.0);
            }
            value = MathUtil.calculateStd(normalTradesZfWalkList);
        }
        this.updateValue(0, value);
    }
}

