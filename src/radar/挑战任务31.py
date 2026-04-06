import numpy as np
import matplotlib.pyplot as plt

# --- 参数设置 ---
c = 3e8                 # 光速
fc = 10e9               # 载频 10GHz
lam = c / fc            # 波长
d = lam / 2             # 阵元间距
N = 4                   # 接收阵元数
fs = 1e6                # 采样率

# --- 目标设定 ---
target_dist = 100       # 目标距离 (米)
target_angle = 20       # 目标角度 (度)
snr = 20                # 信噪比 (dB)

# --- 1. 产生回波信号 ---
theta_rad = np.deg2rad(target_angle)
# 导向矢量 (Steering Vector)
ant_idx = np.arange(N)
steering_vector = np.exp(1j * 2 * np.pi * d / lam * ant_idx * np.sin(theta_rad))

# 模拟接收信号 (简化为单频信号 + 高斯白噪声)
# 实际工程中会经过下变频处理，这里直接模拟复包络
noise = (np.random.randn(N) + 1j * np.random.randn(N)) / np.sqrt(2)
noise_pwr = 10**(-snr/10)
signal = steering_vector + np.sqrt(noise_pwr) * noise

# --- 2. 测角算法 ---

# A. FFT 测角 (空间频谱)
n_fft = 1024
spatial_fft = np.fft.fftshift(np.fft.fft(signal, n_fft))
freq_axis = np.linspace(-0.5, 0.5, n_fft)
# 将归一化频率映射回角度: sin(theta) = f_spatial * lambda / d
sin_theta_fft = freq_axis * (lam / d)
# 裁剪合理范围防止 arcsin 越界
sin_theta_fft = np.clip(sin_theta_fft, -1.0, 1.0)
angles_fft = np.rad2deg(np.arcsin(sin_theta_fft))
fft_result_angle = angles_fft[np.argmax(np.abs(spatial_fft))]

# B. 相位法测角 (干涉法)
# 利用相邻阵元的相位差平均值
phases = np.angle(signal)
delta_phi = np.diff(phases)
# 处理相位模糊 (wrap around)
delta_phi = (delta_phi + np.pi) % (2 * np.pi) - np.pi
mean_delta_phi = np.mean(delta_phi)
phase_method_angle = np.rad2deg(np.arcsin(mean_delta_phi / (2 * np.pi * d / lam)))

# --- 绘图 ---
plt.figure(figsize=(10, 5))
plt.plot(angles_fft, 20 * np.log10(np.abs(spatial_fft) / np.max(np.abs(spatial_fft))))
plt.axvline(target_angle, color='r', linestyle='--', label=f'True: {target_angle}°')
plt.axvline(fft_result_angle, color='g', linestyle=':', label=f'FFT: {fft_result_angle:.2f}°')
plt.title("Spatial FFT Spectrum")
plt.xlabel("Angle (deg)")
plt.ylabel("Magnitude (dB)")
plt.legend()
plt.grid(True)
plt.show()

print(f"设定目标角度: {target_angle}°")
print(f"FFT 测角结果: {fft_result_angle:.2f}°")
print(f"相位法测角结果: {phase_method_angle:.2f}°")
