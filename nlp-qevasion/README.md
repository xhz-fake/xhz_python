# 对话问答回避检测与 QNLI 数据效率实验

项目使用 QEvasion 数据集进行回答清晰度三分类，并在 QNLI 上比较模型直接迁移、重新训练以及不同标注数据量下的表现。模型包括多数类基线、TF-IDF + 逻辑回归和 GloVe 文本对表示 + 逻辑回归。

论文：Thomas et al., 2024，*“I Never Said That”: A dataset, taxonomy and baselines on response clarity classification*，Findings of EMNLP。

- [论文原文](https://aclanthology.org/2024.findings-emnlp.300/)
- [作者代码](https://github.com/konstantinosftw/Question-Evasion)

## 运行

使用 Python 3.12，在项目目录运行：

```powershell
python -m pip install -r requirements.txt
python download_data.py
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
python experiment.py
python extension.py
python verify_results.py
```

download_data.py 从 Hugging Face 下载数据集与词向量。Linux、macOS 下可在运行前设置相同的线程环境变量。

## 文件说明

| 文件或目录 | 内容 |
|---|---|
| experiment.py | QEvasion 分类与 QNLI 固定抽样迁移实验 |
| extension.py | QNLI 标注数据量对比 |
| download_data.py | 下载固定版本的数据和词向量 |
| verify_results.py | 根据预测文件重算指标，检查抽样索引和汇总结果 |
| requirements.txt | Python 依赖版本 |
| input_manifest.json | 输入文件的下载地址、版本和 SHA-256 |
| output/ | 原任务与迁移实验的指标、配置和数据统计 |
| extension_output/ | 数据量实验的逐次结果、汇总和配置 |
| submission_results/ | 逐样本预测与检查结果 |

## 实验设置

| 实验 | 训练样本数 | 评测样本数 |
|---|---:|---:|
| QEvasion 三分类 | 3,448 | 308 |
| QNLI 固定抽样迁移 | 3,448 | 308 |
| QNLI 数据效率 | 10,475 / 31,423 / 104,743 | 5,463 |

数据效率实验使用官方 QNLI 训练集的 10%、30% 和 100%。10%、30% 分别采用随机种子 42、52、62 按标签分层抽样，同一种子下的 10% 样本包含在 30% 样本中。低比例结果报告三次抽样的均值和样本标准差；100% 使用完整训练集拟合一次。模型参数提前固定，评测集保持不变。

直接迁移将 QEvasion 模型预测的 Clear Reply 映射为 QNLI 的 entailment（0），其余两类映射为 not_entailment（1）。适配实验在 QNLI 训练数据上重新拟合分类器。

GloVe 使用 18,712 个 50 维词向量，每侧文本最多保留 192 词，平均池化后连接 [q, a, |q-a|, q*a]，形成 200 维特征。TF-IDF 使用 min_df=2、max_features=40000、sublinear_tf=True，在训练集上拟合词表。逻辑回归参数为 max_iter=1000、random_state=42。

## 实验结果

QEvasion 类别均衡 TF-IDF 的 Macro-F1 为 **0.4436**。QNLI 固定抽样实验中，GloVe 模型直接迁移为 **0.4719**，在目标数据上重新训练后为 **0.6807**。

QNLI 官方验证集上的数据效率结果：

| 训练比例 | TF-IDF Macro-F1 | GloVe Macro-F1 |
|---|---:|---:|
| 10% | 0.5722 ± 0.0043 | 0.6576 ± 0.0024 |
| 30% | 0.5893 ± 0.0023 | 0.6621 ± 0.0026 |
| 100% | 0.6081 | 0.6636 |

GloVe 在 10% 标注量下已接近全量结果；TF-IDF 随训练数据增加继续改善。完整指标见 output/metrics.json 和 extension_output/summary.json。

## 数据来源

- [QEvasion](https://huggingface.co/datasets/ailsntua/QEvasion)，许可证：CC-BY-NC-ND-4.0。
- [GLUE / QNLI](https://huggingface.co/datasets/nyu-mll/glue)。
- [GloVe](https://nlp.stanford.edu/projects/glove/)。

数据与词向量通过下载脚本获取，固定版本见 input_manifest.json。
