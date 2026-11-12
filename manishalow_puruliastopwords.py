"""
============================================================
Topic: Indic Language Stop Words for Natural Language Processing
============================================================
Author Name(s): Manisha Low
Short Description: This file contains a stop-word list for the
Bengali language. These words may be used during text
preprocessing in Natural Language Processing (NLP), for example
before tokenisation-based tasks such as keyword extraction, topic
modelling, or text classification.
Semester: Monsoon Semester 2026
Affiliation: Student
Note:
This list contains commonly used function words (conjunctions,
pronouns, postpositions, auxiliaries, particles). It is meant as
a practical starting point and should be adapted to the corpus
and task at hand.
============================================================
"""
 
# 1. Bengali Stop Words
# Language: Bengali
# Script: Bengali
 
bengali_stopwords = [
    # Conjunctions and connectors
    "এবং",
    "কিন্তু",
    "অথবা",
    "বা",
    "যদি",
    "তবে",
    "তাই",
    "কারণ",
    "যেহেতু",
    "অতএব",
    "আর",
    "ও",
    "তবু",
    "নতুবা",
    "অর্থাৎ",
 
    # Demonstrative and relative pronouns
    "এই",
    "এটা",
    "এটি",
    "ওই",
    "ওটা",
    "সেই",
    "সে",
    "তা",
    "তার",
    "তাকে",
    "তাদের",
    "তারা",
    "যে",
    "যা",
    "যার",
    "যারা",
    "যাকে",
    "এরা",
    "ওরা",
    "এর",
    "ওর",
 
    # Personal pronouns
    "আমি",
    "আমার",
    "আমাকে",
    "আমরা",
    "আমাদের",
    "তুমি",
    "তোমার",
    "তোমাকে",
    "তোমরা",
    "তোমাদের",
    "তুই",
    "আপনি",
    "আপনার",
    "আপনাকে",
    "আপনারা",
    "আপনাদের",
 
    # Interrogatives
    "কি",
    "কী",
    "কে",
    "কাকে",
    "কার",
    "কেন",
    "কোন",
    "কোথায়",
    "কখন",
    "কবে",
    "কিভাবে",
    "কত",
    "কিছু",
    "কেউ",
    "কোনো",
 
    # Postpositions and case markers
    "থেকে",
    "দিয়ে",
    "জন্য",
    "মধ্যে",
    "সাথে",
    "সঙ্গে",
    "পর্যন্ত",
    "প্রতি",
    "উপর",
    "নিচে",
    "পরে",
    "আগে",
    "ভিতরে",
    "বাইরে",
    "দ্বারা",
    "মতো",
    "মত",
    "কাছে",
    "পাশে",
    "বিরুদ্ধে",
    "সম্পর্কে",
    "ছাড়া",
    "হতে",
    "করে",
 
    # Auxiliary and common verb forms
    "আছে",
    "আছি",
    "আছো",
    "আছেন",
    "ছিল",
    "ছিলাম",
    "ছিলেন",
    "হয়",
    "হয়েছে",
    "হয়েছিল",
    "হবে",
    "হচ্ছে",
    "হল",
    "হলো",
    "হন",
    "হই",
    "থাকা",
    "থাকে",
    "থাকবে",
    "করা",
    "করে",
    "করেছে",
    "করেছিল",
    "করবে",
    "করছে",
    "করেন",
    "করি",
    "দেওয়া",
    "নেওয়া",
    "যায়",
    "যাওয়া",
    "পারে",
    "পারা",
 
    # Negation
    "না",
    "নয়",
    "নেই",
    "নি",
    "নাই",
 
    # Particles, emphasis and quantifiers
    "ই",
    "টা",
    "টি",
    "খানা",
    "খানি",
    "গুলো",
    "গুলি",
    "সব",
    "সকল",
    "সবাই",
    "অনেক",
    "আরও",
    "আরো",
    "খুব",
    "শুধু",
    "মাত্র",
    "প্রায়",
    "এখন",
    "তখন",
    "এখানে",
    "সেখানে",
    "যখন",
    "যেখানে",
    "তো",
    "যেন",
    "নিজে",
    "নিজের",
    "একটি",
    "একটা",
    "এক",
    "দুই",
    "হ্যাঁ",
    "অন্য",
    "আবার",
    "ভাল",
    "এমন",
    "তেমন",
    "এত",
    "তত",
    "এমনকি",
]
 
# Remove accidental duplicates while preserving order
bengali_stopwords = list(dict.fromkeys(bengali_stopwords))
 
 
if __name__ == "__main__":
    # Quick sanity check: run `python bengali_stopwords.py`
    print(f"Total Bengali stop words: {len(bengali_stopwords)}")
 
    sample = "আমি এবং তুমি বাজারে যাব কিন্তু সে বাড়িতে থাকবে"
    filtered = [w for w in sample.split() if w not in bengali_stopwords]
    print("Original:", sample)
    print("Filtered:", " ".join(filtered))
