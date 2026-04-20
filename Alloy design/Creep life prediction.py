# -*- coding: utf-8 -*-
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ==============================
# Step 1: 加载蠕变训练数据
# ==============================
train_data = pd.read_excel(r"predicted_solvus_temperatures.xlsx", engine='openpyxl')
print("✅ 训练数据列:", list(train_data.columns))
print(f"📊 训练样本数: {len(train_data)}")

# 定义输入特征
feature_cols = [
    'T', 'Stress', 'Ni', 'Al', 'Co', 'Cr', 'Mo', 'Re', 'Ti', 'Ta', 'W', 'Hf', 'Nb',
    'predicted_solvus_temperature (℃)'
]

X_train_raw = train_data[feature_cols]
y_train_raw = train_data['Creep_life']

# 对目标取对数（避免极端值影响）
y_train_log = np.log(y_train_raw + 1e-6)

# 标准化特征
X_mean = X_train_raw.mean()
X_std = X_train_raw.std()
X_train = (X_train_raw - X_mean) / X_std

# ==============================
# Step 2: 构建模型
# ==============================
model = tf.keras.Sequential([
    tf.keras.layers.Dense(14, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001), input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# ==============================
# Step 3: 训练模型（静默模式减少输出干扰）
# ==============================
print("\n🔄 开始训练蠕变寿命模型（epochs=200）...")
history = model.fit(
    X_train.values, y_train_log.values,
    epochs=200,
    batch_size=2,
    verbose=0  # 关闭逐 epoch 输出，最后统一评估
)

# ==============================
# Step 4: 评估训练性能（在训练集上）
# ==============================
y_train_pred_log = model.predict(X_train.values, verbose=0).flatten()
y_train_pred = np.exp(y_train_pred_log)  # 逆对数

# 计算指标（在原始尺度上评估）
r2 = r2_score(y_train_raw, y_train_pred)
mae = mean_absolute_error(y_train_raw, y_train_pred)
rmse = np.sqrt(mean_squared_error(y_train_raw, y_train_pred))

print("\n🔍 模型在训练集上的性能:")
print(f"   R² Score     : {r2:.4f}")
print(f"   MAE (小时)   : {mae:.2f}")
print(f"   RMSE (小时)  : {rmse:.2f}")

# 判断是否继续
if r2 < 0.3:
    print("\n⚠️ 警告：模型 R² 过低 (<0.3)，预测结果可能不可靠！")
    proceed = input("是否仍要继续预测？(y/n): ").strip().lower()
    if proceed != 'y':
        print("🛑 预测已中止。")
        exit()
else:
    print("✅ 模型表现尚可，继续预测新合金...")

# ==============================
# Step 5: 加载新合金数据（由你的 SVR 脚本生成）
# ==============================
new_data = pd.read_csv("predicted_solvus_and_solidus_for_all_alloys.csv")
print(f"\n📥 新合金数据: {len(new_data)} 条")

# ==============================
# Step 6: 构建完整输入（补 Hf/Nb=0，重命名 solvus 列）
# ==============================
TARGET_TEMP = 1100    # ← 修改为你关心的温度
TARGET_STRESS = 137  # ← 修改为你关心的应力

X_new = pd.DataFrame(0.0, index=new_data.index, columns=feature_cols)

# 填充成分
element_map = ['Ni', 'Al', 'Co', 'Cr', 'Mo', 'Re', 'Ti', 'Ta', 'W']
for col in element_map:
    if col in new_data.columns:
        X_new[col] = new_data[col]

# Hf, Nb 设为 0（二代单晶通常不含）
X_new['Hf'] = 0.0
X_new['Nb'] = 0.0

# 重命名溶解温度列
X_new['predicted_solvus_temperature (℃)'] = new_data["Predicted_γ'_Solvus_Temperature(℃)"]

# 设置工况
X_new['T'] = TARGET_TEMP
X_new['Stress'] = TARGET_STRESS

# ==============================
# Step 7: 预测
# ==============================
X_new_scaled = (X_new - X_mean) / X_std
y_pred_log = model.predict(X_new_scaled, verbose=0).flatten()
y_pred = np.exp(y_pred_log)

# ==============================
# Step 8: 保存结果
# ==============================
result_df = new_data.copy()
result_df[f'Predicted_Creep_Life_{TARGET_TEMP}C_{TARGET_STRESS}MPa'] = np.round(y_pred, 2)

output_file = f'蠕变寿命预测_{TARGET_TEMP}C_{TARGET_STRESS}MPa_with_eval.xlsx'
result_df.to_excel(output_file, index=False, engine='openpyxl')

print(f"\n🎉 预测完成！结果已保存至:\n📁 {output_file}")
print(f"\n📈 最高预测寿命: {y_pred.max():.1f} 小时")
print(f"📉 最低预测寿命: {y_pred.min():.1f} 小时")