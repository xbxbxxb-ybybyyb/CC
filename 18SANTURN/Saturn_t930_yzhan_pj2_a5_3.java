/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 *  org.apache.commons.lang3.tuple.MutablePair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.tuple.MutablePair;

public class Saturn_t930_yzhan_pj2_a5_3
extends BaseFactor {
    private final List<Double> cumTradeQty2List;
    private double cumTradeQty2 = 0.0;

    public Saturn_t930_yzhan_pj2_a5_3(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_yzhan_pj2_a5_3"};
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
        double value = 0.0;
        List<Fill> fillList = this.marketDataManager.getFillList();
        if (fillList.size() > 0) {
            double totalAmt = this.marketDataManager.getTotalAmt();
            double lastValue = this.cumTradeQty2List.get(this.cumTradeQty2List.size() - 1);
            HashMap<Long, MutablePair> amtAdjMap = new HashMap<Long, MutablePair>();
            for (int i = this.cumTradeQty2List.size() - 1; i >= 0; --i) {
                MutablePair pair2;
                Fill fill = fillList.get(i);
                MutablePair mutablePair = pair2 = amtAdjMap.computeIfAbsent(fill.getBuyNo(), k -> MutablePair.of((Object)0.0, (Object)0.0));
                Double.valueOf((Double)mutablePair.left + fill.getAmt() / totalAmt);
                mutablePair.left = mutablePair.left;
                mutablePair = pair2;
                Double.valueOf((Double)mutablePair.right + 1.0);
                mutablePair.right = mutablePair.right;
                if (this.cumTradeQty2List.get(i) / lastValue < 0.5) break;
            }
            double[] meanList = amtAdjMap.values().stream().mapToDouble(pair -> (Double)pair.left / (Double)pair.right).toArray();
            value = MathUtil.calculateStd(meanList);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.0 : value);
    }
}

