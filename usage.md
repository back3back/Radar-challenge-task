# 使用方法说明

## 📁 项目文件结构

```
D:\01_Projects\class\Radar\
├── README.md                    # 任务要求
├── 挑战任务 3.md                 # 详细报告（Markdown 格式）
├── presentation.html            # HTML PPT 演示文稿
├── usage.md                     # 本文件 - 使用说明
├── pyproject.toml               # Python 项目配置
│
├── src/radar/
│   ├── p3-1.py                  # 任务 3-1 仿真代码
│   ├── p3-2.py                  # 任务 3-2 仿真代码
│   └── __init__.py
│
├── tests/
│   └── test_radar.py            # pytest 单元测试
│
└── docs/
    ├── p3-1-results.png         # 任务 3-1 结果图
    └── p3-2-results.png         # 任务 3-2 结果图
```

---

## 🔧 环境准备

### 前置要求
- Python 3.10+
- uv 包管理器（推荐）或 pip

### 安装依赖

```bash
# 进入项目目录
cd D:\01_Projects\class\Radar

# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip
pip install -e .
```

---

## 📊 运行仿真

### 运行任务 3-1（单目标测角）

```bash
# 使用 uv
uv run python src/radar/p3-1.py

# 或直接运行（如果已激活虚拟环境）
python src/radar/p3-1.py
```

**输出：**
- 控制台打印测角结果和作用距离分析
- 生成 `p3-1-results.png` 图片

### 运行任务 3-2（双目标测角）

```bash
uv run python src/radar/p3-2.py
```

**输出：**
- 控制台打印不同测角方法对比和参数分析
- 生成 `p3-2-results.png` 图片

---

## ✅ 运行测试

```bash
# 运行所有 pytest 测试
uv run pytest tests/test_radar.py -v

# 查看测试覆盖率
uv run pytest tests/test_radar.py -v --cov=src/radar
```

**预期结果：** 19 个测试全部通过

---

## 📖 查看报告

### 查看详细报告（Markdown）

使用 Markdown 阅读器打开 `挑战任务 3.md`：

- **VS Code**: 选中文件，按 `Ctrl+Shift+V` 预览
- **Typora**: 直接打开文件
- **浏览器**: 使用 Markdown 预览插件

### 查看 HTML PPT 演示文稿

#### 方法 1：直接打开（推荐）

```bash
# Windows 资源管理器
start presentation.html

# 或使用默认浏览器
start "" "presentation.html"
```

#### 方法 2：使用本地服务器

```bash
# 使用 Python 内置服务器
uv run python -m http.server 8000

# 然后访问：http://localhost:8000/presentation.html
```

### 生成 PowerPoint (.pptx) 文件

如果需要原生 PowerPoint 格式，可以使用 Python 脚本生成：

```bash
# 生成 PPTX 文件
uv run python create_ppt.py

# 打开生成的 PPTX
start presentation.pptx
```

**注意：** PPTX 文件中的公式会以纯文本形式显示（如 `Δθ ≈ λ / L`），不如 HTML 中的 LaTeX 渲染效果美观。

---

## 🎮 HTML PPT 操作指南

### 键盘快捷键

| 按键 | 功能 |
|------|------|
| `→` 或 `空格` 或 `Enter` | 下一页 |
| `←` | 上一页 |

### 触摸操作

- 向左滑动：下一页
- 向右滑动：上一页

### 界面元素

- **底部进度条**: 显示当前演示进度
- **左下角页码**: 显示当前页/总页数
- **右下角导航按钮**: 点击切换页面

---

## 📋 PPT 内容概览

共 14 张幻灯片：

1. 标题页
2. 任务概述
3. 系统参数设计
4. 信号模型
5. 测角算法原理
6. 任务 3-1 结果图
7. 任务 3-1 数据总结
8. 任务 3-2 结果图
9. 角度分辨力分析
10. 提高分辨率的方法
11. 代码结构
12. 测试结果
13. 结论
14. 结束页

---

## 🔍 常见问题

### Q1: 依赖安装失败？

```bash
# 尝试更新 uv
uv self update

# 或清除缓存后重新安装
rm -rf .venv
uv sync
```

### Q2: 图片无法显示？

确保 `docs/` 目录与 `presentation.html` 在同一层级，图片路径为 `./docs/p3-1-results.png`

### Q3: 如何在浏览器中全屏查看？

按 `F11` 进入全屏模式，获得最佳演示体验。

### Q4: PPT 中的公式显示不正常？

PPT 使用 [MathJax](https://www.mathjax.org/) 渲染 LaTeX 公式，需要网络连接加载 MathJax CDN。
- 确保电脑已连接互联网
- 如果网络受限，公式可能无法正确渲染

### Q5: 公式渲染慢？

MathJax 首次加载需要时间，等待几秒钟即可正常显示。刷新页面可重新渲染。

---

## 📞 技术支持

如有问题，请检查：
1. Python 版本 >= 3.10
2. 所有依赖已正确安装
3. 文件路径是否正确
