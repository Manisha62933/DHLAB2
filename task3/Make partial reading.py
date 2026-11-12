"""
Synthetic Reading - Step 1: Partial Reading generator
Story: "The Child's Return" by Rabindranath Tagore (Stories from Tagore, 1918)

Method
------
1. Load the corpus (story text only).
2. Split into sentences ("lines").
3. Divide the sentences into N_PARTS equal parts.
4. From EACH part, randomly sample 20% of the sentences (fixed seed so the
   result is reproducible), keeping them in original story order.
"""
import random, re, math

CORPUS = "childs_return_corpus.txt"
OUT = "partial_reading.txt"
N_PARTS = 3
SAMPLE_RATIO = 0.20
SEED = 42

raw = open(CORPUS, encoding="utf-8").read()
story = raw.split("=====STORY STARTS BELOW=====")[1]

# drop bare section numerals (I, II, III), keep prose
paras = [p.strip() for p in story.split("\n") if p.strip() and p.strip() not in ("I", "II", "III")]
text = " ".join(paras)

# sentence split: after . ! ? (optionally followed by a closing quote) before a capital/quote
sentences = re.split(r'(?<=[.!?])(?:"|\u201d)?\s+(?=["\u201c]?[A-Z])', text)
# re-attach closing quotes lost in split
sentences = [s.strip() for s in sentences if s.strip()]

total = len(sentences)
size = math.ceil(total / N_PARTS)
parts = [sentences[i:i + size] for i in range(0, total, size)]

random.seed(SEED)
lines = []
lines.append("PARTIAL READING - The Child's Return (Rabindranath Tagore)")
lines.append(f"Method: {total} sentences divided into {len(parts)} equal parts; "
             f"random {int(SAMPLE_RATIO*100)}% of sentences sampled per part (seed={SEED}).")
lines.append("Sentences are shown in their original story order.")
lines.append("=" * 70)

for n, part in enumerate(parts, 1):
    k = max(1, round(len(part) * SAMPLE_RATIO))
    idx = sorted(random.sample(range(len(part)), k))
    lines.append(f"\nPART {n}  ({len(part)} sentences, {k} sampled)")
    lines.append("-" * 70)
    for i in idx:
        lines.append(f"[{n}.{i+1}] {part[i]}")

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"Total sentences: {total}; parts: {[len(p) for p in parts]}")