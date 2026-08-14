/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashSet;
import java.util.Map;

public class Saturn_t930_wd_jh_id_qty_bda
extends BaseFactor {
    public Saturn_t930_wd_jh_id_qty_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_id_qty_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.5;
        double[] sellNoArray = this.marketDataManager.getFillList().stream().mapToDouble(Fill::getSellNo).toArray();
        if (sellNoArray.length > 0) {
            double sellNoMedian = MathUtil.calcMedian(sellNoArray);
            HashSet<Long> buyNoSet = new HashSet<Long>();
            HashSet<Long> sellNoSet = new HashSet<Long>();
            for (Fill fill : this.marketDataManager.getFillList()) {
                if (!((double)fill.getBuyNo() > sellNoMedian)) continue;
                buyNoSet.add(fill.getBuyNo());
                sellNoSet.add(fill.getSellNo());
            }
            if (sellNoSet.size() > 0) {
                factorValue = (double)buyNoSet.size() / (double)sellNoSet.size();
            }
        }
        this.updateValue(0, factorValue);
    }
}

