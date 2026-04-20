#!/usr/bin/env python3
# evaluate_rag_enhanced.py - 强化版 RAG 评估脚本（60题）
# 重点解决：中文元素名 → 英文符号、摄氏度→℃、同义词标准化等问题

import requests
import csv
import time
import os
from rag_retriever import search

# ===== 配置 =====
API_URL = "http://127.0.0.1:8000/v1/chat/completions"
MODEL_NAME = "Qwen3-8B"

# === 基础40题 ===
BASE_QA = [
    {"question": "合金GH4413中元素W的质量分数是多少？", "ground_truth": "5.00～7.00%"},
    {"question": "合金DD406中元素Al的质量分数是多少？", "ground_truth": "5.20～6.20%"},
    {"question": "合金GH4500中元素P的质量分数是多少？", "ground_truth": "≤0.015%"},
    {"question": "合金DD407中元素Cr的质量分数是多少？", "ground_truth": "7.80～8.30%"},
    {"question": "合金K406中元素Ti的质量分数是多少？", "ground_truth": "2.00～3.00%"},
    {"question": "合金DD426中元素Co的质量分数是多少？", "ground_truth": "8.00～10.0%"},
    {"question": "合金DD432中元素Ta的质量分数是多少？", "ground_truth": "3.50～4.50%"},
    {"question": "合金DZ406中元素Hf的质量分数是多少？", "ground_truth": "1.30～1.70%"},
    {"question": "合金GH4708中元素Cr的质量分数是多少？", "ground_truth": "17.50～20.00%"},
    {"question": "合金FGH4095中元素Nb的质量分数是多少？", "ground_truth": "3.30～3.70%"},
    {"question": "合金 GH3030 在400℃的热导率是多少？", "ground_truth": "19.3 W/(m·℃)"},
    {"question": "合金 K414 在100℃的热导率是多少？", "ground_truth": "11.3 W/(m·℃)"},
    {"question": "合金 GH3039 在900℃的热导率是多少？", "ground_truth": "26.8 W/(m·℃)"},
    {"question": "合金 GH3128 在1150℃的电阻率是多少？", "ground_truth": "1.39*10^(-6)Ω·m"},
    {"question": "合金 FGH4095 在700℃的电阻率是多少？", "ground_truth": "1.603*10^(-6)Ω·m"},
    {"question": "合金 GH3128 在900℃的热扩散率是多少？", "ground_truth": "4.16*10^(-6) m^2/s"},
    {"question": "合金 K444 在1000℃的热扩散率是多少？", "ground_truth": "4.71*10^(-6) m^2/s"},
    {"question": "合金 GH1180 在800℃的电阻率是多少？", "ground_truth": "1.25*10^(-6)Ω·m"},
    {"question": "合金 GH3030 在150℃的比热容是多少？", "ground_truth": "565.2 J/(kg·℃)"},
    {"question": "合金 K418 在100℃的比热容是多少？", "ground_truth": "439.0 J/(kg·℃)"},
    {"question": "合金 GH4742 在热处理为1150℃×8h/AC时的室温冲击韧性是多少？", "ground_truth": "1600kJ/m^2"},
    {"question": "合金 K417 在20~100℃的线膨胀系数是多少？", "ground_truth": "13.2*10^(-6) ℃^(-1)"},
    {"question": "合金 K414 在300℃的切变模量G是多少？", "ground_truth": "71.5GPa"},
    {"question": "合金 GH3039 在700℃的动态弹性模量ED是多少？", "ground_truth": "162.0GPa"},
    {"question": "合金 GH3170 在700℃的泊松比μ是多少？", "ground_truth": "0.35"},
    {"question": "合金GH3030在空气介质、900℃试验100h的氧化速率是多少？", "ground_truth": "0.0535g/(m2·h)"},
    {"question": "合金GH3044在空气介质、900℃试验100h的氧化速率是多少？", "ground_truth": "0.0971g/(m2·h)"},
    {"question": "合金DD407在空气介质、900℃试验50h的氧化速率是多少？", "ground_truth": "0.039g/(m2·h)"},
    {"question": "合金 GH3030，取样为δ1.5冷轧板 供应状态，在300℃的拉伸强度σb是多少？", "ground_truth": "708MPa"},
    {"question": "合金 GH3181，取样为90方坯 标准热处理，在600℃的拉伸强度σb是多少？", "ground_truth": "713MPa"},
    {"question": "合金 GH4586 的应用概况及特性是什么？", "ground_truth": "该合金是我国自行研制具有自主知识产权的一种高性能高温合金涡轮盘材料，已用于制作航空、航天等领域发动机用耐热承力件，包括液氧/煤油火箭发动机用涡轮转子以及多种型号航天发动机涡轮转子模锻件，使用情况良好。"},
    {"question": "合金 GH4049 的熔化温度范围是多少？", "ground_truth": "1320℃～1390℃。"},
    {"question": "合金 K403 的概述是什么？", "ground_truth": "K403 是镍基沉淀硬化型等轴晶铸造高温合金，合金由多种金属元素进行综合强化，使用温度在1000℃ 以下。合金具有较高的高温强度，在1000℃、100h的持久强度可达150MPa、1000h的持久强度可达94MPa。合金的铸造性能良好，可铸出形状复杂的精铸件，适合于制作1000℃以下工作的燃气涡轮导向叶片和900℃以下工作的涡轮转子叶片及其他零件。"},
    {"question": "合金 GH2901 的相近牌号有哪些？", "ground_truth": "Incoloy901(美)，Nimonic901(英)，Z8NCDT42(法)，2·4662(德)。"},
    {"question": "合金 DD432 的热处理制度是什么？", "ground_truth": "摘自Q/KJ.J02.32，合金的标准热处理制度为：1290℃×4h/AC+1280℃×4h/AC+1150℃×4h/AC+870℃×24h/AC。"},
    {"question": "合金 GH6783 的相近牌号是什么？", "ground_truth": "Inconel 783（美）。"},
    {"question": "合金 K480 的热处理制度是什么？", "ground_truth": "摘自HB/Z 140，合金的标准热处理制度为： 1220℃±10℃×2h/AC+1090℃±10℃×4h/AC+1050℃±10℃×4h/AC+840℃±10℃×16h/AC。"},
    {"question": "合金 K480 的熔化温度范围是多少？", "ground_truth": "1270℃~1320℃"},
    {"question": "合金 K444 的成型工艺与性能如何？", "ground_truth": "合金的铸造性能良好，用熔模铸造法可铸成复杂的薄壁空心叶片，铸造线收缩率约为1.9%。"},
    {"question": "合金 GH4169 的相近牌号有哪些？", "ground_truth": "Inconel 718(美)，NC19FeNb（法）。"}
]

