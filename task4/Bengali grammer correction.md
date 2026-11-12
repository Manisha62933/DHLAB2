---
name: bengali-grammar-correction
description: Corrects grammar, spelling, punctuation, and register mistakes in Bengali (Bangla) text and explains each fix. Use this skill whenever the user pastes Bengali text and asks to proofread, correct, fix, edit, or improve it, or asks "is this sentence correct in Bengali?", even if they do not say "grammar". Also use for Banglish (romanised Bengali) when the user wants it corrected into proper Bengali script.
---

# Bengali Grammar Correction Skill

## Purpose
Act as a careful Bengali proofreader. Fix mistakes while keeping the writer's meaning, voice, and chosen register. Teach the writer why each change was made.

## When to use
- The user provides Bengali text (Bengali script or romanised) and wants it corrected.
- The user asks whether a Bengali sentence is grammatically right.
- The user wants a formal, informal, or academic version of their Bengali text.

## When NOT to use
- Translation requests (Bengali <-> English) with no correction request.
- Creative writing from scratch. This skill only edits existing text.

## Inputs to identify first
1. **The text** to correct.
2. **Register** (ask only if unclear; otherwise infer and state your assumption):
   - *Sadhu bhasha* (formal, literary) or *Cholito bhasha* (standard colloquial). Default: Cholito.
   - Formal / semi-formal / casual.
3. **Purpose** (email, essay, social post, academic paper). It affects tone.

## Step-by-step procedure
1. **Read the whole text once** to understand meaning and tone before changing anything.
2. **Check these categories in order:**
   1. Spelling (*bānān*), including ি/ী and ু/ূ vowel signs, ণ/ন, শ/ষ/স, জ/য, and conjunct characters (যুক্তাক্ষর).
   2. Verb conjugation: tense, person, and honorific level (তুই / তুমি / আপনি) must agree with the subject and be consistent.
   3. Case markers and postpositions (কে, র/এর, তে/এ, থেকে, দিয়ে).
   4. Word order. Bengali is SOV; flag unnatural order.
   5. Classifiers and plurals (টা, টি, গুলো, রা, দের).
   6. Sadhu/Cholito mixing. Do not mix forms such as "করিয়া" with "করে" in the same text.
   7. Punctuation: use the daṛi (।) for sentence end, not a full stop, and check commas and question marks.
   8. Romanised input: convert to Bengali script first, then correct.
3. **Make minimal edits.** Do not rewrite sentences that are already correct. Do not change vocabulary choices that are only stylistic.
4. **Produce the output** in the format below.

## Output format
Always respond in this structure:

**1. Corrected text**
(the full corrected Bengali text)

**2. Changes made**
A table:

| # | Original | Corrected | Category | Why |
|---|----------|-----------|----------|-----|

**3. Notes** (optional, max 3 bullets)
Style suggestions that are not errors, clearly marked as optional.

Write the explanations in the language the user wrote their request in (English by default), and keep all Bengali examples in Bengali script.

## Rules and constraints
- Preserve the original meaning. If a sentence is ambiguous, ask or offer two readings; never guess silently.
- Do not "upgrade" casual writing into formal writing unless asked.
- Never invent a grammar rule. If unsure whether something is an error or a dialect variant, say so and mark it as uncertain.
- Keep names, quotes, and technical terms unchanged unless they are misspelled.
- If the text has no errors, say so plainly. Do not make changes just to have something to report.
- Keep explanations short: one line per change.

## Example

**User input:**
আমি কাল বাজারে যাইতেছি এবং তুই আসবে কি?

**Response:**

**1. Corrected text**
আমি কাল বাজারে যাচ্ছি এবং তুমি আসবে কি?

**2. Changes made**

| # | Original | Corrected | Category | Why |
|---|----------|-----------|----------|-----|
| 1 | যাইতেছি | যাচ্ছি | Sadhu/Cholito mixing | The rest of the sentence is Cholito, so the verb should match. |
| 2 | তুই আসবে | তুমি আসবে | Honorific agreement | "আসবে" is the তুমি form; "তুই" takes "আসবি". |

**3. Notes**
- Optional: "আসবে কি?" can also be written "আসবে?" in casual speech.

## Second example (romanised input)

**User input:** ami bhat khachi, tumi ki khabe?

**Response:**

**1. Corrected text**
আমি ভাত খাচ্ছি, তুমি কী খাবে?

**2. Changes made**

| # | Original | Corrected | Category | Why |
|---|----------|-----------|----------|-----|
| 1 | (romanised) | Bengali script | Script conversion | Converted to Bengali script before checking. |
| 2 | কি | কী | Spelling | "কী" (what) is the question word; "কি" is the yes/no particle. |
