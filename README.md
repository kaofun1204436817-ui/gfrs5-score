# GFRS-5 Lower-Limb Functional Decline Risk Score

**GFRS-5**（Gout Functional Risk Score, 5-item）is a bedside risk score for lower-limb functional decline in adults with gout or hyperuricaemia. It uses five items available from routine interview and physical examination — age, sex, BMI, comorbidity count and arthritis — and requires no laboratory test.

**GFRS-5** 是面向痛风及高尿酸血症人群的下肢功能衰退风险评分，仅含年龄、性别、BMI、共病数与关节炎 5 项，均为问诊与体检可得，不需要实验室检测。

---

## Model performance / 模型性能

| Item / 项目 | Value / 数值 |
|---|---|
| Development cohort / 开发队列 | NHANES 2007–2018, 6 cycles, n = 5 765, events 1 294 (22.4%) |
| External validation / 外部验证 | CHARLS 2011–2020, n = 8 977, events 3 361, median follow-up 7 years |
| Discrimination (development) / 开发库区分度 | AUC 0.771 (95%CI 0.759–0.785) |
| Discrimination (external) / 外部验证区分度 | Harrell C-index 0.664 (95%CI 0.654–0.673); IPCW C-index 0.693 |
| Increment over age + sex / 相对年龄性别的增量 | External C-index 0.636 → 0.647 (+BMI & comorbidity) → 0.668 (+arthritis); NRI 0.412, IDI 0.044 |
| Four-year cumulative incidence by stratum / 分层 4 年累积发生率 | Low 17.5% · Intermediate 36.7% · High 50.0% |

The four-year risk conversion `risk = 1 / (1 + exp(-(-2.2841 + 0.0387 × score)))` was estimated **within CHARLS** as a logistic recalibration. **Recalibrate before applying to any other population.**

4 年风险换算系数由 CHARLS 数据再校准得到，迁移至其他人群前必须重新校准。

---

## Score / 评分

| Item / 项目 | Category / 分类 | Points / 分值 |
|---|---|---|
| Age (years) / 年龄 | < 55 / 55–64 / 65–74 / ≥ 75 | 0 / 9 / 17 / 26 |
| BMI (kg/m²) | < 24 / 24–27.9 / 28–31.9 / ≥ 32 | 0 / 4 / 7 / 12 |
| Comorbidity count / 共病数 | 0 / 1 / 2 / 3 / ≥ 4 | 0 / 6 / 13 / 19 / 26 |
| Sex / 性别 | Male / Female | 0 / 3 |
| Arthritis / 关节炎 | No / Yes | 0 / 23 |

Total 0–90 points. Strata: **low < 36**, **intermediate 36–58**, **high > 58**.

Comorbidity count covers nine conditions (heart failure, coronary heart disease, angina, myocardial infarction, stroke, diabetes, chronic kidney disease, hypertension, dyslipidaemia) and **excludes arthritis**, which is scored separately.

共病数计 9 类慢性病，**不含关节炎**（关节炎已单列，重复计入会高估风险）。

---

## Run locally / 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

---

## Privacy / 隐私

All computation happens in the browser session. No input is uploaded, logged or stored.

所有计算在本地会话内完成，不上传、不记录、不存储任何输入。

---

## Disclaimer / 免责

This tool is for risk stratification and follow-up planning only. It is **not** a diagnostic or therapeutic device and does **not** provide medication advice. Clinical decisions must integrate history, examination and concurrent treatment.

本工具仅用于风险分层与随访强度提示，**不构成诊断、治疗或用药建议**，不替代医师面诊。

---

## Data availability / 数据可得性

No individual-level data are included in this repository. NHANES data are available from the US National Center for Health Statistics (https://www.cdc.gov/nchs/nhanes/); CHARLS data are available from the National School of Development, Peking University (http://charls.pku.edu.cn/).

本仓库不含任何个体数据。

---

## Citation / 引用

郭帆凡, 郭德鸿, 林昌松. 痛风及高尿酸血症人群下肢功能衰退风险评分的构建与验证：基于 NHANES 与 CHARLS 的双库研究[J]. 实用医学杂志, 2026.（投稿中）

---

## Files / 文件

| File | Purpose |
|---|---|
| `app.py` | Streamlit application / 主程序 |
| `scorecard.json` | Single source of truth for points, cut-offs and risk coefficients / 分值唯一真值 |
| `requirements.txt` | Dependencies / 依赖 |

Do not hard-code points inside `app.py`; edit `scorecard.json` only.

分值只写在 `scorecard.json`，不要改 `app.py` 里的逻辑。
