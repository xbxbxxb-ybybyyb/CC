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
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1mcs_movepct_minp_rank_and_qmovep2pctp_diff_max
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_t1mcs_movepct_minp_rank_and_qmovep2pctp_diff_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1mcs_movepct_minp_rank", "saturn_t931_sss_t1mcs_qmovep2pctp_diff_max"};
        for (Map.Entry<String, Integer> entry : marketDataManager.getSaturnAfterNotUlLenMap().entrySet()) {
            if (entry.getValue() <= 10) continue;
            this.stockSet.add(entry.getKey());
        }
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        LocalTime localTime = LocalTime.of(9, 30);
        int index = -1;
        ArrayList<Double> pcts = new ArrayList<Double>();
        double currFactor = Double.NaN;
        double max = Double.NEGATIVE_INFINITY;
        for (String stock : this.stockSet) {
            HashMap<Integer, Double> diff = new HashMap<Integer, Double>();
            TradeInfo now = null;
            double lastPrice = Double.NaN;
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (trade.getTurnover() > 0.0 && TimeUtil.UDateToLocalTime(trade.getTimestamp()).isAfter(localTime)) {
                    TradeInfo nowTrade;
                    now = nowTrade = new TradeInfo(now, trade, lastPrice);
                    diff.merge(nowTrade.priceCnt, nowTrade.diff, Double::sum);
                }
                if (!(trade.getTurnover() > 0.0)) continue;
                lastPrice = trade.getPrice();
            }
            if (diff.isEmpty()) continue;
            double preClose = this.marketDataManager.getPreClosePxMap().get(stock);
            double last = Double.NaN;
            double diff_sum = 0.0;
            double min = Double.POSITIVE_INFINITY;
            double thr = preClose * 0.002 * (double)(stock.startsWith("3") ? 2 : 1);
            double move_quick_up = 0.0;
            double move_quick_down = 0.0;
            for (Double val : diff.values()) {
                if (val * last < 0.0) {
                    if (diff_sum < min) {
                        min = diff_sum;
                    }
                    if (diff_sum > thr) {
                        move_quick_up += Math.abs(diff_sum);
                    } else if (diff_sum < -thr) {
                        move_quick_down += Math.abs(diff_sum);
                    }
                    diff_sum = val;
                } else {
                    diff_sum += val.doubleValue();
                }
                last = val;
            }
            if (diff_sum < min) {
                min = diff_sum;
            }
            if (diff_sum > thr) {
                move_quick_up += Math.abs(diff_sum);
            } else if (diff_sum < -thr) {
                move_quick_down += Math.abs(diff_sum);
            }
            double pct = min / preClose;
            pcts.add(pct);
            double factor = (move_quick_up - move_quick_down) / preClose;
            if (stock.startsWith("3")) {
                factor /= 2.0;
            }
            if (factor > max) {
                max = factor;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            index = pcts.size() - 1;
            currFactor = factor;
        }
        double factorVal = 0.0;
        List<Double> ranks = MathUtil.calcRankData(pcts, true);
        if (index != -1) {
            factorVal = ranks.get(index) - 0.5;
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
        double factorVal2 = currFactor - max;
        this.updateValue(1, Double.isNaN(factorVal2) || Double.isInfinite(factorVal2) ? 0.0 : factorVal2);
    }

    class TradeInfo {
        public double price;
        public double diff;
        public int priceCnt;

        public TradeInfo(TradeInfo tradeInfo, Trade trade, double lastPrice) {
            if (tradeInfo == null) {
                this.diff = trade.getPrice() - lastPrice;
                this.priceCnt = this.diff == 0.0 ? 0 : 1;
                this.price = trade.getPrice();
            } else {
                this.diff = trade.getPrice() - tradeInfo.price;
                this.priceCnt = this.diff == 0.0 ? tradeInfo.priceCnt : tradeInfo.priceCnt + 1;
                this.price = trade.getPrice();
            }
        }
    }
}

