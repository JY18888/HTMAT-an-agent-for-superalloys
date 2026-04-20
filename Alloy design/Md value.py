# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# 读取你的合金数据
df = pd.read_csv("predicted_solvus_and_solidus_with_density.csv")

# 定义元素信息：(原子量, Md)
element_info = {
    'Cr': (52.00, 1.142),
    'Co': (58.93, 0.771),
    'Mo': (95.95, 1.550),
    'W': (183.84, 1.655),
    'Al': (26.98, 1.900),
    'Ti': (47.87, 2.271),
    'Ta': (180.95, 2.224),
    'Re': (186.21, 1.267),
    'Ni': (58.69, 0.717)
}

# 确保所有需要的列存在（缺失则设为 0）
for elem in element_info.keys():
    if elem not in df.columns:
        df[elem] = 0.0
        print(f"⚠️ 警告：'{elem}' 列不存在，已设为 0.0")

# 初始化 Md_bar 列
md_bar_list = []

# 逐行计算（也可向量化，但逐行更清晰）
for idx, row in df.iterrows():
    # 提取质量百分比（wt%）
    wt = {elem: row[elem] for elem in element_info.keys()}

    # 计算摩尔数 = wt% / 原子量
    moles = {}
    total_moles = 0.0
    for elem, (atomic_weight, md_val) in element_info.items():
        moles[elem] = wt[elem] / atomic_weight
        total_moles += moles[elem]

    # 防止除零（理论上不会发生，因为 Ni 至少 >50%）
    if total_moles == 0:
        md_bar = np.nan
    else:
        # 计算原子分数，并加权求和 Md
        md_bar = 0.0
        for elem, (atomic_weight, md_val) in element_info.items():
            x_i = moles[elem] / total_moles  # 原子分数
            md_bar += x_i * md_val
    md_bar_list.append(md_bar)

# 添加到 DataFrame
df['Md_bar_(eV)'] = np.round(md_bar_list, 4)

# 保存结果
output_file = "predicted_solvus_solidus_density_MdStability.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ Microstructure Stability (\u1E42d\u0305) 计算完成！")
print(f"📁 结果已保存至: {output_file}")
print(f"📊 \u1E42d\u0305 范围: {df['Md_bar_(eV)'].min():.4f} ~ {df['Md_bar_(eV)'].max():.4f} eV")
print(f"\n🔍 前5行预览:")
preview_cols = ['Al', 'Ti', 'Co', 'Cr', 'Ta', 'Mo', 'W', 'Re', 'Ni', 'Density_(g/cm3)', 'Md_bar_(eV)']
print(df[preview_cols].head().to_string(index=False))