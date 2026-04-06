"""
雷达挑战任务 3-2:1 发 4 收阵列双目标测角仿真

仿真一个 1 发 4 收的阵列 (d = λ/2) 测量 2 个点目标的角度
要求：
1. 给出仿真结果
2. 仿真比较不同参数（阵元个数，阵元间距）设置对角度分辨力的影响
3. 查阅文献，给出 2 种提高角度分辨率方法的实现思路
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh
from scipy.signal import find_peaks as scipy_find_peaks


def generate_multi_target_echo(f0, t, targets, num_rx, d, c):
    """
    生成多目标回波信号 (基带模型)

    参数:
        f0: 载波频率 (Hz)
        t: 时间向量
        targets: 目标列表，每个元素为 (range, angle, rcs)
        num_rx: 接收阵元数量
        d: 阵元间距 (m)
        c: 光速 (m/s)

    返回:
        echo_signals: 各阵元的回波信号叠加
    """
    wavelength = c / f0
    echo_signals = np.zeros((num_rx, len(t)), dtype=complex)

    for target_range, target_angle, rcs in targets:
        for n in range(num_rx):
            # 波程差引起的相位差 (相对于阵元 0)
            path_diff = n * d * np.sin(target_angle)
            phase_shift = 2 * np.pi * path_diff / wavelength

            # 信号 (简化为常数，重点关注空间相位)
            echo_signals[n, :] += np.ones(len(t)) * np.exp(1j * phase_shift) * np.sqrt(rcs)

    return echo_signals


def fft_angle_estimation(echo_signals, wavelength, d, n_fft=256):
    """FFT 测角"""
    num_rx, num_samples = echo_signals.shape

    # 脉冲压缩
    compressed_signals = np.zeros(num_rx, dtype=complex)
    for n in range(num_rx):
        compressed_signals[n] = np.sum(echo_signals[n, :])

    # 空间 FFT
    angle_spectrum = np.abs(np.fft.fft(compressed_signals, n_fft))
    angle_spectrum = np.fft.fftshift(angle_spectrum)

    sin_theta = np.linspace(-1, 1, n_fft)

    # 找双峰
    peaks = find_peaks(angle_spectrum, n_peaks=2)
    estimated_angles = np.arcsin(np.clip(sin_theta[peaks], -1, 1)) if len(peaks) > 0 else np.array([])

    return estimated_angles, angle_spectrum, sin_theta


def music_angle_estimation(echo_signals, wavelength, d, num_sources=2, n_fft=256):
    """
    MUSIC 算法测角 (Multiple Signal Classification)
    高分辨率测角方法 1：基于子空间分解
    """
    num_rx, num_samples = echo_signals.shape

    # 构建协方差矩阵
    R = np.cov(echo_signals)

    # 特征分解
    eigenvalues, eigenvectors = eigh(R)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 噪声子空间
    noise_subspace = eigenvectors[:, num_sources:]

    # 空间谱搜索
    sin_theta = np.linspace(-1, 1, n_fft)
    music_spectrum = np.zeros(n_fft)

    for i, sin_val in enumerate(sin_theta):
        # 导向矢量
        a = np.exp(1j * 2 * np.pi * d / wavelength * sin_val * np.arange(num_rx)).reshape(-1, 1)

        # MUSIC 空间谱
        projection = np.conj(a.T) @ noise_subspace @ noise_subspace.conj().T @ a
        music_spectrum[i] = 1.0 / (float(np.real(projection[0, 0])) + 1e-10)

    # 找峰值
    peaks = find_peaks(music_spectrum, n_peaks=num_sources)
    estimated_angles = np.arcsin(np.clip(sin_theta[peaks], -1, 1)) if len(peaks) > 0 else np.array([])

    return estimated_angles, music_spectrum, sin_theta


def esprit_angle_estimation(echo_signals, wavelength, d, num_sources=2):
    """
    ESPRIT 算法测角
    高分辨率测角方法 2：基于旋转不变性
    """
    num_rx, num_samples = echo_signals.shape

    # 构建协方差矩阵
    R = np.cov(echo_signals)

    # 特征分解
    eigenvalues, eigenvectors = eigh(R)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx]

    # 信号子空间
    signal_subspace = eigenvectors[:, :num_sources]

    # 构造旋转矩阵
    phi1 = signal_subspace[:-1, :]  # 前 num_rx-1 个阵元
    phi2 = signal_subspace[1:, :]   # 后 num_rx-1 个阵元

    # 最小二乘求解旋转算子
    psi, _, _, _ = np.linalg.lstsq(phi1, phi2, rcond=None)

    # 特征值分解得到角度
    eigenvalues_psi, _ = np.linalg.eig(psi)

    # 由特征值相位计算角度
    estimated_angles = np.zeros(num_sources)
    for i in range(num_sources):
        phase = np.angle(eigenvalues_psi[i])
        sin_theta = phase * wavelength / (2 * np.pi * d)
        sin_theta = np.clip(sin_theta, -1, 1)
        estimated_angles[i] = np.arcsin(sin_theta)

    return estimated_angles


def find_peaks(spectrum, n_peaks=2):
    """找谱峰"""
    # 归一化
    spectrum_norm = (spectrum - np.min(spectrum)) / (np.max(spectrum) - np.min(spectrum) + 1e-10)

    # 找峰值
    peaks, properties = scipy_find_peaks(spectrum_norm, prominence=0.1, distance=5)

    if len(peaks) == 0:
        return np.array([])

    # 按峰值大小排序
    peak_values = spectrum_norm[peaks]
    sorted_idx = np.argsort(peak_values)[::-1][:n_peaks]

    return np.array(peaks)[sorted_idx] if len(peaks) >= n_peaks else peaks


def calc_angular_resolution(num_rx, d, wavelength):
    """
    计算理论角度分辨力 (瑞利判据)
    """
    L = (num_rx - 1) * d  # 阵列孔径
    delta_theta = wavelength / L  # 弧度
    return np.rad2deg(delta_theta)


def analyze_resolution_vs_parameters(f0, num_rx_list, d_factors, target_angle_sep_deg):
    """
    分析不同参数对角度分辨力的影响
    """
    c = 3e8
    wavelength = c / f0

    results = {'num_rx': [], 'd_factor': [], 'resolution': [], 'can_resolve': []}

    for num_rx in num_rx_list:
        for d_factor in d_factors:
            d = d_factor * wavelength
            resolution = calc_angular_resolution(num_rx, d, wavelength)
            can_resolve = target_angle_sep_deg > resolution

            results['num_rx'].append(num_rx)
            results['d_factor'].append(d_factor)
            results['resolution'].append(resolution)
            results['can_resolve'].append(can_resolve)

    return results


def main():
    # ========== 系统参数 ==========
    c = 3e8
    f0 = 10e9
    bw = 100e6
    wavelength = c / f0

    # 阵列参数
    num_rx = 4
    d = wavelength / 2

    # 时间参数
    pulse_width = 10e-6
    fs = 10 * bw
    t = np.arange(0, pulse_width, 1/fs)

    # ========== 双目标场景 ==========
    target_range1, target_angle1 = 10000, np.deg2rad(30)
    target_range2, target_angle2 = 10500, np.deg2rad(35)

    targets = [
        (target_range1, target_angle1, 1.0),
        (target_range2, target_angle2, 1.0)
    ]

    angle_separation = np.rad2deg(abs(target_angle2 - target_angle1))

    print("=" * 50)
    print("Radar Challenge Task 3-2: Two-Target Angle Estimation")
    print("=" * 50)
    print(f"\nSystem Parameters:")
    print(f"  Frequency: {f0/1e9:.1f} GHz")
    print(f"  Bandwidth: {bw/1e6:.1f} MHz")
    print(f"  Wavelength: {wavelength*1000:.2f} mm")
    print(f"  Elements: {num_rx}")
    print(f"  Spacing: {d/wavelength:.2f} lambda")
    print(f"\nTarget Parameters:")
    print(f"  Target 1: Range {target_range1/1000:.1f} km, Angle {np.rad2deg(target_angle1):.1f} deg")
    print(f"  Target 2: Range {target_range2/1000:.1f} km, Angle {np.rad2deg(target_angle2):.1f} deg")
    print(f"  Angular Separation: {angle_separation:.1f} deg")

    # 生成回波信号
    echo_signals = generate_multi_target_echo(f0, t, targets, num_rx, d, c)

    # ========== 不同测角方法对比 ==========
    print(f"\n--- Angle Estimation Methods Comparison ---")

    # FFT 测角
    fft_angles, fft_spectrum, sin_theta = fft_angle_estimation(echo_signals, wavelength, d)
    print(f"\nFFT Method:")
    if len(fft_angles) > 0:
        for i, angle in enumerate(fft_angles):
            print(f"  Target {i+1}: Estimated = {np.rad2deg(angle):.2f} deg")
    else:
        print("  Could not resolve two targets")

    # MUSIC 算法
    music_angles, music_spectrum, music_sin_theta = music_angle_estimation(
        echo_signals, wavelength, d, num_sources=2
    )
    print(f"\nMUSIC Algorithm (High Resolution):")
    if len(music_angles) > 0:
        for i, angle in enumerate(music_angles):
            print(f"  Target {i+1}: Estimated = {np.rad2deg(angle):.2f} deg")
    else:
        print("  Could not resolve two targets")

    # ESPRIT 算法
    esprit_angles = esprit_angle_estimation(echo_signals, wavelength, d, num_sources=2)
    print(f"\nESPRIT Algorithm (High Resolution):")
    if len(esprit_angles) > 0:
        for i, angle in enumerate(esprit_angles):
            print(f"  Target {i+1}: Estimated = {np.rad2deg(angle):.2f} deg")
    else:
        print("  Could not resolve two targets")

    # ========== 参数对分辨力的影响 ==========
    print(f"\n--- Array Parameters vs Angular Resolution ---")

    num_rx_list = [2, 4, 8, 16]
    d_factors = [0.25, 0.5, 0.75, 1.0]

    resolution_results = analyze_resolution_vs_parameters(
        f0, num_rx_list, d_factors, angle_separation
    )

    print(f"\nTheoretical Angular Resolution (Rayleigh Criterion):")
    print(f"  {'Elements':<10} {'d/lambda':<10} {'Resolution (deg)':<18} {'Can Resolve 5deg'}")
    print(f"  {'-'*50}")

    for i in range(len(resolution_results['num_rx'])):
        num_rx_val = resolution_results['num_rx'][i]
        d_factor = resolution_results['d_factor'][i]
        resolution = resolution_results['resolution'][i]
        can_resolve = "Yes" if resolution_results['can_resolve'][i] else "No"
        print(f"  {num_rx_val:<10} {d_factor:<10.2f} {resolution:<18.2f} {can_resolve}")

    # ========== 提高角度分辨率的方法 ==========
    print(f"\n--- Methods to Improve Angular Resolution ---")
    print("""