# === 新增20个复杂扰动题 ===
COMPLEX_QA = [
    {"question": "合金 GH3030 在400摄氏度的热导率是多少？", "ground_truth": "19.3 W/(m·℃)"},
    {"question": "GH3128 在一千一百五十摄氏度下的电阻率是多少？", "ground_truth": "1.39*10^(-6)Ω·m"},
    {"question": "K414 在100℃时的热导率，单位用瓦每米摄氏度表示是多少？", "ground_truth": "11.3 W/(m·℃)"},
    {"question": "GH3030 在900℃氧化100小时的氧化速率是多少克每平方米每小时？", "ground_truth": "0.0535g/(m2·h)"},
    {"question": "DD406 合金里铝元素的质量百分比范围是多少？", "ground_truth": "5.20～6.20%"},
    {"question": "FGH4095 中铌的含量是多少？", "ground_truth": "3.30～3.70%"},
    {"question": "GH3181 在600℃下的抗拉强度σb是多少兆帕？", "ground_truth": "713MPa"},
    {"question": "K417 从20度到100度之间的热膨胀系数是多少？", "ground_truth": "13.2*10^(-6) ℃^(-1)"},
    {"question": "DD432 合金的标准热处理工艺是什么？（参考标准 Q/KJ.J02.32）", "ground_truth": "摘自Q/KJ.J02.32，合金的标准热处理制度为：1290℃×4h/AC+1280℃×4h/AC+1150℃×4h/AC+870℃×24h/AC。"},
    {"question": "GH4169 对应的美国和法国牌号分别是什么？", "ground_truth": "Inconel 718(美)，NC19FeNb（法）。"},
    {"question": "GH3044 在空气中900℃暴露100小时后的氧化增重速率是多少？", "ground_truth": "0.0971g/(m2·h)"},
    {"question": "GH3039 在700℃时的动态弹性模量 Ed 是多少吉帕？", "ground_truth": "162.0GPa"},
    {"question": "GH3170 在700℃时的泊松比 mu 是多少？", "ground_truth": "0.35"},
    {"question": "K414 在300℃时的剪切模量 G 是多少？", "ground_truth": "71.5GPa"},
    {"question": "GH4742 经过1150℃保温8小时空冷后的室温冲击功是多少千焦每平方米？", "ground_truth": "1600kJ/m^2"},
    {"question": "K480 合金的熔点区间是多少摄氏度？", "ground_truth": "1270℃~1320℃"},
    {"question": "GH4586 主要用在哪些航空航天部件上？", "ground_truth": "该合金是我国自行研制具有自主知识产权的一种高性能高温合金涡轮盘材料，已用于制作航空、航天等领域发动机用耐热承力件，包括液氧/煤油火箭发动机用涡轮转子以及多种型号航天发动机涡轮转子模锻件，使用情况良好。"},
    {"question": "K444 合金适合用什么方法铸造？线收缩率大约多少？", "ground_truth": "合金的铸造性能良好，用熔模铸造法可铸成复杂的薄壁空心叶片，铸造线收缩率约为1.9%。"},
    {"question": "K403 合金在1000℃下持续100小时的持久强度能达到多少兆帕？", "ground_truth": "150MPa"},
    {"question": "GH4500 中磷的最大允许含量是多少？", "ground_truth": "≤0.015%"}
]

TEST_QA = BASE_QA + COMPLEX_QA  # 共60题

