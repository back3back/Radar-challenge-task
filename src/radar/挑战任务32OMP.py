import numpy as np
import matplotlib.pyplot as plt

def omp_doa(x_snapshot, dict_matrix, num_targets):
    """
    正交匹配追踪算法 (OMP)
    x_snapshot: 接收到的单次快拍信号 (N x 1)
    dict_matrix: 过完备字典 (N x M)
    num_targets: 预期的目标个数 K
    """
    N, M = dict_matrix.shape
    residual = x_snapshot.copy()  # 初始化残差
    selected_indices = []         # 存放选中的字典列索引
    
    for _ in range(num_targets):
        # 1. 匹配：计算残差与字典每一列的相关性
        projections = np.abs(dict_matrix.conj().T @ residual)
        
        # 2. 识别：找到相关性最大的角度索引
        best_idx = np.argmax(projections)
        selected_indices.append(best_idx)
        
        # 3. 估计：最小二乘投影，更新信号系数
        Phi = dict_matrix[:, selected_indices]
        # 解方程 Phi * s = x_snapshot -> s = pinv(Phi) * x
        s_hat = np.linalg.pinv(Phi) @ x_snapshot
        
        # 4. 更新：计算新的残差
        residual = x_snapshot - Phi @ s_hat
        
    # 构建最终的稀疏谱
    s_sparse = np.zeros(M)
    s_sparse[selected_indices] = np.abs(s_hat)
    return s_sparse

# --- 仿真参数 ---
N = 4                 # 4个阵元
d_lambda = 0.5        # 间距
snr = 20
angles_true = [-5, 5] # 两个挨得很近的目标
num_targets = len(angles_true)

# 1. 生成接收信号 (单快拍)
theta_rad = np.deg2rad(angles_true)
A = np.exp(-2j * np.pi * d_lambda * np.arange(N).reshape(-1, 1) @ np.sin(theta_rad).reshape(1, -1))
s = np.array([1.0, 0.8]) * np.exp(1j * 2 * np.pi * np.random.rand(num_targets)) # 目标幅值
noise = (np.random.randn(N) + 1j * np.random.randn(N)) / np.sqrt(2) * np.sqrt(10**(-snr/10))
x = A @ s + noise

# 2. 构造过完备字典 (划分1800个细网格)
search_angles = np.linspace(-90, 90, 1800)
D = np.exp(-2j * np.pi * d_lambda * np.arange(N).reshape(-1, 1) @ np.sin(np.deg2rad(search_angles)).reshape(1, -1))

# 3. 运行 CS-OMP 算法
s_sparse = omp_doa(x, D, num_targets)

# 4. 绘图对比
plt.figure(figsize=(10, 6))
plt.stem(search_angles, s_sparse / np.max(s_sparse), linefmt='r-', markerfmt='ro', basefmt=' ', label='CS-OMP Result')
for ang in angles_true:
    plt.axvline(ang, color='k', linestyle='--', alpha=0.5, label='True Angle' if ang==angles_true[0] else "")

plt.title(f"Super-Resolution DOA via Compressive Sensing (N={N})")
plt.xlabel("Angle (deg)")
plt.ylabel("Normalized Amplitude")
plt.legend()
plt.grid(True)
plt.show()
