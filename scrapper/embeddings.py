import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import re

def parse_markdown_to_chunks(filepath: str) -> list:
    """Reads a markdown file and splits it into semantic chunks."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split the document by horizontal rules (---) or double newlines
    # This naturally separates different jobs, projects, and sections
    raw_blocks = re.split(r'\n---\n|\n\n', content)
    
    chunks = []
    for i, block in enumerate(raw_blocks):
        clean_block = block.strip()
        # Only keep blocks that have meaningful content (ignore empty lines or single characters)
        if len(clean_block) > 20:
            chunks.append({
                "id": f"md_chunk_{i}",
                "content": clean_block
            })
            
    return chunks

def generate_embeddings():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    # This downloads the model on the first run, caches locally afterward
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    data_path = "../data/resume.md"
    data_embeddings_cache = "../data/embeddings_cache.npy"
    data_chunk_cache = "../data/chunks_cache.json"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Could not find {data_path}. Please create it.")
    
    print(f"Parsing {data_path} into chunks...")
    chunks = parse_markdown_to_chunks(data_path)
    
    print(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts)
    
    # Save the numpy array and the chunk metadata cache
    np.save(data_embeddings_cache, embeddings)
    with open(data_chunk_cache, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print("✅ Embeddings saved to data/embeddings_cache.npy and data/chunks_cache.json")