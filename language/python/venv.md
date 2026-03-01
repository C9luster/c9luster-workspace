# Python venv 使用说明

`venv` 是 Python 3.3+ 内置的虚拟环境模块，用于为项目创建独立的 Python 环境，避免依赖冲突。

## 创建虚拟环境

在项目目录下执行（常用目录名为 `.venv` 或 `venv`）：

```bash
python -m venv .venv
```

或指定 Python 解释器版本（**不会自动下载 Python**，需本机已安装该版本并在 PATH 中）：

```bash
python3.11 -m venv .venv
```

多版本需自行安装（如用系统包管理器、pyenv、官方安装包等）并配置好 PATH，venv 只是「用已有的解释器」建环境。

## 激活虚拟环境

**macOS / Linux：**

```bash
source .venv/bin/activate
```

**Windows (CMD)：**

```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell)：**

```powershell
.venv\Scripts\Activate.ps1
```

激活后终端提示符前会显示 `(.venv)`，此时 `pip install` 的包只会装到该环境中。

## 常用操作

```bash
# 在虚拟环境中安装依赖
pip install -r requirements.txt
pip install some-package

# 导出当前环境依赖（便于他人复现）
pip freeze > requirements.txt

# 退出虚拟环境
deactivate
```

## 建议

- 将虚拟环境目录（如 `.venv`）加入 `.gitignore`，不要提交到版本库。
- 每个项目单独一个 venv，避免多项目共用同一环境。

## venv 与 conda 对比

| 能力           | venv              | conda                    |
|----------------|-------------------|--------------------------|
| 隔离依赖       | ✅                 | ✅                       |
| 多 Python 版本 | 需本机先装好并配 PATH | ✅ 可 `conda install python=3.11` 安装 |
| 非 Python 依赖 | ❌                 | ✅（如 CUDA、R、C 库等） |
| 体积/复杂度    | 轻量、标准库      | 较重、需装 Anaconda/Miniconda |

需要多版本 Python 或大量科学计算/系统级依赖时，conda 更省心；只做纯 Python 项目、本机版本已固定时，venv 足够。
