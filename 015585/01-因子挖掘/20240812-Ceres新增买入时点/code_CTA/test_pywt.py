import pywt
import numpy as np
import matplotlib.pyplot as plt
# 生成原始信号
t = np.linspace(0, 1, 1000)
f = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)

# 生成噪声
np.random.seed(0)
noise = 0.5 * np.random.randn(len(t))

# 添加噪声到信号中
noisy_signal = f + noise
a = noisy_signal[:10]
b = noisy_signal[:20]
for noisy_signal in [a,b]:
    # 选择小波基和去噪级别
    wavelet = 'db4'
    level = 4
    # 对信号进行小波变换
    coeffs = pywt.wavedec(noisy_signal, wavelet, level=level)
    # 通过阈值处理细节系数
    threshold = np.median(np.abs(coeffs[-1])) / 0.6745
    coeffs = [pywt.threshold(coeff, threshold, mode='soft') for coeff in coeffs]
    denoised_signal = pywt.waverec(coeffs, wavelet)
    print(denoised_signal[:10])