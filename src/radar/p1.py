import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# --- 参数设置 ---
fc = 450e6          # P波段载频 450MHz
fs = 2e9            # 采样率 2GHz (为了看清450MHz波形)
tau = 2e-6          # 脉宽 2us
pri = 10e-6         # 脉冲重复间隔 10us (为了绘图清晰，缩短了PRI)
n_pulses = 3        # 仿真3个脉冲
t_total = n_pulses * pri
t = np.arange(0, t_total, 1/fs)

# --- 产生脉冲串信号 ---
# 逻辑：只有在 n*PRI < t < n*PRI + tau 时信号才不为0
s_t = np.zeros_like(t)
for n in range(n_pulses):
    idx = (t >= n*pri) & (t < n*pri + tau)
    s_t[idx] = np.cos(2*np.pi*fc*t[idx])

# --- 正交解调 ---
lo_i = np.cos(2*np.pi*fc*t)
lo_q = -np.sin(2*np.pi*fc*t)

# 混频 (包含脉冲和空隙)
mixed_i = s_t * lo_i
mixed_q = s_t * lo_q

# 低通滤波提取基带 (设计一个截止频率远小于fc的滤波器)
def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter(order, cutoff / (0.5 * fs), btype='low')
    return lfilter(b, a, data)

# 截止频率设为 50MHz，足以通过单频脉冲的频谱
baseband_i = lowpass_filter(mixed_i, 50e6, fs)
baseband_q = lowpass_filter(mixed_q, 50e6, fs)

# --- 绘图 ---
plt.figure(figsize=(12, 8))

# 1. 射频脉冲串 (放大看前两个脉冲)
plt.subplot(3, 1, 1)
plt.plot(t * 1e6, s_t, color='blue')
plt.title("RF Pulse Train (P-Band, 450MHz)")
plt.ylabel("Amplitude")
plt.grid(True)

# 2. 解调后的 I 路 (基带)
plt.subplot(3, 1, 2)
plt.plot(t * 1e6, baseband_i, color='red', label='I Channel')
plt.plot(t * 1e6, baseband_q, color='green', linestyle='--', label='Q Channel')
plt.title("Demodulated I/Q Baseband Signal")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

# 3. 频谱对比 (展示能量集中在fc处和下变频到0处)
plt.subplot(3, 1, 3)
freqs = np.fft.fftfreq(len(t), 1/fs)
S_f = np.abs(np.fft.fft(s_t))
I_f = np.abs(np.fft.fft(baseband_i))
plt.plot(freqs[:len(freqs)//2] * 1e-6, S_f[:len(freqs)//2], label='RF Spectrum')
plt.plot(freqs[:len(freqs)//2] * 1e-6, I_f[:len(freqs)//2], label='Baseband I Spectrum')
plt.xlim(0, 600) # 只看 0-600MHz
plt.title("Spectrum Comparison (MHz)")
plt.xlabel("Frequency (MHz)")
plt.legend()
plt.tight_layout()
plt.show()
