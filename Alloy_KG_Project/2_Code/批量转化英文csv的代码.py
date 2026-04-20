import json
import csv
import os

# ================= 配置区域 =================
# 输出的 CSV 文件路径
output_csv = r"C:\Users\pljjswd\Desktop\convert_jsonl\all_data_import.csv"

# 【关键】在这里把你的所有文件都列出来
# 格式：r"文件路径": "属性类型名称"
file_mapping = {
    r"C:\Users\pljjswd\Desktop\convert_jsonl\1.7english.jsonl": "Chemical Composition",       #化学成分
    r"C:\Users\pljjswd\Desktop\convert_jsonl\1.8english.jsonl": "Heat Treatment Regime",      # 热处理制度
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.3english.jsonl": "Thermal Conductivity",       # 热导率
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.4english.jsonl": "Electrical Resistivity",     # 电阻率
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.5english.jsonl": "Thermal Diffusivity",        # 热扩散率
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.6english.jsonl": "Specific Heat Capacity",     # 比热容
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.7english.jsonl": "Linear Expansion Coefficient",# 线膨胀系数
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.9english.jsonl": "Magnetic Properties",        # 磁性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.10english.jsonl": "Elastic Properties",         # 弹性性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.11english.jsonl": "Oxidation Resistance",       # 抗氧化性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\2.12english.jsonl": "Corrosion Resistance",       # 耐腐蚀性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.1english.jsonl": "Hardness",                   # 硬度
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.2english.jsonl": "Impact Properties",          # 冲击性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.3english.jsonl": "Compressive Properties",     # 压缩性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.4english.jsonl": "Torsional Properties",       # 扭转性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.5english.jsonl": "Shear Properties",           # 剪切性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.2.6english.jsonl": "Tensile Properties",         # 拉伸性能
    r"C:\Users\pljjswd\Desktop\convert_jsonl\3.3.1english.jsonl": "Stress Rupture Properties",  # 持久性能
}
# ===========================================

def batch_convert():
    print(f"🚀 开始合并转换，目标文件: {output_csv}")
    
    total_count = 0
    
    # 打开输出的 CSV 文件准备写入
    with open(output_csv, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        
        # 1. 写入表头 (Header)
        # alloy_id: 合金名
        # text: 具体的描述文本
        # prop_type: 属性的具体分类（如化学成分、蠕变等）
        writer.writerow(["alloy_id", "text", "prop_type"])
        
        # 2. 遍历你配置的每一个文件
        for input_file, p_type in file_mapping.items():
            if not os.path.exists(input_file):
                print(f"⚠️ 跳过不存在的文件: {input_file}")
                continue
                
            print(f"📂 正在处理: {os.path.basename(input_file)} -> 类型: {p_type}")
            
            try:
                with open(input_file, "r", encoding="utf-8") as f_in:
                    file_count = 0
                    for line in f_in:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                # 【核心逻辑】写入 CSV 时，把当前的 p_type 带进去
                                writer.writerow([data["id"], data["text"], p_type])
                                file_count += 1
                                total_count += 1
                            except json.JSONDecodeError:
                                continue
                    print(f"   └─ 已写入 {file_count} 条数据")
            except Exception as e:
                print(f"❌ 处理文件出错: {e}")

    print("-" * 30)
    print(f"✅ 所有文件合并完成！")
    print(f"📊 总共生成 {total_count} 条数据。")
    print("❗ 请将生成的 CSV 文件放入 Neo4j 安装目录下的 'import' 文件夹中。")

if __name__ == "__main__":
    batch_convert()