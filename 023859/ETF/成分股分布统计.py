import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，适用于 Windows
rcParams['axes.unicode_minus'] = False
import IO
from xquant.funddata import FundData
fd = FundData()
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

OUTPUT_XLSX = 'ETF分布分析.xlsx'

def ensure_output_dir(path: str):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def save_chart(fig, filename: str):
    fig.tight_layout()
    fig.savefig(filename, dpi=160, bbox_inches="tight")
    plt.close(fig)

start_date, end_date = 20250826, 20250826

fund_set = fd.get_fund_set('20240826')
fund_df = []
for fund in fund_set:
    df = fd.get_fund_issuance_info(fund)
    fund_df.append(df)

fund_df = pd.concat(fund_df, axis=0)
fund_df.to_excel('/data/user/023859/ETF/基金基本信息.xlsx')

info = pd.read_hdf('/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
md = IO.read_data([start_date, end_date],columns=['close', 'amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['S_INFO_NAME'] = info['S_INFO_NAME']
# 流通股本
df_float_shares = IO.read_data([start_date, end_date], columns=['FLOAT_A_SHR_TODAY'], alt='/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
md['float_shares'] = df_float_shares['FLOAT_A_SHR_TODAY']
md['Circu_Mkt'] = (md['float_shares'] * md['close'])

# fund_df = pd.read_excel('/data/user/023859/ETF/基金基本信息.xlsx')
fund_df = fund_df[fund_df['INVESTYPE'] == 1]
fund_df = fund_df[~fund_df['CHINESENAME'].str.contains('上证综合|沪深300|上证50|中证500|中证800|中证1000|中证2000|国证2000|科创板50|科创板100|科创创业50|创业板|中证A500|MSCI|A50')] # 剔除宽基指数
etf_list = fund_df['WINDCODE'].tolist()
ChinaETFPchRedmMembers = s.get_factor_value('WIND_ChinaETFPchRedmMembers', S_INFO_WINDCODE=etf_list, TRADE_DT=['>='+str(start_date), '<='+str(end_date)])
ChinaETFPchRedmMembers = ChinaETFPchRedmMembers.merge(fund_df[['WINDCODE','SHORTNAME']], left_on='S_INFO_WINDCODE', right_on='WINDCODE', how='left')
ChinaETFPchRedmMembers = ChinaETFPchRedmMembers[ChinaETFPchRedmMembers['S_CON_WINDCODE'].str.endswith(('SH','SZ','BJ'))]
ChinaETFPchRedmMembers = pd.merge(ChinaETFPchRedmMembers, md.reset_index(), left_on='S_CON_WINDCODE',right_on='Ticker',how='left')

ChinaETFPchRedmMembers['equiv_value'] = ChinaETFPchRedmMembers['S_CON_STOCKNUMBER'] * ChinaETFPchRedmMembers['close']
ChinaETFPchRedmMembers['equiv_value'] = ChinaETFPchRedmMembers['equiv_value'].replace(0,np.nan)
ChinaETFPchRedmMembers['equiv_value'] = ChinaETFPchRedmMembers['equiv_value'].fillna(ChinaETFPchRedmMembers['F_INFO_CASUBAMOUNT']/(1+ChinaETFPchRedmMembers['F_INFO_CASUBPREMRA']/100))

denom = ChinaETFPchRedmMembers.groupby('S_INFO_WINDCODE', as_index=False)['equiv_value'].sum().rename(columns={'equiv_value':'denom'})
ChinaETFPchRedmMembers = ChinaETFPchRedmMembers.merge(denom, on=['S_INFO_WINDCODE'],how='left')
ChinaETFPchRedmMembers['weight'] = np.where(ChinaETFPchRedmMembers['denom']>0, ChinaETFPchRedmMembers['equiv_value']/ChinaETFPchRedmMembers['denom'], 0.0)
ChinaETFPchRedmMembers_Stocks = ChinaETFPchRedmMembers[(~ChinaETFPchRedmMembers['Ticker'].isna())]

print(len(ChinaETFPchRedmMembers_Stocks['S_INFO_WINDCODE'].unique()))
print(len(ChinaETFPchRedmMembers_Stocks['S_CON_WINDCODE'].unique()))

long_df = ChinaETFPchRedmMembers_Stocks[['S_INFO_WINDCODE','SHORTNAME','S_CON_WINDCODE','S_INFO_NAME','weight']].copy()
wide_df = ChinaETFPchRedmMembers_Stocks[['S_INFO_WINDCODE','SHORTNAME','S_CON_WINDCODE','S_INFO_NAME','weight']].copy()
wide_df = wide_df.pivot(index='S_CON_WINDCODE', columns='S_INFO_WINDCODE', values='weight')

from xquant.factordata import FactorData
s = FactorData()
stockPool1800 = list(set(s.hset('INDEX', '20250826', 'ZZ1000')['stock']) | set(s.hset('INDEX', '20250826', 'ZZ500')['stock']) | set(s.hset('INDEX', '20250826', 'HS300')['stock']))
tmp = wide_df[~wide_df.index.isin(stockPool1800)].sum().sort_values(ascending=False)
tmp=tmp[tmp>=0.2].reset_index(name='非ZZ1800及申赎现金权重')
tmp = tmp.merge(fund_df, left_on='S_INFO_WINDCODE', right_on='WINDCODE', how='left')

etf_sums = long_df.groupby('S_CON_WINDCODE')['weight'].sum() # 股票权重占比

# 市值分布
bins = [0, 5e6, 2e7, float('inf')]
labels = ["小盘(<500亿)", "中盘(500-2000亿)", "大盘(>2000亿)"]
# ChinaETFPchRedmMembers['Circu_Mkt_bucket'] = pd.cut(ChinaETFPchRedmMembers['Circu_Mkt'], bins=bins, labels=labels)
total_weight = ChinaETFPchRedmMembers_Stocks.groupby(['S_CON_WINDCODE','S_INFO_NAME'])['weight'].sum().reset_index()
total_weight['total_weight_norm'] = total_weight['weight'] / total_weight['weight'].sum()
mw = pd.merge(total_weight, md.drop(columns=['S_INFO_NAME']).reset_index(), left_on='S_CON_WINDCODE',right_on='Ticker',how='left')
mw["mktcap_bucket"] = pd.cut(mw["Circu_Mkt"], bins=bins, labels=labels, include_lowest=True)
md['mktcap_bucket'] = pd.cut(md['Circu_Mkt'], bins=bins, labels=labels, include_lowest=True)
md['weight'] = md['Circu_Mkt'] / md['Circu_Mkt'].sum()
# Distribution by bucket (sum of normalized weight)
mktcap_dist = mw.groupby("mktcap_bucket")["total_weight_norm"].sum().reset_index(name="weight_etf")
mktcap_dist_ = md.groupby('mktcap_bucket')['weight'].sum().reset_index(name='weight_mkt')
mktcap_dist['weight_mkt'] = mktcap_dist_['weight_mkt']

# 频次分布: 有多少ETF持有该股票
freq = long_df.groupby(['S_CON_WINDCODE','S_INFO_NAME'])['S_INFO_WINDCODE'].nunique().reset_index()
freq = freq.rename(columns={'S_INFO_WINDCODE':'freq_etf_count'})
freq_hist = freq['freq_etf_count'].value_counts().sort_index().reset_index()
freq_hist.columns = ["freq_etf_count", "num_stocks"]

# top_freq = freq.sort_values('freq_etf_count', ascending=False).head(20)

# 权重分布
# --- Weight distribution stats
weight_desc = total_weight["total_weight_norm"].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99]).to_frame(name="value")
weight_desc.index.name = "stat"

# --- Top tables
top_freq   = freq.sort_values("freq_etf_count", ascending=False).head(30)
top_weight = mw.sort_values("total_weight_norm", ascending=False)[["S_CON_WINDCODE","S_INFO_NAME","total_weight_norm","Circu_Mkt"]].head(30)

# Choose top rows / columns for heatmap to keep the plot readable
# Top stocks by total normalized weight, top ETFs by total weight (column sum)
row_order = total_weight.sort_values("total_weight_norm", ascending=False)["S_CON_WINDCODE"].head(30).tolist()
col_order = wide_df.sum(axis=0).sort_values(ascending=False).index.to_series().head(30).tolist() # 股票权重占比最大的30只ETF
heat = wide_df.loc[wide_df.index.intersection(row_order), wide_df.columns.intersection(col_order)]

# =========================
# ====== PLOTTING =========
# =========================

charts = {}

# 1) Market-cap bucket distribution (bar)
x = np.arange(len(mktcap_dist))
width = 0.35
fig1, ax = plt.subplots(figsize=(8, 5))
ax.bar(x-width/2, mktcap_dist['weight_etf'], width, label='ETF中的权重')
ax.bar(x+width/2, mktcap_dist['weight_mkt'], width, label='全市场中的权重')
ax.set_xticks(x)
ax.set_xticklabels(mktcap_dist['mktcap_bucket'])
ax.set_xlabel("市值分桶")
ax.set_ylabel("权重占比")
ax.set_title("成分股市值分布对比")
ax.legend()
plt.show()
charts["mktcap_distribution.png"] = fig1

# 2) Stock frequency histogram (bar)
fig2, ax2 = plt.subplots(figsize=(9, 5))
ax2.bar(freq_hist["freq_etf_count"], freq_hist["num_stocks"])
ax2.set_xlabel("出现于多少只ETF")
ax2.set_ylabel("股票数量")
ax2.set_title("股票被纳入ETF的次数分布")
plt.show()
charts["frequency_hist.png"] = fig2

# 3) Total weight per stock distribution (hist)
fig3 = plt.figure(figsize=(9, 5))
# Avoid zeros for log-scale optional; keep simple linear hist
plt.hist(total_weight["total_weight_norm"].replace([np.inf, -np.inf], np.nan).dropna(), bins=50)
plt.title("股票权重分布")
plt.xlabel("权重")
plt.ylabel("股票数量")
plt.show()
charts["weight_hist.png"] = fig3

# 4) Heatmap of subset (imshow)
# if heat.shape[0] > 0 and heat.shape[1] > 0:
#     fig4 = plt.figure(figsize=(max(8, heat.shape[1]*0.35), max(6, heat.shape[0]*0.35)))
#     plt.imshow(heat.values, aspect="auto")
#     plt.colorbar()
#     plt.title(f"权重热力图（Top30股票 × Top30 ETF）")
#     plt.yticks(ticks=np.arange(len(heat.index)), labels=heat.index, fontsize=8)
#     plt.xticks(ticks=np.arange(len(heat.columns)), labels=heat.columns, rotation=90, fontsize=8)
#     charts["heatmap.png"] = fig4

# Save charts
ensure_output_dir(OUTPUT_XLSX)
for fname, fig in charts.items():
    save_chart(fig, fname)

# ====== SAVE EXCEL =======
# =========================
with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
    # Core tables
    mktcap_dist.to_excel(writer, sheet_name="成分股市值分布", index=False)
    freq.to_excel(writer, sheet_name="股票为其成分股的ETF个数", index=False)
    freq_hist.to_excel(writer, sheet_name="股票频数分布", index=False)
    total_weight.to_excel(writer, sheet_name="按股票在ETF中的权重分布", index=False)
    weight_desc.to_excel(writer, sheet_name="权重分布描述性统计")

    top_freq.to_excel(writer, sheet_name="频数最高的30只成分股", index=False)
    top_weight.to_excel(writer, sheet_name="权重最高的30只成分股", index=False)

    # Optionally write a small heatmap data sheet to inspect numbers
    # if heat.shape[0] > 0 and heat.shape[1] > 0:
    #     heat.to_excel(writer, sheet_name="heatmap_data")

    # Charts sheet: insert chart PNGs
    wb  = writer.book
    ws  = wb.add_worksheet("Charts")
    writer.sheets["Charts"] = ws

    row = 0
    for fname in ["mktcap_distribution.png", "frequency_hist.png", "weight_hist.png"]:
        if os.path.exists(fname):
            ws.insert_image(row, 0, fname, {"x_offset": 5, "y_offset": 5, "x_scale": 1.0, "y_scale": 1.0})
            row += 30  # move down for next image

print(f"Done. Wrote Excel to: {OUTPUT_XLSX}")
for f in charts.keys():
    if os.path.exists(f):
        print("Saved chart:", f)