Method 1: MUSIC Algorithm (Multiple Signal Classification)
  Principle: Based on orthogonality between signal and noise subspaces
  Implementation:
    1. Build covariance matrix R = E[xx^H]
    2. Eigen-decomposition to separate signal and noise subspaces
    3. Construct spatial spectrum using noise subspace orthogonality
    4. Search for spectrum peaks to get DOA estimates
  Advantages: Breaks Rayleigh limit, super-resolution
  Disadvantages: Requires known number of sources, high computation

Method 2: ESPRIT Algorithm
  Principle: Exploits translational invariance of array
  Implementation:
    1. Divide array into two identical overlapping subarrays
    2. Eigen-decomposition to get signal subspace
    3. Use rotational invariance between subarrays
    4. Direct angle estimation via eigenvalue decomposition
  Advantages: Low computation, no spectrum search, high accuracy
  Disadvantages: Requires translational invariant array structure

Method 3: Compressed Sensing
  Principle: Exploits sparsity of targets in angle domain
  Implementation:
    1. Build over-complete angle dictionary
    2. Formulate DOA as sparse reconstruction problem
    3. Solve using L1 minimization or greedy algorithms
  Advantages: Works with few snapshots
  Disadvantages: Requires sparsity assumption, complex algorithms

Method 4: Maximum Likelihood Estimation
  Principle: Statistically optimal estimation
  Implementation:
    1. Build statistical model of received signals
    2. Construct likelihood function
    3. Solve via multidimensional search or alternating optimization
  Advantages: Asymptotically optimal, high resolution
  Disadvantages: Very high complexity, requires multidimensional search
