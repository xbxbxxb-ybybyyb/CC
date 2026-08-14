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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_qyh_T1mtra_cct_bs
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_cct_bs(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_cct_bs"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List fillList = this.marketDataManager.getLxjjFillList().stream().filter(a -> a.getPrice() > 0.0).collect(Collectors.toList());
        HashMap<Long, Double> buy_amt_map = new HashMap<Long, Double>();
        HashMap<Long, Double> sell_amt_map = new HashMap<Long, Double>();
        double buy_amt_sum = 0.0;
        double sell_amt_sum = 0.0;
        double total_amt = 0.0;
        for (Fill fill : fillList) {
            if (fill.getSide() == Trade.Side.Offer) {
                sell_amt_map.merge(fill.getSellNo(), fill.getAmt(), Double::sum);
                sell_amt_sum += fill.getAmt().doubleValue();
            } else if (fill.getSide() == Trade.Side.Bid) {
                buy_amt_map.merge(fill.getBuyNo(), fill.getAmt(), Double::sum);
                buy_amt_sum += fill.getAmt().doubleValue();
            }
            total_amt += fill.getAmt().doubleValue();
        }
        double factorValue = 0.0;
        if (Math.abs(total_amt) > 1.0) {
            double tm_buy = buy_amt_map.values().stream().mapToDouble(e -> Math.pow(e, 2.0)).sum();
            double tm_sell = sell_amt_map.values().stream().mapToDouble(e -> Math.pow(e, 2.0)).sum();
            factorValue = tm_buy / Math.pow(buy_amt_sum, 2.0) - tm_sell / Math.pow(sell_amt_sum, 2.0);
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.0;
        }
        this.updateValue(0, factorValue);
    }
}

