# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import warnings

warnings.filterwarnings('ignore')

# ==============================
# 🔧 配置路径（请根据实际情况确认）
# ==============================
CANDIDATE_FILE = "design_space_with_Ni.csv"  # 候选合金（含 Al, Ti, ..., Ni）

SOLVUS_DATA = "solvus(γ′溶剂温度).xlsx"
SOLIDUS_DATA = r"E:\AAAAA新学术科研\二代S1单晶高温合金+NLP\aaa成分设计\熔点数据集.xlsx"

OUTPUT_FILE = "predicted_solvus_and_solidus_for_all_alloys.csv"

# ==============================
# 📥 加载候选合金
# ==============================
print("📥 正在加载候选合金成分...")
candidates = pd.read_csv(CANDIDATE_FILE)
print(f"✅ 共 {len(candidates)} 种候选合金")
print(f"   当前包含元素: {list(candidates.columns)}")


# ==============================
# 🛠️ 工具函数：对齐特征（缺失列自动补 0）
# ==============================
def align_features(df, required_features):
    """确保 df 包含 required_features 中所有列，缺失的设为 0.0，并按顺序排列"""
    df_out = df.copy()
    missing_cols = []
    for col in required_features:
        if col not in df_out.columns:
            df_out[col] = 0.0
            missing_cols.append(col)
    if missing_cols:
        print(f"   ⚠️ 补充缺失特征（设为 0.0）: {missing_cols}")
    return df_out[required_features]


# ==============================
# 🛠️ 训练模型通用函数
# ==============================
def train_svr_model(data_path, target_col_candidates, model_name):
    print(f"\n🔄 正在准备 {model_name} 预测模型...")
    data = pd.read_excel(data_path)

    # 删除元信息列
    cols_to_drop = ['DOIs', 'material', 'Unit', 'other_property_info']
    cols_to_drop = [c for c in cols_to_drop if c in data.columns]
    data = data.drop(columns=cols_to_drop, errors='ignore')
    data.fillna(0, inplace=True)

    # 删除全零列
    all_zero_cols = data.columns[(data == 0).all()]
    data = data.drop(columns=all_zero_cols, errors='ignore')

    # 查找目标列
    target_col = None
    for col in target_col_candidates:
        if col in data.columns:
            target_col = col
            break
    if target_col is None:
        raise ValueError(f"❌ 未找到目标列！尝试了: {target_col_candidates}")

    print(f"   使用目标列: '{target_col}'")
    y_raw = data[target_col].values
    X_raw = data.drop(columns=[target_col])
    feature_names = list(X_raw.columns)
    print(f"   特征数: {len(feature_names)} | 样本数: {len(y_raw)}")
    print(f"   特征列表: {feature_names}")

    # 标准化
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    X_scaled = scaler_X.fit_transform(X_raw)
    y_scaled = scaler_y.fit_transform(y_raw.reshape(-1, 1)).flatten()

    # 网格搜索
    param_grid = {
        "C": [0.1, 1, 10, 100, 1000],
        "gamma": [1e-7, 1e-4, 1e-3, 1e-2]
    }
    svr = SVR(kernel='rbf')
    gs = GridSearchCV(svr, param_grid, cv=5, scoring='r2', n_jobs=1, verbose=0)
    gs.fit(X_scaled, y_scaled)

    print(f"   ✅ {model_name} 模型训练完成！最佳 CV R²: {gs.best_score_:.4f}")
    return gs.best_estimator_, scaler_X, scaler_y, feature_names


# ==============================
# 🧪 训练两个模型
# ==============================
# γ' 溶解温度
solvus_targets = ["solvus temperature (℃)", "solvus temperature(℃)", "γ' solvus (℃)"]
solvus_model, solvus_scaler_X, solvus_scaler_y, solvus_feats = train_svr_model(
    SOLVUS_DATA, solvus_targets, "γ' 溶解温度 (solvus)"
)

# 固相线温度
solidus_targets = [
    'solidus temperature(℃)',
    'solidus temperature (℃)',
    'solidus temperature(°C)',
    'solidus temperature (°C)',
    'solidus temperature'
]
solidus_model, solidus_scaler_X, solidus_scaler_y, solidus_feats = train_svr_model(
    SOLIDUS_DATA, solidus_targets, "固相线温度 (solidus)"
)

# ==============================
# 🔧 对齐候选合金与模型所需特征
# ==============================
print("\n🔧 正在对齐候选合金与模型特征（缺失元素自动设为 0）...")
candidates_solvus = align_features(candidates, solvus_feats)
candidates_solidus = align_features(candidates, solidus_feats)

# ==============================
# 🔮 批量预测
# ==============================
print("\n🔮 正在预测所有候选合金的 γ' 溶解温度 和 固相线温度...")

# γ' 溶解温度
X_solvus_scaled = solvus_scaler_X.transform(candidates_solvus)
y_solvus_pred = solvus_scaler_y.inverse_transform(
    solvus_model.predict(X_solvus_scaled).reshape(-1, 1)
).flatten()

# 固相线温度
X_solidus_scaled = solidus_scaler_X.transform(candidates_solidus)
y_solidus_pred = solidus_scaler_y.inverse_transform(
    solidus_model.predict(X_solidus_scaled).reshape(-1, 1)
).flatten()

# ==============================
# 💾 保存结果
# ==============================
result_df = candidates.copy()
result_df["Predicted_γ'_Solvus_Temperature(℃)"] = np.round(y_solvus_pred, 2)
result_df["Predicted_Solidus_Temperature(℃)"] = np.round(y_solidus_pred, 2)
result_df["γ'_Phase_Field_Width(℃)"] = (
        result_df["Predicted_Solidus_Temperature(℃)"] - result_df["Predicted_γ'_Solvus_Temperature(℃)"]
)

# 按 γ' 相温区宽度降序排序（优先高工艺窗口合金）
result_df = result_df.sort_values("γ'_Phase_Field_Width(℃)", ascending=False)

# 保存
result_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"\n🎉 预测成功完成！")
print(f"📁 结果已保存至: {os.path.abspath(OUTPUT_FILE)}")
print(f"📊 总行数: {len(result_df):,}")

# 显示前5行
preview_cols = [
    'Al', 'Ti', 'Co', 'Cr', 'Ta', 'Mo', 'W', 'Re', 'Ni',
    "Predicted_γ'_Solvus_Temperature(℃)",
    "Predicted_Solidus_Temperature(℃)",
    "γ'_Phase_Field_Width(℃)"
]
print("\n🔍 前5行结果预览:")
print(result_df[preview_cols].head().to_string(index=False))