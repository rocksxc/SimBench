# ICML 项目交接包 — v13（第三轮评审已完成：4/4/3，目标未达成；按用户要求在第四轮修改前暂停。详见 ROUND_LOG_v13.md 与 HANDOFF_v13.md 的“Where to start for round 4”）

论文：**The Statistical Value of Adaptive Feature Queries**（目标 ICML 2027，尚未投稿）。本目录 = v13 的全部新工作；v11/v12 快照不在仓库中（见原交接包）。

## 先读什么
1. `HANDOFF_v13.md`：当前状态、新定理、新实验数字、易错点、下一步。
2. `Manuscript/paper.pdf`：当前稿件（正文 8 页含影响声明；附录按正文引用顺序排列）；`Manuscript/legacy_supplement.pdf`：早期阶段材料（受限分支菜单、受控细化、标定迁移、试点、成本交叉等），已从主稿附录移出。
3. `ROUND_LOG_v13.md`：每一轮的新颖性检查、三位审稿人分数与主要意见、修改记录。
4. `Reviews/`：第二轮（v12）三份完整审稿与第三轮（v13）审稿。
5. `Research/code/`、`Research/results/`：v13 新代码与逐任务结果（精确上限网格、平滑/自助敏感性、模型辅助插补、参考律预测器、定理数值检验）。

## 用户的工作方式（必须遵守）
- 不断修改，直到三位独立模拟的 ICML 2027 审稿人都给出至少 Weak accept（6 分制中的 4 分）。
- 每轮修改前先联网检查新颖性；若已有工作使剩余方向很窄，则放弃并先断网独立构思新方向。
- 每轮结束后向用户汇报。

## 不要做的事
- 不要编造审稿分数、作者核验、实验或参考文献；证明的人工核验仍未完成（`Manuscript/AUTHOR_VERIFICATION.md`）。
- 不要把模拟审稿当作真实 ICML 意见。
