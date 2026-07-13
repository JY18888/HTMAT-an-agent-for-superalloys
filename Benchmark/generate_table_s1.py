"""Generate Table S1: per-question benchmark results.
Matches bench_final_1000.py logic EXACTLY."""
import json, re, time, math, sys, os, numpy as np
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import requests
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

API_URL = 'https://api.deepseek.com/v1/chat/completions'
API_KEY = 'sk-e57e9f9b3fc04b669655e557a47b9daf'
MODEL_NAME = 'deepseek-chat'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

print('Loading models and data...')
from sentence_transformers import SentenceTransformer
emb_model = SentenceTransformer('.cache/huggingface/models--BAAI--bge-small-en-v1.5')

KB_DIR = 'knowledge_data'
docs = []
for fname in sorted(os.listdir(KB_DIR)):
    if not fname.endswith('.jsonl'): continue
    with open(os.path.join(KB_DIR, fname), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                docs.append((obj.get('id','').strip(), obj.get('text','').strip(), fname))
            except: pass

with open('doc_embeddings_cache.json', 'r') as f:
    doc_embs = np.array(json.load(f)['embeddings'], dtype=np.float32)
norms = np.linalg.norm(doc_embs, axis=1, keepdims=True)
doc_embs = doc_embs / np.maximum(norms, 1e-10)

alloy_to_indices = defaultdict(list)
for i, (aid,_,_) in enumerate(docs):
    alloy_to_indices[aid].append(i)

with open('qa_pairs_cleaned_v3.jsonl', 'r', encoding='utf-8') as f:
    qa_pairs = [json.loads(line) for line in f if line.strip()]

test_qas = qa_pairs[:900]
print(f'{len(test_qas)} questions, {len(docs)} docs')

# ── Tokenization & BM25 ──
def tokenize(text):
    tokens = re.findall(r'[a-z0-9αβγδεζηθικλμνξπρστυφχψωσψ≥≤±°℃%]+', text.lower())
    return [t for t in tokens if len(t) >= 1]
doc_tokens = [tokenize(d[1]) for d in docs]
df = Counter()
for tokens in doc_tokens:
    for t in set(tokens): df[t] += 1
N = len(docs)
idf = {t: math.log((N-d+0.5)/(d+0.5)+1.0) for t, d in df.items()}
avgdl = np.mean([len(t) for t in doc_tokens])
k1, b_bm = 1.5, 0.75

def bm25_score(q_tokens, doc_idx):
    doc_toks = doc_tokens[doc_idx]; dl = len(doc_toks)
    if dl == 0: return 0.0
    tf = Counter(doc_toks); score = 0.0
    for token in set(q_tokens):
        if token not in idf or token not in tf: continue
        tf_d = tf[token]
        score += idf[token] * tf_d * (k1+1) / (tf_d + k1*(1-b_bm+b_bm*dl/avgdl))
    return score

# ── Property keyword map (from original) ──
PROP_KW = {
    'Tensile': ['tensile strength', 'σb'],
    'Yield': ['yield strength', 'σp0.2', 'σp0.1', 'σp0.01', 'σp'],
    'Elongation': ['elongation', 'δ5', 'δ'],
    'Reduction': ['reduction of area', 'ψ', 'φ'],
    'Rupture': ['rupture', 'σ100', 'σ500', 'σ1000', 'σ50', 'σ30', 'σ10',
                'σ200', 'σ300', 'σ5000', 'σ10000', 'σ1500', 'σ3000'],
    'Mass Fraction': ['mass fraction'],
    'Thermal': ['thermal conductivity'],
    'Specific Heat': ['specific heat', 'cp', 'specific heat capacity'],
    'Linear Expansion': ['linear expansion', 'thermal expansion', 'cte', 'α'],
    'Density': ['density', 'ρ'],
    'Hardness': ['hardness', 'hb', 'hrc', 'hv'],
    'Elastic Modulus': ['elastic modulus', "e'", 'young'],
    'Shear Modulus': ['shear modulus'],
    'Poisson': ['poisson', 'ν'],
    'Impact': ['impact toughness', 'akv', 'aku'],
    'Creep Rupture Time': ['creep rupture time'],
    'Melting': ['melting', 'solidus', 'liquidus'],
    'Oxidation': ['oxidation'],
    'Resistivity': ['resistivity'],
    'Magnetic': ['magnetic', 'curie'],
    'Thermal Diffusivity': ['thermal diffusivity'],
    'Heat Treatment': ['heat treatment', 'solution', 'aging', 'annealing'],
    'Forming Process': ['forming process', 'forging', 'hot working'],
    'Melting Process': ['melting process', 'vacuum induction'],
    'Welding': ['welding', 'weldability'],
    'Machining': ['machining', 'machinability'],
    'Product Specification': ['product specification'],
    'Material Grade': ['material grade'],
}

def get_kws(prop_name):
    prop_lower = prop_name.lower()
    for group, kws in PROP_KW.items():
        for kw in kws:
            if kw.lower() in prop_lower: return group
    return 'Other'

# ── Helpers ──
def extract_temps(text):
    return [int(t) for t in re.findall(r'(\d+)\s*(?:℃|°C|°\s*C)', text)]

def extract_times(text):
    return [int(t) for t in re.findall(r'(?<!\d)(\d+)\s*h', text.lower())]

# ── Original check_correct ──
def check_correct(ans, gt):
    gt_s = str(gt).strip(); ans_s = str(ans).strip()
    if ans_s.startswith('[API_ERROR'): return False

    gt_nums = re.findall(r'[\d.]+', gt_s)
    gt_nums = [n for n in gt_nums if n != '.' and len(n.replace('.',''))>=1]

    if gt_nums:
        range_match = re.search(r'([\d.]+)\s*(?:℃|°C)?\s*[~～]\s*([\d.]+)', gt_s)
        if range_match:
            lo, hi = float(range_match.group(1)), float(range_match.group(2))
            ans_range = re.search(r'([\d.]+)\s*(?:℃|°C)?\s*[~～]\s*([\d.]+)', ans_s)
            if ans_range:
                alo, ahi = float(ans_range.group(1)), float(ans_range.group(2))
                if alo <= hi and ahi >= lo:
                    if abs(alo-lo)/(max(lo,1)) < 0.15 and abs(ahi-hi)/(max(hi,1)) < 0.15:
                        return True
            ans_nums = [float(n) for n in re.findall(r'[\d.]+', ans_s)
                       if n != '.' and len(n.replace('.',''))>=1]
            for an in ans_nums:
                if lo <= an <= hi: return True
        if len(gt_nums) >= 3:
            matched = sum(1 for n in gt_nums[:3] if n in ans_s)
            if matched >= 2: return True
        if gt_nums[0] in ans_s: return True
        for n in gt_nums[:3]:
            if n in ans_s: return True
        return False

    # Text matching
    ans_l = ans_s.lower(); gt_l = gt_s.lower()
    if gt_l == ans_l: return True
    if len(gt_l) > 15 and gt_l in ans_l: return True
    if len(ans_l) > 15 and ans_l in gt_l: return True
    if len(gt_l) >= 20 and gt_l[:20] in ans_l: return True
    if len(ans_l) >= 20 and ans_l[:20] in gt_l: return True
    gt_words = set(gt_l.split()); ans_words = set(ans_l.split())
    if len(gt_words) >= 3:
        overlap = len(gt_words & ans_words)
        if overlap >= min(3, len(gt_words) * 0.4): return True
    elif len(gt_words) >= 1:
        if len(gt_words & ans_words) >= max(1, len(gt_words) * 0.5): return True
    if len(gt_l) > 30:
        ratio = SequenceMatcher(None, gt_l[:200], ans_l[:200]).ratio()
        if ratio > 0.65: return True
    for s in ['non-magnetic', 'no special', 'as-cast', 'same as the standard',
              'vacuum', 'solution treatment', 'air cool', 'water quench',
              'argon', 'forced', 'diffusion', 'excerpted from',
              'gb/t', 'gjb', 'hb 7763', 'hb/z',
              'standard heat treatment', 'each product', 'each product form']:
        if s in gt_l and s in ans_l: return True
    return False

# ── Original retrieval functions ──
def plain_vector_retrieve(question, alloy_str, top_k=3):
    q_emb = emb_model.encode([question], normalize_embeddings=True)[0]
    if alloy_str and alloy_str in alloy_to_indices:
        indices = alloy_to_indices[alloy_str]
        scores = np.dot(doc_embs[indices], q_emb)
        top_local = np.argsort(scores)[::-1][:top_k]
        return [indices[i] for i in top_local]
    scores = np.dot(doc_embs, q_emb)
    return np.argsort(scores)[::-1][:top_k].tolist()

def hybrid_retrieve(question, prop_name, alloy_str, top_k=8):
    q_tokens = tokenize(question)
    q_emb = emb_model.encode([question], normalize_embeddings=True)[0]
    search_indices = set()
    for a in re.split(r'\s+and\s+|\s*&\s*|[,，]', alloy_str or ''):
        a = a.strip()
        if a in alloy_to_indices: search_indices.update(alloy_to_indices[a])
        else:
            for key in alloy_to_indices:
                if a in key or key in a: search_indices.update(alloy_to_indices[key])
    if not search_indices: search_indices = set(range(len(docs)))
    search_indices = list(search_indices)

    kw_group = get_kws(prop_name)
    prop_kws = PROP_KW.get(kw_group, [])
    q_lower = question.lower()
    if kw_group == 'Rupture':
        tm = re.search(r'for\s+(\d+)\s*h', q_lower)
        if tm: prop_kws = prop_kws + ['σ' + tm.group(1)]
    active_kws = [kw for kw in prop_kws if kw.lower() in q_lower]
    doc_match_kws = active_kws if active_kws else prop_kws

    filtered = []
    for gi in search_indices:
        dt = docs[gi][1].lower()
        for kw in doc_match_kws:
            if kw.lower() in dt: filtered.append(gi); break
    if not filtered: filtered = search_indices
    if len(filtered) < top_k * 2: filtered = search_indices

    q_temps = extract_temps(question)
    target_temp = q_temps[0] if q_temps else None
    time_match = re.search(r'for\s+(\d+)\s*h', q_lower)
    target_time = int(time_match.group(1)) if time_match else None

    Nf = len(filtered)
    vec_s = np.zeros(Nf); bm25_s = np.zeros(Nf)
    temp_b = np.zeros(Nf); time_b = np.zeros(Nf); kw_b = np.zeros(Nf)
    for li, gi in enumerate(filtered):
        dt = docs[gi][1]; dt_lower = dt.lower()
        vec_s[li] = float(np.dot(doc_embs[gi], q_emb))
        bm25_s[li] = bm25_score(q_tokens, gi)
        for kw in doc_match_kws:
            if kw.lower() in dt_lower: kw_b[li] += 0.3
        if target_temp is not None:
            doc_temps = extract_temps(dt)
            if target_temp in doc_temps: temp_b[li] = 1.5
            elif doc_temps:
                closest = min(doc_temps, key=lambda t: abs(t-target_temp))
                diff = abs(closest-target_temp)
                if diff <= 20: temp_b[li] = 0.8
                elif diff <= 50: temp_b[li] = 0.4
        if target_time is not None:
            doc_times = extract_times(dt)
            if target_time in doc_times: time_b[li] = 1.5
            elif doc_times:
                closest = min(doc_times, key=lambda t: abs(t-target_time))
                if abs(closest-target_time) <= target_time*0.2: time_b[li] = 0.8
    for arr in [vec_s, bm25_s]:
        if arr.max()-arr.min() > 0.001: arr[:] = (arr-arr.min())/(arr.max()-arr.min())
        else: arr[:] = 0.5
    combined = 0.30*vec_s + 0.20*bm25_s + 0.25*temp_b + 0.15*time_b + 0.10*kw_b
    top_local = np.argsort(combined)[::-1][:top_k]
    return [filtered[i] for i in top_local]

# ── Unit pre-filter ──
def filter_docs_by_unit(docs_list, prop):
    prop_lower = prop.lower()
    if any(kw in prop_lower for kw in ['tensile', 'yield', 'stress rupture', 'compression']):
        valid_unit = lambda v: bool(re.search(r'MPa|GPa|ksi', str(v)))
    elif any(kw in prop_lower for kw in ['elongation', 'reduction of area']):
        valid_unit = lambda v: '%' in str(v) and not bool(re.search(r'MPa|GPa|h\b|kJ|W/', str(v)))
    elif 'creep rupture time' in prop_lower:
        valid_unit = lambda v: bool(re.search(r'\d+\s*h', str(v)))
    elif 'impact' in prop_lower:
        valid_unit = lambda v: bool(re.search(r'J/cm|kJ/m|J\b', str(v)))
    elif 'thermal conductivity' in prop_lower:
        valid_unit = lambda v: bool(re.search(r'W/', str(v)))
    elif 'hardness' in prop_lower:
        valid_unit = lambda v: bool(re.search(r'HB|HRC|HRB|HV|HBS', str(v)))
    else:
        return docs_list
    filtered = []
    for doc_text in docs_list:
        last_eq = doc_text.rfind('=')
        last_colon = max(doc_text.rfind(':'), doc_text.rfind('：'))
        sep = max(last_eq, last_colon)
        doc_value = doc_text[sep+1:].strip()[:60] if sep > 0 else doc_text[-60:]
        if valid_unit(doc_value):
            filtered.append(doc_text)
    return filtered if len(filtered) >= 3 else docs_list

# ── API ──
def call_api(messages, max_tokens=200):
    headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json'}
    payload = {'model': MODEL_NAME, 'messages': messages, 'max_tokens': max_tokens, 'temperature': 0.0}
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
        return '[API_ERROR:' + str(r.status_code) + ']'
    except Exception as e: return '[API_ERROR]'

# ── Prompts (from original) ──
SYSTEM_NUMERIC = (
    'You are a superalloy materials expert. Read ALL data entries carefully. '
    'Each entry has specimen conditions followed by a measured value. '
    'STEP 1: Identify which entries match the specimen conditions (alloy, temperature, '
    'heat treatment, specimen type, orientation, stress level, duration). '
    'STEP 2: From matching entries, find the one with the MOST specific condition match. '
    'STEP 3: Output ONLY the value (number+unit) from that entry. No explanation.'
)

SYSTEM_DESCRIPTIVE = (
    'You are a superalloy materials expert. Read ALL data entries carefully. '
    'Find the entry whose conditions BEST MATCH the question. '
    'Then, COPY the EXACT descriptive text from that entry as your answer. '
    'Preserve ALL formatting, symbols, punctuation, special characters, and spaces. '
    'Do NOT paraphrase, summarize, reorder, or convert to any other format. '
    'Output ONLY the copied text, exactly as it appears in the data entry.'
)

DESCRIPTIVE_PROPS = {
    'heat treatment schedule', 'product specification', 'forming process',
    'overview', 'material grade', 'melting process', 'welding performance',
    'machining performance', 'surface treatment', 'oxidation resistance',
    'phase transformation', 'casting performance',
}

# ── Run ──
rows = []
results = {'pure_model': 0, 'plain_rag': 0, 'agent': 0}
prop_stats = defaultdict(lambda: {'pm':0, 'pr':0, 'agent':0, 't':0})

for idx, qa in enumerate(test_qas):
    q = qa['question']; gt = qa['answer']; prop = qa['property']; alloy = qa.get('alloy','')

    # 1. Pure Model
    pm_ans = call_api([
        {'role':'system','content':'You are a superalloy materials expert. Answer concisely with just the value and unit. No explanation.'},
        {'role':'user','content': q}
    ], max_tokens=120)
    pm_ok = check_correct(pm_ans, gt)
    if pm_ok: results['pure_model'] += 1; prop_stats[prop]['pm'] += 1

    # 2. Plain Vector RAG (Top-3) — NO LLM, just check if doc contains answer
    plain_top = plain_vector_retrieve(q, alloy, top_k=3)
    plain_docs = [docs[i][1] for i in plain_top]
    pr_ok = any(check_correct(dt, gt) for dt in plain_docs)
    if pr_ok: results['plain_rag'] += 1; prop_stats[prop]['pr'] += 1

    # 3. Our Agent: Hybrid Top-8 + unit filter + LLM
    hybrid_top8 = hybrid_retrieve(q, prop, alloy, top_k=8)
    hybrid_docs = [docs[i][1] for i in hybrid_top8]
    hybrid_docs = filter_docs_by_unit(hybrid_docs, prop)
    hybrid_context = '\n\n'.join(['[Doc ' + str(j+1) + '] ' + dt for j, dt in enumerate(hybrid_docs)])

    is_descriptive = prop in DESCRIPTIVE_PROPS
    sys_prompt = SYSTEM_DESCRIPTIVE if is_descriptive else SYSTEM_NUMERIC
    user_end = 'BEST-MATCHING TEXT (copy exactly):' if is_descriptive else 'BEST-MATCHING VALUE:'

    agent_ans = call_api([
        {'role':'system','content': sys_prompt},
        {'role':'user','content': 'DATA:\n' + hybrid_context + '\n\nQUESTION: ' + q + '\n\n' + user_end}
    ], max_tokens=200)
    agent_ok = check_correct(agent_ans, gt)
    if agent_ok: results['agent'] += 1; prop_stats[prop]['agent'] += 1
    prop_stats[prop]['t'] += 1

    rows.append({
        'No.': idx + 1,
        'Alloy': alloy,
        'Property Type': prop,
        'Question': q,
        'Gold Answer': gt,
        'Pure Model Answer': pm_ans,
        'Pure Model Correct': 'Yes' if pm_ok else 'No',
        'Plain RAG Correct': 'Yes' if pr_ok else 'No',
        'Agent Answer': agent_ans,
        'Agent Correct': 'Yes' if agent_ok else 'No',
    })

    pm_sym = 'V' if pm_ok else 'X'
    pr_sym = 'V' if pr_ok else 'X'
    ag_sym = 'V' if agent_ok else 'X'
    print(f'[{idx+1:4d}] PM:{pm_sym} PR:{pr_sym} AG:{ag_sym} | {prop[:22]} | {str(gt)[:30]}')

    if (idx+1) % 50 == 0:
        n = idx+1
        print(f'  >> {n}: PM={100*results["pure_model"]/n:.1f}% PR={100*results["plain_rag"]/n:.1f}% AG={100*results["agent"]/n:.1f}%')

    if (idx+1) % 20 == 0:
        df_tmp = pd.DataFrame(rows)
        df_tmp.to_excel('TableS1_progress.xlsx', index=False)

    time.sleep(0.3)

# ── Finalize ──
df = pd.DataFrame(rows)
df.to_excel('TableS1_benchmark_details.xlsx', index=False)

pm_total = results['pure_model']
pr_total = results['plain_rag']
ag_total = results['agent']
print(f'\nDone! PM={pm_total}({100*pm_total/900:.1f}%) PR={pr_total}({100*pr_total/900:.1f}%) AG={ag_total}({100*ag_total/900:.1f}%)')

# Update bench_final_results_v2.json
stats_out = {}
for prop, s in prop_stats.items():
    stats_out[prop] = {'pm': s['pm'], 'pr': s['pr'], 'agent': s['agent'], 't': s['t']}

save_data = {'n': 900, 'results': results, 'prop_stats': stats_out}
with open('bench_final_results_v2.json', 'w', encoding='utf-8') as f:
    json.dump(save_data, f, ensure_ascii=False)
print('Updated bench_final_results_v2.json')
print('Saved to TableS1_benchmark_details.xlsx')
