from langchain.storage import InMemoryByteStore, LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
from . import files
from langchain_core.documents import Document
import uuid
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

class VectorDB:
    def __init__(self, embeddings_model, in_memory=False, cache_dir="./cache"):
        print("Initializing VectorDB with Pinecone...")
        self.embeddings_model = embeddings_model

        em_cache = files.get_abs_path(cache_dir, "embeddings")
        
        if in_memory:
            self.store = InMemoryByteStore()
        else:
            self.store = LocalFileStore(em_cache)

        # Setup the embeddings model with the chosen cache storage
        self.embedder = CacheBackedEmbeddings.from_bytes_store(
            embeddings_model, 
            self.store, 
            namespace=getattr(embeddings_model, 'model', getattr(embeddings_model, 'model_name', "default"))
        )

        # Initialize Pinecone
        self.pc = Pinecone(api_key=embeddings_model.pinecone_api_key)
        index_name = embeddings_model.pinecone_index_name

        if index_name not in self.pc.list_indexes():
            self.pc.create_index(
                name=index_name,
                dimension=embeddings_model.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="azure",  # or "gcp" depending on your preference
                    region="eastus2"  # choose an appropriate region
                )
            )

        self.index = self.pc.Index(index_name)
        self.db = PineconeVectorStore(index=self.index, embedding=self.embedder)

    def search_similarity(self, query, results=3):
        return self.db.similarity_search(query, k=results)
    
    def search_similarity_threshold(self, query, results=3, threshold=0.5):
        docs_and_scores = self.db.similarity_search_with_score(query, k=results)
        return [doc for doc, score in docs_and_scores if score <= threshold]

    def search_max_rel(self, query, results=3):
        # Pinecone doesn't have a direct equivalent to max_marginal_relevance_search
        # Fallback to regular similarity search
        return self.search_similarity(query, results)

    def delete_documents_by_query(self, query:str, threshold=0.1):
        k = 100
        tot = 0
        while True:
            docs_and_scores = self.db.similarity_search_with_score(query, k=k)
            document_ids = [doc.metadata["id"] for doc, score in docs_and_scores if score <= threshold]
            
            if document_ids:
                self.db.delete(ids=document_ids)
                tot += len(document_ids)
            
            if len(document_ids) < k:
                break
        
        return tot

    def delete_documents_by_ids(self, ids:list[str]):
        self.db.delete(ids=ids)
        return len(ids)
        
    def insert_document(self, data):
        id = str(uuid.uuid4())
        self.db.add_documents(documents=[Document(page_content=data, metadata={"id": id})], ids=[id])
        return id