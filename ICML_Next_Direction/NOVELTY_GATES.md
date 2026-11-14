# 联网新颖性检查记录（2026-11-14）

每条结论后面的链接是检索时看到的来源。arxiv.org 在沙箱里打不开，下面对 arXiv 论文的描述来自搜索摘要和 GitHub 说明，**没有读到全文**。

## 检查一：重复采样曲线的外推极限（`NEW_DIRECTION.md` 的推荐方向）——未通过，放弃

备忘录里的三个核心现象已经被 2026 年的工作覆盖：

| 我们离线得到的现象 | 已有工作 |
|---|---|
| 固定 n 次采样只确定前 n 阶矩，k > n 的 pass@k 只能部分识别 | *What Fixed-Rollout pass@k Evaluations Can Identify*，arXiv 2609.09245（2026 年 9 月） |
| 题目无穷多时可确定到 k ≈ n²（由 x^k 的最佳多项式逼近给出） | 同一工作的代码仓库写明 Theorem 1A：k ≤ n²/ln(4/ε) 时误差至多 ε，k ≥ 8n² 时至少 0.34 |
| 题目有限时只能外推约 2 倍；两点下界；非参数区间；"多采样比多出题有效" | 同上，并在 Monkey Business 数据上验证 |
| 多数投票曲线的矩问题 | *Two Calls, Two Moments, and the Vote-Accuracy Curve of Repeated LLM Inference*，arXiv 2605.03379（2026 年 5 月），用前两阶矩给出有限票数和无穷票数的精确界 |
| Beta-二项参数外推 | Kazdan 等，arXiv 2510.05197（确实存在） |

剩下没人做的只有假设阶梯、硬边渐近和"首次成功即停"的设计，属于窄的边角。按规则放弃。

来源：
- https://arxiv.org/pdf/2609.09245
- https://github.com/meherabb/passk-extrapolation-limits
- https://arxiv.org/abs/2605.03379
- https://arxiv.org/abs/2510.05197
- https://arxiv.org/pdf/1511.07428

## 检查二：每题只有少数标注者时，评测指标能被确定到什么程度——通过，带一条风险

方向内容见 `DIRECTION_2.md`。

没有找到的东西：对"模型相对于真实多数标签的准确率"在少数标注者下给出精确可识别区间、有效置信区间或排名可识别条件的工作。

相邻工作（都要引用，并说明区别）：

| 工作 | 做了什么 | 与本方向的区别 |
|---|---|---|
| arXiv 2605.03379、2609.09245 | 同一种数学视角（混合分布的矩），对象是 LLM 的重复采样 | 对象不是人类标注；前者只用两阶矩 |
| *Forest vs Tree: The (N,K) Trade-off in Reproducible ML Evaluation*（Google，2026 年 3 月博客介绍） | 用模拟器研究题数与每题标注人数的取舍 | 模拟研究，没有可识别性结论 |
| *Bias-Corrected Ceilings of Emotion Predictability…*，arXiv 2608.15619 | 少数标注下熵型上限的偏差校正（GoEmotions） | 目标是熵和 Fano 界，不是共识准确率 |
| Ishida 等 2023；Ushio 等（ICLR 2026） | 用软标签或多个硬标签估计 Bayes 误差及其偏差 | 没有非参数极限，也不涉及模型与共识的一致率 |
| *Weak Supervision Performance Evaluation via Partial Identification*（NeurIPS 2024） | 用 Fréchet 界评估弱监督模型 | 没有标注者重复这一结构 |
| Kadasi & Singh 2023 等 | 在 ChaosNLI 上对标注者子采样的经验研究 | 经验研究 |

风险：数学工具是经典的矩问题理论，并且 2026 年已有两篇把它用在 LLM 采样上。理论审稿人可能认为本方向是"同一工具换了对象"。应对办法是把重点放在那两篇没有的内容上：与模型预测的联合识别和排名、共识准确率与上限的不同速率、有限题数下的有效区间、自适应追加标注，以及在有 50–120 名标注者的真实数据上的验证。

数据可得性（已实测）：
- CIFAR-10H 的计数文件可从 GitHub 下载（10000 张图，每张 47–63 人标注）。
- DICES 可从 GitHub 下载（每段对话约 70–123 人）。
- CIFAR-10 的预训练模型权重可从 GitHub release 下载。
- ChaosNLI 原始数据在 Dropbox，HuggingFace 和 Dropbox 都被沙箱网络策略拦截，需要另找镜像或请您放行。

来源：
- https://arxiv.org/pdf/2608.15619
- https://research.google/blog/building-better-ai-benchmarks-how-many-raters-are-enough/
- https://arxiv.org/pdf/2202.00395
- https://github.com/RyotaUshio/bayes-error-estimation
- https://proceedings.neurips.cc/paper_files/paper/2024/file/f4c6bec746b0aeca8c2cd15096f1ad1f-Paper-Conference.pdf
- https://arxiv.org/html/2604.07591
- https://arxiv.org/pdf/2606.15031
