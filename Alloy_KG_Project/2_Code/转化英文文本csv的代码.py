import json
import csv
import re
import os

# ================= 配置区域 =================
# 你的这个特殊的、混合属性的 jsonl 文件路径
input_file = r"C:\Users\pljjswd\Desktop\convert_jsonl\3文本english.jsonl" 

# 输出的 CSV 文件名
output_csv = r"C:\Users\pljjswd\Desktop\convert_jsonl\文本_data_import.csv"
# ===========================================

def extract_property_type(text):
    """
    核心逻辑：从长文本中智能提取属性类型
    例如： "Density of Alloy GH4090: ..." -> 提取出 "Density"
    """
    # 1. 既然所有数据格式都是 "标题: 内容"，我们先用冒号分割，只看冒号前面
    if ":" in text:
        header = text.split(":", 1)[0].strip()
    else:
        # 如果没有冒号，就拿前5个词作为兜底，或者直接标记为 "General Description"
        return "General Description"

    # 2. 使用正则表达式提取 "of/for/to Alloy" 之前的内容
    # 说明：
    # ^(.*?)     -> 从头开始捕获任意字符（非贪婪模式）
    # \s+        -> 必须有空格
    # (of|for|to)-> 遇到 of 或 for 或 to
    # \s+        -> 空格
    # Alloys?    -> 匹配 Alloy 或者 Alloys
    pattern = r"^(.*?)\s+(of|for|to)\s+Alloys?"
    
    match = re.search(pattern, header, re.IGNORECASE)
    
    if match:
        # 如果匹配成功，返回第一部分（即属性名）
        return match.group(1).strip()
    else:
        # 如果没找到 "of Alloy" 这种关键字，直接把冒号前的整个标题作为属性名
        # 比如 "Summary:" -> "Summary"
        return header.strip()

def main():
    print(f"🚀 开始智能解析，目标文件: {output_csv}")
    
    count = 0
    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_csv, "w", encoding="utf-8", newline="") as f_out:
        
        writer = csv.writer(f_out)
        # 保持和之前完全一样的表头，这样 Neo4j 的代码通用！
        writer.writerow(["alloy_id", "text", "prop_type"])
        
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                raw_text = data["text"]
                alloy_id = data["id"]
                
                # 【调用智能提取函数】
                prop_type = extract_property_type(raw_text)
                
                # 写入 CSV
                writer.writerow([alloy_id, raw_text, prop_type])
                count += 1
                
                # 打印前几条看看效果，确保提取正确
                if count <= 5:
                    print(f"   [示例] 提取到类型: 【{prop_type}】")
                    
            except json.JSONDecodeError:
                continue
                
    print("-" * 30)
    print(f"✅ 转换完成！生成了 {count} 条数据。")
    print(f"📂 文件位置: {output_csv}")
    print("❗ 请将此 CSV 放入 Neo4j 的 import 文件夹。")

if __name__ == "__main__":
    main()