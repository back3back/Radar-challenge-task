import numpy as np
import matplotlib.pyplot as plt

def dbf_algo(N, d_over_lambda, angles_true, snr, num_samples=1000):
    # 1. 模拟信号产生 (跟之前一样)
    theta = np.deg2rad(angles_true)
    # 导向矢量矩阵
    A = np.exp(-2j * np.pi * d_over_lambda * np.arange(N).reshape(-1, 1) @ np.sin(theta).reshape(1, -1))
    s = np.exp(1j * 2 * np.pi * np.random.rand(len(angles_true), num_samples))
    noise = (np.random.randn(N, num_samples) + 1j * np.random.randn(N, num_samples)) / np.sqrt(2)
    x = A @ s + np.sqrt(10**(-snr/10)) * noise

    # 2. DBF 核心：扫描所有角度，看哪个方向功率最大
    search_angles = np.linspace(-90, 90, 1800)
    P_dbf = []
    
    for a in search_angles:
        rad = np.deg2rad(a)
        # 构造对应角度 a 的“补偿矢量” (Weight Vector)
        w = np.exp(-2j * np.pi * d_over_lambda * np.arange(N) * np.sin(rad))
        
        # 核心操作：加权求和 (Beamforming)
        # 将 N 个阵元的信号按 w 方向对齐并相加
        y = w.conj().T @ x 
        
        # 计算输出能量
        power = np.mean(np.abs(y)**2)
        P_dbf.append(power)
    
    return search_angles, 10 * np.log10(P_dbf / np.max(P_dbf))

# 仿真运行
angles_true = [-20, 15]
angles, spectrum_dbf = dbf_algo(N=4, d_over_lambda=0.5, angles_true=angles_true, snr=20)

plt.figure(figsize=(10, 5))
plt.plot(angles, spectrum_dbf, label='DBF (N=4)', color='blue')
plt.axvline(-20, color='r', linestyle='--', alpha=0.5)
plt.axvline(15, color='r', linestyle='--', alpha=0.5)
plt.title("Digital Beamforming (DBF) Power Spectrum")
plt.xlabel("Angle (deg)")
plt.ylabel("Normalized Power (dB)")
plt.grid(True)
plt.show()
