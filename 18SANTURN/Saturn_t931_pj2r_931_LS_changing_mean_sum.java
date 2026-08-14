/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

public class Saturn_t931_pj2r_931_LS_changing_mean_sum
extends BaseFactor {
    public Saturn_t931_pj2r_931_LS_changing_mean_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_LS_changing_mean_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.005;
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        if (fillList.size() > 0) {
            ArrayList<Double> shortToLongTradesShort = new ArrayList<Double>(fillList.size());
            ArrayList<Double> shortToLongTradesLong = new ArrayList<Double>(fillList.size());
            ArrayList<Double> longToShortTradesLong = new ArrayList<Double>(fillList.size());
            ArrayList<Double> longToShortTradesShort = new ArrayList<Double>(fillList.size());
            for (int i2 = 0; i2 < fillList.size(); ++i2) {
                Fill fill = fillList.get(i2);
                if (i2 + 1 < fillList.size()) {
                    Fill nextFill = fillList.get(i2 + 1);
                    if (fill.getSide() == Trade.Side.Offer) {
                        if (nextFill.getSide() == Trade.Side.Bid) {
                            shortToLongTradesShort.add(fill.getPrice());
                        }
                    } else if (nextFill.getSide() == Trade.Side.Offer) {
                        longToShortTradesLong.add(fill.getPrice());
                    }
                }
                if (i2 - 1 < 0) continue;
                Fill preFill = fillList.get(i2 - 1);
                if (fill.getSide() == Trade.Side.Bid) {
                    if (preFill.getSide() != Trade.Side.Offer) continue;
                    shortToLongTradesLong.add(fill.getPrice());
                    continue;
                }
                if (preFill.getSide() != Trade.Side.Bid) continue;
                longToShortTradesShort.add(fill.getPrice());
            }
            double shortToLongPriceMean = IntStream.range(0, shortToLongTradesLong.size()).mapToDouble(i -> (Double)shortToLongTradesLong.get(i) - (Double)shortToLongTradesShort.get(i)).average().orElse(Double.NaN) / this.marketDataManager.getPreClose();
            double longToShortPriceMean = IntStream.range(0, longToShortTradesLong.size()).mapToDouble(i -> (Double)longToShortTradesLong.get(i) - (Double)longToShortTradesShort.get(i)).average().orElse(Double.NaN) / this.marketDataManager.getPreClose();
            value = shortToLongPriceMean + longToShortPriceMean;
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.005 : value);
    }
}

