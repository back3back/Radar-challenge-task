"""
雷达挑战任务 3-1:1 发 4 收阵列单目标测角仿真

仿真一个 1 发 4 收的阵列 (d = λ/2) 测量某点目标的角度
要求：
1. 产生回波信号
2. 给出用 FFT 测角和相位法测角的仿真结果
3. 分析对比两种测角方式下的作用距离
"""

import numpy as np
import matplotlib.pyplot as plt


def generate_echo_signal(f0, t, target_angle, num_rx, d, c):
    """
    生成回波信号 (基带信号模型)

    参数:
        f0: 载波频率 (Hz)
        t: 时间向量
        target_angle: 目标角度 (rad)
        num_rx: 接收阵元数量
        d: 阵元间距 (m)
        c: 光速 (m/s)

    返回:
        echo_signals: 各阵元的回波信号 (复数基带)
    """
    wavelength = c / f0

    # 各阵元的回波信号 (考虑波程差引入的相位差)
    # 注意：相位是相对于第一个阵元的
    echo_signals = np.zeros((num_rx, len(t)), dtype=complex)

    for n in range(num_rx):
        # 波程差引起的相位差 (相对于阵元 0)
        # 当波从 theta 方向来时，阵元 n 比阵元 0 多走 n*d*sin(theta) 的距离
        # 对应的相位超前为：2*pi*n*d*sin(theta)/lambda
        path_diff = n * d * np.sin(target_angle)
        phase_shift = 2 * np.pi * path_diff / wavelength

        # 基带信号 (简化模型，重点关注空间相位)
        baseband_signal = np.ones(len(t)) * np.exp(1j * phase_shift)
        echo_signals[n, :] = baseband_signal

    return echo_signals


def fft_angle_estimation(echo_signals, wavelength, d):
    """
    FFT 测角方法
    """
    num_rx, num_samples = echo_signals.shape

    # 脉冲压缩 (时间维积累)
    compressed_signals = np.zeros(num_rx, dtype=complex)
    for n in range(num_rx):
        compressed_signals[n] = np.sum(echo_signals[n, :])

    # 空间 FFT
    n_fft = 256
    angle_spectrum = np.abs(np.fft.fft(compressed_signals, n_fft))
    angle_spectrum = np.fft.fftshift(angle_spectrum)

    # 角度轴 (sin_theta 空间)
    sin_theta = np.linspace(-1, 1, n_fft)

    # 找到峰值对应的角度
    peak_idx = np.argmax(angle_spectrum)
    estimated_sin_theta = sin_theta[peak_idx]
    estimated_sin_theta = np.clip(estimated_sin_theta, -1, 1)
    estimated_angle = np.arcsin(estimated_sin_theta)

    return estimated_angle, angle_spectrum, sin_theta


def phase_angle_estimation(echo_signals, wavelength, d):
    """
    相位法测角 (比相法)
    """
    num_rx, num_samples = echo_signals.shape

    # 脉冲压缩
    compressed_signals = np.zeros(num_rx, dtype=complex)
    for n in range(num_rx):
        compressed_signals[n] = np.sum(echo_signals[n, :])

    # 计算相邻阵元间的相位差
    phase_diffs = np.zeros(num_rx - 1)
    for n in range(num_rx - 1):
        phase_diff = np.angle(compressed_signals[n + 1] * np.conj(compressed_signals[n]))
        phase_diffs[n] = phase_diff

    # 平均相位差
    avg_phase_diff = np.mean(phase_diffs)

    # 由相位差计算角度：phase_diff = 2*pi*d*sin(theta)/lambda
    estimated_sin_theta = avg_phase_diff * wavelength / (2 * np.pi * d)
    estimated_sin_theta = np.clip(estimated_sin_theta, -1, 1)
    estimated_angle = np.arcsin(estimated_sin_theta)

    return estimated_angle, phase_diffs


