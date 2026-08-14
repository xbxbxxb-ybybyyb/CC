from tensorboard.backend.event_processing import event_accumulator
import csv
import matplotlib.pyplot as plt

# 加载 TensorBoard 日志文件
ea = event_accumulator.EventAccumulator("/data/user/000021/gjx/alphagen-high时序也用filter版本/path/for/tb/log/new_100_2_20240827010313_1")
ea.Reload()

# 获取所有标量数据的标签
tags = ea.Tags()['scalars']

# 定义需要提取的标量数据标签
tags = [
    'train/entropy_loss',
    'train/policy_gradient_loss',
    'train/value_loss',
    'train/approx_kl',
    'train/clip_fraction',
    'train/loss',
    'train/explained_variance',
    'train/clip_range'
]

# 提取所有需要的标量数据
data = {tag: ea.Scalars(tag) for tag in tags}

# # 将数据保存到 CSV 文件
# with open('output.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     # 写入表头
#     headers = ['step'] + tags
#     writer.writerow(headers)
#
#     # 获取所有步骤
#     steps = sorted(set(entry.step for entries in data.values() for entry in entries))
#
#     # 写入数据
#     for step in steps:
#         row = [step]
#         for tag in tags:
#             entry = next((e for e in data[tag] if e.step == step), None)
#             row.append(entry.value if entry else None)
#         writer.writerow(row)


# 绘制每个标量数据的图表
for tag in tags:
    steps = [entry.step for entry in data[tag]]
    values = [entry.value for entry in data[tag]]

    plt.figure()
    plt.plot(steps, values)
    plt.title(tag)
    plt.xlabel('Step')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig(f"{tag.replace('/', '_')}.png")  # 保存图表为 PNG 文件
    plt.show()