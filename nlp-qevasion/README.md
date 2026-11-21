# 对话问答回避检测与 QNLI 数据效率实验

课程项目围绕三个问题：基础模型是否优于多数类、文本对流程跨任务的适配边界，以及标注量变化如何影响结果。

论文依据：Thomas et al., 2024，*“I Never Said That”: A dataset, taxonomy and baselines on response clarity classification*，Findings of EMNLP。原文：<https://aclanthology.org/2024.findings-emnlp.300/>。作者代码：<https://github.com/konstantinosftw/Question-Evasion>。

这里实现课程轻量基线和扩展，不声称复现论文的 Llama-70B、LoRA 或全部神经模型。GloVe 是静态预训练词表示。

## 运行

Python 3.12，建议在独立虚拟环境中运行。

```powershell
python -m pip install -r requirements.txt
python download_data.py
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
python experiment.py
python extension.py
python verify_results.py
```

Linux/macOS 可把线程环境变量置于命令前。下载可能需要正常访问 Hugging Face。公开数据和词向量按固定版本取得，原始数据不随仓库再分发。

## 文件

- `experiment.py`：QEvasion 多数类、三组 TF-IDF、GloVe，以及 QNLI 固定抽样迁移比较。
- `extension.py`：官方完整 QNLI 训练池上的 10%、30%、100% 标注量比较。
- `download_data.py`：固定版本输入下载，校验 Parquet 完整性并明确限制词向量为前 8,000,000 字节。
- `verify_results.py`：独立根据预测重算指标，检查训练子集嵌套关系与汇总一致性。
- `output/metrics.json`、`output/config.json`、`output/stats.json`：原任务和固定抽样迁移结果。
- `extension_output/summary.json`、`runs.csv`、`details.json`、`config.json`：标注量实验结果与协议。
- `submission_results/`：上传用的精简逐样本预测和验证记录，排除原始问答文本。
- `input_manifest.json`：固定输入来源、修订与 SHA-256。清单中的论文不参与模型训练。

## 评测口径

原任务使用固定版本 QEvasion 官方训练/测试：3,448 / 308。QNLI 迁移比较沿用官方训练/验证中固定抽取的 3,448 / 308 条。新增数据效率使用官方完整训练 104,743 条、固定官方验证 5,463 条；两个评测规模的分数分开解释。

数据效率的 10%、30% 分别在种子 42、52、62 上做按标签分层的嵌套抽样；100% 为完整官方训练数据，确定性分类器只拟合一次。全部参数提前固定，官方测试/验证仅用于报告，不用于配置挑选。低比例汇总是均值和样本标准差，不是置信区间。

直接复用把源三分类器的 `Clear Reply` 映射为 QNLI 0，其余映射为 1。该语义桥接不表示两个任务等价；预测先三分类再映射，与先合并概率再 argmax 并非同一决策规则。适配训练是在 QNLI 上重训相同表示和分类结构。

GloVe 仅使用 18,712 个完整 50 维词向量；每侧最多 192 词，平均池化后连接 `[q, a, |q-a|, q*a]` 得到 200 维表示。TF-IDF 使用 `min_df=2,max_features=40000,sublinear_tf=True`，词表只在当前训练集拟合。逻辑回归 `max_iter=1000,random_state=42`，其余参数由锁定环境确定。

## 本次结果

以提交的 JSON 和逐样本预测为准。QEvasion 类别均衡 TF-IDF 的 Macro-F1 为 0.4436；固定抽样 QNLI 的 GloVe 适配重训为 0.6807。官方完整验证集上，GloVe 在 10%、30%、100% 下的 Macro-F1 分别为 0.6576、0.6621、0.6636；TF-IDF 分别为 0.5722、0.5893、0.6081。

历史课程输出使用未完整锁定的环境，与本次部分结果有小幅差异；历史文件保留在本地，不混入本提交。本文结论只适用于当前英文文本、固定数据版本及表示模型。没有进行统计显著性检验，不将小差异称为显著提升。

## 数据来源和引用

QEvasion：<https://huggingface.co/datasets/ailsntua/QEvasion>，数据卡标注 `CC-BY-NC-ND-4.0`。GLUE/QNLI：<https://huggingface.co/datasets/nyu-mll/glue>。GloVe：<https://nlp.stanford.edu/projects/glove/>；下载使用清单中固定的镜像修订。请分别遵守上游条款并引用原作者；本项目不替上游数据或模型授予许可证。
