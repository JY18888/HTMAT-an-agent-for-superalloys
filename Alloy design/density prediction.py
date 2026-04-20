# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# 读取你的合金设计空间文件
df = pd.read_csv("predicted_solvus_and_solidus_for_all_alloys.csv")

# 确保所需元素列存在（若缺失则设为 0）
required_elements = ['Co', 'Cr', 'Mo', 'W', 'Re', 'Al', 'Ti', 'Ta']
for elem in required_elements:
    if elem not in df.columns:
        df[elem] = 0.0
        print(f"⚠️ 警告：'{elem}' 列不存在，已设为 0.0")

# Ru 在二代单晶中通常为 0
c_Ru = 0.0

# 应用密度公式（向量化计算，极快）
rho = (
    8.939
    - 0.0014 * df['Co']
    - 0.0197 * df['Cr']
    + 0.0125 * df['Mo']
    + 0.0436 * df['W']
    + 0.0508 * df['Re']
    + 0.0194 * c_Ru          # = 0
    - 0.1281 * df['Al']
    - 0.0498 * df['Ti']
    + 0.0409 * df['Ta']
)

# 添加密度列（保留 4 位小数）
df['Density_(g/cm3)'] = np.round(rho, 4)

# 保存回原文件（或另存为新文件）
output_file = "predicted_solvus_and_solidus_with_density.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ 密度计算完成！")
print(f"📁 结果已保存至: {output_file}")
print(f"📊 密度范围: {df['Density_(g/cm3)'].min():.4f} ~ {df['Density_(g/cm3)'].max():.4f} g/cm³")
print(f"\n🔍 前5行预览:")
print(df[['Al', 'Ti', 'Co', 'Cr', 'Ta', 'Mo', 'W', 'Re', 'Density_(g/cm3)']].head().to_string(index=False))