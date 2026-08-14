/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.scaler.BaseScaler;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public abstract class BaseFactor {
    protected final SaturnMarketDataManager marketDataManager;
    private final Map<String, Double> factorValueMap;
    private final Set<BaseScaler> scalerList = new HashSet<BaseScaler>();
    protected String[] factorName;
    protected int updateMode = 0;

    public BaseFactor(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        this.marketDataManager = marketDataManager;
        this.factorValueMap = factorValueMap;
    }

    public void update(Trade trade) {
    }

    public void update(Fill fill) {
    }

    public abstract void calculate();

    protected void updateValue(int index, double value) {
        this.factorValueMap.put(this.factorName[index], value);
        for (BaseScaler scaler : this.scalerList) {
            scaler.updateInput(this.factorName[index], value);
        }
    }

    public String[] getFactorName() {
        return this.factorName;
    }

    public int getUpdateMode() {
        return this.updateMode;
    }

    public void registerScaler(BaseScaler scaler) {
        for (String name : this.factorName) {
            if (!scaler.containsFactor(name)) continue;
            this.scalerList.add(scaler);
            scaler.updateCheck(name);
        }
    }
}

