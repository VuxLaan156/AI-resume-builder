from langchain_huggingface import HuggingFaceEmbeddings

embedder = HuggingFaceEmbeddings(
    model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
)
#vectors = embedder.embed_documents([chunk.text for chunk in chunks])