# === 调用大模型 ===
def call_qwen(messages, max_tokens=512):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "[ERROR] Model response format invalid"
    except Exception as e:
        return f"[ERROR] {str(e)}"

# === 强化版 Query Rewriting（核心改进）===
def rewrite_query_to_symbols(query):
    prompt = (
        "你是一位高温合金数据检索专家，请将用户问题改写为标准数据库查询语句。\n\n"
        "【标准化映射表 - 必须使用】\n"
        "元素：铝→Al, 铌→Nb, 铬→Cr, 钨→W, 钴→Co, 钽→Ta, 铪→Hf, 磷→P, 钛→Ti, 镍→Ni, 铁→Fe\n"
        "温度：摄氏度/度 → ℃\n"
        "时间：小时 → h\n"
        "力学性能：抗拉强度/拉伸强度 → 拉伸强度σb；剪切模量/切变模量 → 切变模量G；弹性模量 → 动态弹性模量ED；热膨胀系数 → 线膨胀系数\n"
        "单位：瓦每米摄氏度 → W/(m·℃)；欧姆·米 → Ω·m；吉帕 → GPa；千焦每平方米 → kJ/m²\n\n"
        "【改写要求】\n"
        "1. 将问题中的中文术语替换为上表对应的标准符号\n"
        "2. 中文数字（如'一千一百五十'）转为阿拉伯数字（1150）\n"
        "3. 只输出改写后的查询语句，不要任何其他文字\n"
        "4. 如果不确定如何转换，保留原词\n\n"
        "用户问题: " + query
    )
    messages = [{"role": "user", "content": prompt}]
    rewritten = call_qwen(messages, max_tokens=120)
    
    # 安全过滤：防止模型输出非查询内容
    if not rewritten or len(rewritten) > 200 or any(w in rewritten for w in ["我", "你", "请", "注意", "例如", "比如", "答", "根据", "输出"]):
        rewritten = query

    # 规则兜底：确保关键术语被替换（双重保险）
    rules = {
        "铝": "Al", "铌": "Nb", "铬": "Cr", "钨": "W", "钴": "Co",
        "钽": "Ta", "铪": "Hf", "磷": "P", "钛": "Ti", "镍": "Ni", "铁": "Fe",
        "摄氏度": "℃", "度": "℃", "小时": "h",
        "抗拉强度": "拉伸强度σb", "拉伸强度": "拉伸强度σb",
        "剪切模量": "切变模量G", "切变模量": "切变模量G",
        "弹性模量": "动态弹性模量ED", "热膨胀系数": "线膨胀系数",
        "瓦每米摄氏度": "W/(m·℃)", "欧姆·米": "Ω·m", "吉帕": "GPa", "千焦每平方米": "kJ/m²"
    }
    for zh, en in rules.items():
        rewritten = rewritten.replace(zh, en)
    
    # 处理中文数字（简单场景）
    num_map = {"一千一百五十": "1150", "九百": "900", "七百": "700", "六百": "600", "四百": "400"}
    for zh_num, num in num_map.items():
        rewritten = rewritten.replace(zh_num, num)
    
    return rewritten.strip()[:150]

# === 三种评估模式 ===
def pure_qwen(question):
    return call_qwen([{"role": "user", "content": question}])

def pure_rag(question):
    results = search(question, k=3)
    return "\n".join([r["content"] for r in results]) if results else "[NO RETRIEVAL]"

def qwen_plus_rag(question):
    rewritten = rewrite_query_to_symbols(question)
    results = search(rewritten, k=3)
    context = "\n".join([r["content"] for r in results]) if results else "（无相关资料）"
    system_prompt = (
        "你是一位高温合金领域的专家，请严格基于以下参考资料回答问题。\n"
        "如果参考资料无法回答该问题，请明确说明“根据现有资料无法回答”。\n\n"
        f"参考资料：\n{context}"
    )
    return call_qwen([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ])

# === 主程序 ===
def main():
    print("🚀 启动强化版 RAG 评估（60题，含元素符号标准化）...")
    print(f"📊 共 {len(TEST_QA)} 个问题 | 模型: {MODEL_NAME}")
    print("⏳ 预计耗时：15~25 分钟\n")

    output_file = "rag_evaluation_enhanced_60q.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Question", "Ground_Truth",
            "Pure_Qwen", "Pure_RAG", "Qwen+RAG_Enhanced"
        ])

    for i, item in enumerate(TEST_QA, start=1):
        q = item["question"]
        gt = item["ground_truth"]
        print(f"[{i}/60] Running: {q[:50]}...")

        ans1 = pure_qwen(q)
        time.sleep(0.5)
        ans2 = pure_rag(q)
        time.sleep(0.5)
        ans3 = qwen_plus_rag(q)
        time.sleep(1)

        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([i, q, gt, ans1, ans2, ans3])

    print(f"\n✅ 评估完成！结果保存至: {os.path.abspath(output_file)}")
    print("\n🔍 重点关注：")
    print("- ID 41~60：Qwen+RAG_Enhanced 应显著优于 Pure_RAG")
    print("- 检查 '铝'→'Al', '摄氏度'→'℃' 是否成功转换")

if __name__ == "__main__":
    main()