# Retrieval evaluation on five job descriptions

## Method

The benchmark used five JD PDFs, 26 text chunks, and 10 queries in English
and Vietnamese. Each JD had one skills query and one requirements query.
The queries were scored against 21 manually labeled evidence items. Each
label identified a JD, a page, and a source quote. A result counted as
evidence when a returned chunk contained that quote on the expected page.
Overlapping chunks could satisfy the same label only once.

Every query searched all five JDs. BM25+ ranked text by keyword matches.
Semantic search ranked embeddings by cosine similarity in in-memory
Qdrant. The hybrid method fused up to 20 candidates per branch and
reranked up to 20 fused candidates with the multilingual cross-encoder.
All scores below come from the run with the configured models.

**Hit@5** counts queries with at least one labeled item in the top five.
**MRR@5** averages the reciprocal rank of the first relevant chunk, with
misses scored as zero. **Evidence recall@5** counts how many labeled
items appeared anywhere in the top five.

## Results

| Retriever | Skills evidence | Requirements evidence | Overall evidence | Hit@5 | MRR@5 |
|---|---:|---:|---:|---:|---:|
| BM25+ | **9/10 (90%)** | 9/11 (82%) | 18/21 (86%) | **10/10** | 0.545 |
| Semantic | 2/10 (20%) | 5/11 (45%) | 7/21 (33%) | 5/10 | 0.270 |
| Hybrid + rerank | 8/10 (80%) | **11/11 (100%)** | **19/21 (90%)** | 9/10 | **0.625** |

BM25+ found at least one relevant chunk for every query and recovered the
most skill evidence. For JD 1, it found the programming libraries but
missed SQL/NoSQL. Hybrid recovered both facts. For JD 5, BM25+ missed the
postgraduate degree and equivalent research experience, while hybrid
found all three labeled requirements. Hybrid missed both labeled skill
items for that same JD, which were nonlinear optimization and Python
with PyTorch.

## Conclusion

Use **BM25+ for skill lookup** and **hybrid retrieval with reranking for
requirements lookup** as initial defaults. On this set, BM25+ covered more
skill evidence, while hybrid covered every labeled requirement and ranked
the first relevant result higher on average across all tasks. Semantic
search added useful evidence for JD 5 despite its lower overall coverage
when run on its own.

Treat these defaults as provisional. Five JDs and one query per task per
JD make this a small benchmark. The labels cover selected facts, so the
scores measure retrieval of those facts rather than exhaustive extraction
or the accuracy of generated answers. Inspect the JD 5 skill query at
each stage of the hybrid pipeline to locate where its evidence dropped
out, then repeat the comparison on more JDs before changing the production
default.

Run the benchmark from the repository root.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m backend.tests.evaluate_retriever
```
