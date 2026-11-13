import os
import numpy
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
    timeout=30.0,
    max_retries=0
)


EMBED_MODEL = os.getenv("EMBED_MODEL")
KB_FOLDER = os.getenv("KB_FOLDER")

# Get the embedding of a text from Embedding model

def get_embedding(text):
    print(f"Generating embedding for {len(text)} characters...", flush=True)

    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )

        print("Embedding generated successfully!", flush=True)
        return response.data[0].embedding

    except Exception as e:
        print(f"Embedding error: {e}", flush=True)
        raise

# Get the cosine similarity between two vectors
def cosine_similarity(A, B):
    dot_prod = numpy.dot(A, B)
    norm_a = numpy.linalg.norm(A)
    norm_b = numpy.linalg.norm(B)
    return dot_prod / (norm_a * norm_b)

# Load the  documents
def load_documents(folder=KB_FOLDER):
    documents = []
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            documents.append(
                {
                    "source": filename,
                    "text": f.read()
                }
            )

    return documents

# Add embeddings in the documents
def add_embeddings(documents):
    for i, document in enumerate(documents):
        print(
            f"\nProcessing document {i+1}/{len(documents)}: "
            f"{document['source']}",
            flush=True
        )

        vector = get_embedding(document["text"])
        document["vector"] = vector

    return documents

# Search method to search the top_k documents for a user_query
def search(query, documents, top_k=3):
    query_vector = get_embedding(query)

    results = []
    for document in documents:
        score = cosine_similarity(query_vector, document["vector"])
        results.append(
            {
                "score" : float(score),
                "source" : document["source"],
                "text" : document["text"],
                "size" : len(document["text"])
            }
        ) 

    results.sort(key=lambda rec:rec["score"], reverse=True)
    return results[:top_k]

# Testing method

def test(user_query, documents, top_k=3):
    print("\nUser Query: {user_query}\n")

    results = search(user_query, documents, top_k)

    for r in results:
        print(f" {r['score']:.2f} - {r['source']} - {r['size']} characters")

#Let's start testing
# Let's start testing
print("1. Loading documents...", flush=True)
documents = load_documents()

print(f"2. Loaded {len(documents)} documents", flush=True)

print("3. Generating embeddings...", flush=True)
documents = add_embeddings(documents)


print(f"We have embedded {len(documents)} documents")

user_query = "How many days I will get for maternity leave ?"
test(user_query, documents, 3)