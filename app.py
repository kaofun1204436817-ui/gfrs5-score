# -*- coding: utf-8 -*-
"""GFRS-5 评分工具（Streamlit 版，可选）。

正式对外发布用单文件网页 `site/index.html`（由 03_build_site.py 生成）；
本文件是同一套分值的 Streamlit 实现，便于本地交互演示与二次开发。

两者共用唯一真值 scorecard.json —— 分值只写在那里，改完全部重跑：
    python 03_build_site.py   # 重新生成网页
    python 04_校验.py          # 校验网页与论文表 4 一致

运行：
    pip install streamlit
    streamlit run app.py

定位：痛风/高尿酸血症门诊与社区慢病管理中的下肢功能衰退风险分层 + 康复转诊提示。
隐私：不采集可识别信息，服务端不持久化任何输入。若需完全离线，
      应使用随论文补充材料提供的单文件版（site/index.html），其全部计算在本机完成。
免责：仅作风险分层辅助，不替代诊断，不给出用药建议。
"""
import json
import math
import os

import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "scorecard.json"), encoding="utf-8") as f:
    SC = json.load(f)

CUT_LO = SC["cuts"]["low_upper_exclusive"]
CUT_HI = SC["cuts"]["high_lower_exclusive"]
A = SC["risk4"]["intercept"]
B = SC["risk4"]["slope"]


def points_for(key: str, raw) -> int:
    """按 scorecard 的档位求分。upper 为开区间上界（raw < upper）。"""
    conf = SC["score"][key]
    if conf["type"] == "binary":
        return conf["levels"][1]["points"] if raw else conf["levels"][0]["points"]
    for lv in conf["levels"]:
        if lv["upper"] is None or raw < lv["upper"]:
            return lv["points"]
    return conf["levels"][-1]["points"]


def label_for(key: str, raw) -> str:
    conf = SC["score"][key]
    if conf["type"] == "binary":
        return conf["levels"][1]["label"] if raw else conf["levels"][0]["label"]
    for lv in conf["levels"]:
        if lv["upper"] is None or raw < lv["upper"]:
            return lv["label"]
    return conf["levels"][-1]["label"]


def stratum_of(total: int) -> dict:
    if total < CUT_LO:
        return SC["strata"][0]
    if total <= CUT_HI:
        return SC["strata"][1]
    return SC["strata"][2]


st.set_page_config(page_title="GFRS-5 下肢功能风险评分", layout="centered")


def md_safe(text: str) -> str:
    """把区间号 ~ 换成全角波浪号，避免被 Markdown 判成删除线。

    `st.caption` / `st.markdown` / `st.write` 走 GFM 解析，成对的 "~" 会被当作删除线：
    "0.759~0.785" 因此渲染成被划掉的 "0.759 0.785"，波浪号消失、数字上多一条横线。
    真值文件（scorecard.json）与论文、网页保持半角 ~ 不变，只在这一层做显示端转义。
    """
    return text.replace("~", "～")


st.title("GFRS-5 下肢功能风险评分")
st.caption(
    md_safe(
        "Gout Functional Risk Score · 5 项床旁评分 · 适用于 40 岁及以上痛风或高尿酸血症人群 · "
        "分值 0~90，越高风险越高"
    )
)

with st.form("gfrs"):
    c1, c2 = st.columns(2)
    age = c1.number_input("年龄（岁）", 40, 105, 65, 1)
    female = c2.radio("性别", ["男", "女"], horizontal=True) == "女"
    c3, c4 = st.columns(2)
    bmi = c3.number_input("BMI（kg/m²）", 14.0, 60.0, 26.0, 0.1)
    ncm = c4.number_input("共病数（种，不含关节炎）", 0, 9, 2, 1,
                          help="9 类：心力衰竭、冠心病、心绞痛、心肌梗死、卒中、糖尿病、"
                               "慢性肾病、高血压、血脂异常。关节炎已单列一项，请勿重复计入。")
    art = st.radio("关节炎（医师诊断或正在治疗）", ["无", "有"], horizontal=True) == "有"
    submitted = st.form_submit_button("计算评分")

if submitted:
    items = [
        ("年龄", f"{label_for('age', age)} 岁", points_for("age", age)),
        ("性别", "女" if female else "男", points_for("female", int(female))),
        ("BMI", f"{label_for('bmi', bmi)} kg/m²", points_for("bmi", bmi)),
        ("共病数", f"{label_for('ncm', ncm)} 种", points_for("ncm", ncm)),
        ("关节炎", "有" if art else "无", points_for("arthritis", int(art))),
    ]
    total = sum(p for _, _, p in items)
    st_ = stratum_of(total)
    risk4 = 1 / (1 + math.exp(-(A + B * total)))

    st.markdown(f"### 总分：{total} / {SC['total_max']}")
    st.markdown(
        f"### 风险分层：<span style='color:{st_['color']};font-weight:700'>{st_['label']}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**4 年下肢功能衰退风险估计：{risk4 * 100:.1f}%**（CHARLS 再校准）")
    st.progress(min(total / SC["total_max"], 1.0))
    st.info(md_safe(st_["advice"]))

    near = min((CUT_LO, CUT_HI), key=lambda c: abs(total - c))
    if abs(total - near) <= 3:
        st.warning(
            f"总分距 {near} 分切点仅 {abs(total - near)} 分。分层用于确定随访强度，"
            "一次评估的波动即可能改变分层；沟通时宜同时说明分值与连续风险值。"
        )

    with st.expander("分值明细"):
        for name, val, pt in items:
            st.write(md_safe(f"{name}（{val}）：{pt} 分"))
        st.write(f"合计：{total} 分")

    with st.expander("该分层的实际观察风险（CHARLS）"):
        for s in SC["strata"]:
            st.write(f"{s['label']}：4 年 {s['observed_4y']}%｜9 年 {s['observed_9y']}%")

M = SC["model_card"]
st.divider()
st.caption(
    md_safe(
        f"模型卡：{M['development']}；{M['validation']}。"
        f"开发库 AUC {M['auc_dev']}；外部 Harrell C 指数 {M['cindex_ext']}，"
        f"IPCW C 指数 {M['cindex_ipcw']}。变量：{M['variables']}。"
        f"4 年风险换算系数由 CHARLS 数据估计，迁移至其他人群须重新校准。"
    )
)
st.caption(
    "免责声明：本工具仅用于风险分层与随访强度提示，不构成诊断或治疗建议；"
    "不采集姓名、住院号等可识别信息，服务端不持久化任何输入。"
    "如需完全离线的使用环境，请下载随论文补充材料提供的单文件版（全部计算在本机完成）。"
)
st.caption(f"版本 {SC['_meta']['version']}（{SC['_meta']['built']}）· GFRS-5 · "
           "分值表与论文表4 逐项一致")
