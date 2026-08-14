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
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_sss_t1m_each_mean_down
extends BaseFactor {
    public Saturn_t931_sss_t1m_each_mean_down(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_each_mean_down"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, TradeInfo> tradeInfoMap = new TreeMap<Long, TradeInfo>();
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        for (Fill fill : fillList) {
            long flag = fill.getSide().value();
            long tradeNo = fill.getBuyNo() * (2L - flag) + fill.getSellNo() * (flag - 1L);
            if (tradeInfoMap.containsKey(tradeNo)) {
                ((TradeInfo)tradeInfoMap.get(tradeNo)).update(fill);
                continue;
            }
            tradeInfoMap.put(tradeNo, new TradeInfo(fill));
        }
        double preClose = this.marketDataManager.getPreClose();
        double sum = 0.0;
        double cnt = 0.0;
        double lastPrice = this.marketDataManager.getOpenPxMap().getOrDefault(this.marketDataManager.getSymbol(), 0.0);
        for (Map.Entry entry : tradeInfoMap.entrySet()) {
            TradeInfo tradeInfo = (TradeInfo)entry.getValue();
            if (tradeInfo.getFlagMean() == 2) {
                sum += Math.max(tradeInfo.priceMax, lastPrice) - tradeInfo.priceMin;
                cnt += 1.0;
            }
            lastPrice = tradeInfo.priceLast;
        }
        double factorVal = sum / cnt / preClose;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
    }

    class TradeInfo {
        int flagSum;
        double priceMax;
        double priceMin;
        double priceLast;
        int cnt;

        public TradeInfo(Fill fill) {
            this.flagSum = fill.getSide().value();
            this.priceMax = fill.getPrice();
            this.priceMin = fill.getPrice();
            this.priceLast = fill.getPrice();
            this.cnt = 1;
        }

        public void update(Fill fill) {
            this.flagSum += fill.getSide().value();
            this.priceMax = Math.max(this.priceMax, fill.getPrice());
            this.priceMin = Math.min(this.priceMin, fill.getPrice());
            this.priceLast = fill.getPrice();
            ++this.cnt;
        }

        public int getFlagMean() {
            return this.flagSum / this.cnt;
        }
    }
}

