import numpy as np
import matplotlib.pyplot as plt

def music_algo(N, d_over_lambda, angles_true, snr, num_samples=1000):
    # 信号生成
    theta = np.deg2rad(angles_true)
    A = np.exp(-2j * np.pi * d_over_lambda * np.arange(N).reshape(-1, 1) @ np.sin(theta).reshape(1, -1))
    
    # 仿真信号 + 噪声
    s = np.exp(1j * 2 * np.pi * np.random.rand(len(angles_true), num_samples))
    x = A @ s
    noise = (np.random.randn(N, num_samples) + 1j * np.random.randn(N, num_samples)) / np.sqrt(2)
    noise_power = 10**(-snr/10)
    x += np.sqrt(noise_power) * noise

    # 计算协方差矩阵
    R = (x @ x.conj().T) / num_samples
    eigvals, eigvecs = np.linalg.eigh(R)
    En = eigvecs[:, :-len(angles_true)] # 噪声子空间

    # 空间谱搜索
    search_angles = np.linspace(-90, 90, 1800)
    P_music = []
    for a in search_angles:
        rad = np.deg2rad(a)
        steer = np.exp(-2j * np.pi * d_over_lambda * np.arange(N) * np.sin(rad))
        p = 1 / np.abs(steer.conj() @ En @ En.conj().T @ steer)
        P_music.append(p)
    
    return search_angles, 10 * np.log10(P_music / np.max(P_music))

# 基础仿真
angles_true = [10, 15]
angles, spectrum = music_algo(N=4, d_over_lambda=0.5, angles_true=angles_true, snr=20)

plt.figure(figsize=(10, 5))
plt.plot(angles, spectrum, label='N=4, d=0.5λ')
plt.axvline(angles_true[0], color='r', linestyle='--', alpha=0.5)
plt.axvline(angles_true[1], color='r', linestyle='--', alpha=0.5)
plt.title("MUSIC DOA Estimation (1Tx 4Rx)")
plt.xlabel("Angle (deg)")
plt.ylabel("Normalized Spectrum (dB)")
plt.grid(True)
plt.legend()
plt.show()
