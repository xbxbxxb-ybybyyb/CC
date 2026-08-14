/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Saturn_wd_lo_pct_p_ff
extends BaseFactor {
    private final String symbol;
    private final double preHalfHourTurnOverQtl;
    private final Set<String> preZTSymbols;

    public Saturn_wd_lo_pct_p_ff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.symbol = marketDataManager.getSymbol();
        this.preHalfHourTurnOverQtl = marketDataManager.getParams().getPreHalfHourTurnOverQtl();
        this.preZTSymbols = marketDataManager.getParams().getPreZTStockList();
        this.factorName = new String[]{"saturn_wd_lo_pct_p_ff"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        if (!this.preZTSymbols.contains(this.symbol)) {
            this.updateValue(0, 0.0);
            return;
        }
        TreeMap<Double, Double> ratioMap = new TreeMap<Double, Double>();
        for (String preZTSymbol : this.preZTSymbols) {
            Double ratio = this.marketDataManager.getOpenToPreCloseRatio(preZTSymbol);
            ratio = null == ratio ? 0.0 : ratio;
            ratioMap.merge(ratio, 1.0, Double::sum);
        }
        Double ratio = this.marketDataManager.getOpenToPreCloseRatio(this.symbol);
        Double count = (Double)ratioMap.get(ratio);
        double totalSize = this.preZTSymbols.size();
        double startIndex = ratioMap.subMap((Double)ratioMap.firstKey(), true, ratio, false).values().stream().mapToDouble(Double::doubleValue).sum();
        double value = (2.0 * startIndex + count + 1.0) / (2.0 * totalSize);
        double factorValue = value - this.preHalfHourTurnOverQtl;
        this.updateValue(0, factorValue);
    }
}