def calc_max_range_snr(f0, bw, tx_power, g, sigma, noise_figure,
                        min_snr_db, target_angle, num_rx, d, c):
    """
    计算给定条件下的最大作用距离
    """
    wavelength = c / f0
    k = 1.38e-23  # 玻尔兹曼常数
    T0 = 290  # 标准温度

    # 噪声功率
    noise_power = k * T0 * bw * 10**(noise_figure / 10)

    # 不同距离下的 SNR
    ranges = np.linspace(100, 50000, 500)
    snr_db = np.zeros_like(ranges)

    for i, R in enumerate(ranges):
        # 雷达方程
        pr = (tx_power * g**2 * wavelength**2 * sigma) / ((4 * np.pi)**3 * R**4)

        # 阵列增益 (取决于角度)
        array_gain = num_rx * (1 - np.abs(target_angle) / (np.pi / 2))
        pr *= array_gain

        snr = pr / noise_power
        snr_db[i] = 10 * np.log10(snr)

    # 找到满足最小 SNR 的最大距离
    valid_idx = snr_db >= min_snr_db
    if np.any(valid_idx):
        max_range = ranges[valid_idx][-1]
    else:
        max_range = 0

    return max_range, ranges, snr_db


def main():
    # ========== 系统参数 ==========
    c = 3e8  # 光速 (m/s)
    f0 = 10e9  # 载波频率 10 GHz (X 波段)
    bw = 100e6  # 带宽 100 MHz
    wavelength = c / f0

    # 阵列参数
    num_rx = 4  # 4 个接收阵元
    d = wavelength / 2  # 阵元间距半波长

    # 目标参数
    target_range = 10000  # 目标距离 10 km
    target_angle = np.deg2rad(30)  # 目标角度 30 度

    # 时间参数
    pulse_width = 10e-6  # 脉冲宽度 10 us
    fs = 10 * bw  # 采样频率
    t = np.arange(0, pulse_width, 1/fs)

    # ========== 生成回波信号 ==========
    print("=" * 50)
    print("雷达挑战任务 3-1: 单目标测角仿真")
    print("=" * 50)
    print(f"\n系统参数:")
    print(f"  载波频率：{f0/1e9:.1f} GHz")
    print(f"  带宽：{bw/1e6:.1f} MHz")
    print(f"  波长：{wavelength*1000:.2f} mm")
    print(f"  阵元数量：{num_rx}")
    print(f"  阵元间距：{d/wavelength:.2f} λ")
    print(f"\n目标参数:")
    print(f"  距离：{target_range/1000:.1f} km")
    print(f"  角度：{np.rad2deg(target_angle):.1f} 度")

    echo_signals = generate_echo_signal(f0, t, target_angle, num_rx, d, c)

    # ========== FFT 测角 ==========
    fft_angle, angle_spectrum, sin_theta = fft_angle_estimation(echo_signals, wavelength, d)

    print(f"\nFFT 测角结果:")
    print(f"  估计角度：{np.rad2deg(fft_angle):.2f} 度")
    print(f"  角度误差：{np.rad2deg(fft_angle - target_angle):.4f} 度")

    # ========== 相位法测角 ==========
    phase_angle, phase_diffs = phase_angle_estimation(echo_signals, wavelength, d)

    print(f"\n相位法测角结果:")
    print(f"  估计角度：{np.rad2deg(phase_angle):.2f} 度")
    print(f"  角度误差：{np.rad2deg(phase_angle - target_angle):.4f} 度")
    print(f"  相邻阵元相位差：{np.rad2deg(phase_diffs)}")

    # ========== 作用距离分析 ==========
    # 雷达参数
    tx_power = 100  # 发射功率 100 W
    g = 20  # 天线增益 20 dB
    sigma = 1  # 目标 RCS 1 m²
    noise_figure = 5  # 噪声系数 5 dB

    # 计算 FFT 测角的作用距离
    fft_min_snr = 15
    fft_max_range, fft_ranges, fft_snrs = calc_max_range_snr(
        f0, bw, tx_power, g, sigma, noise_figure,
        fft_min_snr, target_angle, num_rx, d, c
    )

    # 计算相位法测角的作用距离 (对 SNR 更敏感)
    phase_min_snr = 20
    phase_max_range, phase_ranges, phase_snrs = calc_max_range_snr(
        f0, bw, tx_power, g, sigma, noise_figure,
        phase_min_snr, target_angle, num_rx, d, c
    )

    print(f"\n作用距离分析:")
    print(f"  FFT 测角最大作用距离：{fft_max_range/1000:.2f} km (要求 SNR >= {fft_min_snr} dB)")
    print(f"  相位法测角最大作用距离：{phase_max_range/1000:.2f} km (要求 SNR >= {phase_min_snr} dB)")
    print(f"\n分析:")
    print(f"  - FFT 测角通过多阵元相干积累，具有较好的噪声抑制能力")
    print(f"  - 相位法测角直接利用相位信息，对噪声更敏感，需要更高的 SNR")
    print(f"  - 相位法测角在低 SNR 条件下性能下降更快")

    # ========== 绘图 ==========
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. 角度谱图 (FFT)
    ax = axes[0, 0]
    ax.plot(np.rad2deg(np.arcsin(sin_theta)), angle_spectrum)
    ax.axvline(np.rad2deg(target_angle), color='r', linestyle='--', label='真实角度')
    ax.axvline(np.rad2deg(fft_angle), color='g', linestyle='--', label='估计角度')
    ax.set_xlabel('Angle (deg)')
    ax.set_ylabel('Magnitude')
    ax.set_title('FFT Angle Estimation - Angle Spectrum')
    ax.legend()
    ax.grid(True)

    # 2. 相位差图
    ax = axes[0, 1]
    ax.bar(range(1, num_rx), np.rad2deg(phase_diffs))
    ax.axhline(np.rad2deg(np.mean(phase_diffs)), color='r', linestyle='--',
               label=f'Avg: {np.rad2deg(np.mean(phase_diffs)):.2f} deg')
    ax.set_xlabel('Element Pair')
    ax.set_ylabel('Phase Diff (deg)')
    ax.set_title('Phase Method - Inter-element Phase Difference')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. SNR vs 距离
    ax = axes[1, 0]
    ax.plot(fft_ranges/1000, fft_snrs, label='FFT Method')
    ax.plot(phase_ranges/1000, phase_snrs, label='Phase Method')
    ax.axhline(fft_min_snr, color='r', linestyle='--', alpha=0.5, label='FFT Min SNR')
    ax.axhline(phase_min_snr, color='g', linestyle='--', alpha=0.5, label='Phase Min SNR')
    ax.axvline(fft_max_range/1000, color='r', linestyle=':', alpha=0.5)
    ax.axvline(phase_max_range/1000, color='g', linestyle=':', alpha=0.5)
    ax.set_xlabel('Range (km)')
    ax.set_ylabel('SNR (dB)')
    ax.set_title('SNR vs Range')
    ax.legend()
    ax.grid(True)

    # 4. 测角误差对比
    ax = axes[1, 1]
    methods = ['FFT', 'Phase']
    errors = [abs(np.rad2deg(fft_angle - target_angle)),
              abs(np.rad2deg(phase_angle - target_angle))]
    bars = ax.bar(methods, errors, color=['blue', 'orange'])
    ax.set_ylabel('Angle Error (deg)')
    ax.set_title('Angle Estimation Error Comparison')
    for bar, err in zip(bars, errors):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{err:.4f}', ha='center', va='bottom', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('p3-1-results.png', dpi=150)
    print(f"\nResults saved to: p3-1-results.png")

    return {
        'fft_angle': fft_angle,
        'phase_angle': phase_angle,
        'fft_max_range': fft_max_range,
        'phase_max_range': phase_max_range
    }


if __name__ == "__main__":
    main()