""")

    # ========== 绘图 ==========
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # 1. FFT 角度谱
    ax = axes[0, 0]
    ax.plot(np.rad2deg(np.arcsin(sin_theta)), fft_spectrum)
    ax.axvline(np.rad2deg(target_angle1), color='r', linestyle='--', label='Target 1')
    ax.axvline(np.rad2deg(target_angle2), color='g', linestyle='--', label='Target 2')
    ax.set_xlabel('Angle (deg)')
    ax.set_ylabel('Magnitude')
    ax.set_title('FFT - Angle Spectrum')
    ax.legend()
    ax.grid(True)

    # 2. MUSIC 空间谱
    ax = axes[0, 1]
    ax.plot(np.rad2deg(np.arcsin(music_sin_theta)), music_spectrum)
    ax.axvline(np.rad2deg(target_angle1), color='r', linestyle='--', label='Target 1')
    ax.axvline(np.rad2deg(target_angle2), color='g', linestyle='--', label='Target 2')
    ax.set_xlabel('Angle (deg)')
    ax.set_ylabel('Power (a.u.)')
    ax.set_title('MUSIC Algorithm - Spatial Spectrum')
    ax.legend()
    ax.grid(True)

    # 3. 分辨力对比 (不同阵元数)
    ax = axes[0, 2]
    for d_factor in d_factors:
        resolutions = [calc_angular_resolution(n, d_factor*wavelength, wavelength)
                       for n in num_rx_list]
        ax.plot(num_rx_list, resolutions, marker='o', label=f'd = {d_factor}λ')
    ax.axhline(angle_separation, color='r', linestyle='--', label=f'Target Sep {angle_separation:.1f}°')
    ax.set_xlabel('Number of Elements')
    ax.set_ylabel('Angular Resolution (deg)')
    ax.set_title('Effect of Element Count on Resolution')
    ax.legend()
    ax.grid(True)

    # 4. 分辨力对比 (不同阵元间距)
    ax = axes[1, 0]
    for num_rx_val in [4, 8, 16]:
        resolutions = [calc_angular_resolution(num_rx_val, df*wavelength, wavelength)
                       for df in d_factors]
        ax.plot(d_factors, resolutions, marker='s', label=f'N = {num_rx_val}')
    ax.axhline(angle_separation, color='r', linestyle='--', label=f'Target Sep {angle_separation:.1f}°')
    ax.set_xlabel('Element Spacing (wavelengths)')
    ax.set_ylabel('Angular Resolution (deg)')
    ax.set_title('Effect of Element Spacing on Resolution')
    ax.legend()
    ax.grid(True)

    # 5. 不同方法测角误差对比
    ax = axes[1, 1]
    methods = ['FFT', 'MUSIC', 'ESPRIT']
    errors = []

    # FFT 误差
    if len(fft_angles) >= 2:
        fft_err1 = min(abs(np.rad2deg(fft_angles[0] - target_angle1)),
                       abs(np.rad2deg(fft_angles[0] - target_angle2)))
        fft_err2 = min(abs(np.rad2deg(fft_angles[1] - target_angle1)),
                       abs(np.rad2deg(fft_angles[1] - target_angle2)))
        errors.append((fft_err1 + fft_err2) / 2)
    else:
        errors.append(angle_separation)

    # MUSIC 误差
    if len(music_angles) >= 2:
        music_err1 = min(abs(np.rad2deg(music_angles[0] - target_angle1)),
                         abs(np.rad2deg(music_angles[0] - target_angle2)))
        music_err2 = min(abs(np.rad2deg(music_angles[1] - target_angle1)),
                         abs(np.rad2deg(music_angles[1] - target_angle2)))
        errors.append((music_err1 + music_err2) / 2)
    else:
        errors.append(angle_separation)

    # ESPRIT 误差
    if len(esprit_angles) >= 2:
        esprit_err1 = min(abs(np.rad2deg(esprit_angles[0] - target_angle1)),
                          abs(np.rad2deg(esprit_angles[0] - target_angle2)))
        esprit_err2 = min(abs(np.rad2deg(esprit_angles[1] - target_angle1)),
                          abs(np.rad2deg(esprit_angles[1] - target_angle2)))
        errors.append((esprit_err1 + esprit_err2) / 2)
    else:
        errors.append(angle_separation)

    colors = ['blue', 'green', 'orange']
    bars = ax.bar(methods, errors, color=colors)
    ax.set_ylabel('Angle Error (deg)')
    ax.set_title('Angle Estimation Error Comparison')
    for bar, err in zip(bars, errors):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{err:.2f}', ha='center', va='bottom', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 6. 分辨力热力图
    ax = axes[1, 2]
    resolution_matrix = np.zeros((len(num_rx_list), len(d_factors)))
    for i, num_rx_val in enumerate(num_rx_list):
        for j, d_factor in enumerate(d_factors):
            resolution_matrix[i, j] = calc_angular_resolution(num_rx_val, d_factor*wavelength, wavelength)

    im = ax.imshow(resolution_matrix, cmap='RdYlGn_r', aspect='auto')
    ax.set_xticks(range(len(d_factors)))
    ax.set_yticks(range(len(num_rx_list)))
    ax.set_xticklabels([f'{d:.2f}λ' for d in d_factors])
    ax.set_yticklabels(num_rx_list)
    ax.set_xlabel('Element Spacing')
    ax.set_ylabel('Number of Elements')
    ax.set_title('Angular Resolution Heatmap (deg)')
    plt.colorbar(im, ax=ax, label='Resolution (deg)')

    for i in range(len(num_rx_list)):
        for j in range(len(d_factors)):
            ax.text(j, i, f'{resolution_matrix[i, j]:.2f}',
                   ha="center", va="center", color="black", fontsize=9)

    plt.tight_layout()
    plt.savefig('p3-2-results.png', dpi=150)
    print(f"\nResults saved to: p3-2-results.png")

    return {
        'fft_angles': fft_angles,
        'music_angles': music_angles,
        'esprit_angles': esprit_angles,
        'resolution_results': resolution_results
    }


if __name__ == "__main__":
    main()
