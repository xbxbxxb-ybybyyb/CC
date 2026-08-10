df = pd.read_pickle('/data/user/000072/share/for_wyc/plot.pkl')
import matplotlib.pyplot as plt

# 创建 figure 和两个 axes 对象，其中一个 axes 对象继承另一个，使得 x 轴是共用的，
# 另外一个的 y 轴和 color 设置不同，方便区分
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

# 绘制 y1 的曲线
df['LastPx'].plot(ax= ax1)
ax1.set_xlabel('x')
ax1.set_ylabel('LastPx')

# 绘制 y2 的曲线
df['qty'].plot(kind = 'bar',ax= ax2)
ax2.set_ylabel('qty')
interval = 20
plt.xticks(range(0, df.shape[0], interval), df.index[::interval], rotation = '60', fontsize = 21)
# 显示图形
plt.show()