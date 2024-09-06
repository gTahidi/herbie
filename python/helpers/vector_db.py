from langchain.storage import InMemoryByteStore, LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain_core.documents import Document
import uuid
import os
import json
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from . import files
from python.helpers import knowledge_import
from python.helpers.log import Log
import models
class VectorDB:
    def __init__(self, logger: Log, embeddings_model, in_memory=False, memory_dir="./memory", knowledge_dir="./knowledge"):
        self.logger = logger
        print("Initializing VectorDB with Pinecone...")
        self.logger.log("info", content="Initializing VectorDB with Pinecone...")
        
        self.embeddings_model = embeddings_model
        self.em_dir = files.get_abs_path(memory_dir, "embeddings")
        self.db_dir = files.get_abs_path(memory_dir, "database")
        self.kn_dir = files.get_abs_path(knowledge_dir) if knowledge_dir else ""
        
        if in_memory:
            self.store = InMemoryByteStore()
        else:
            self.store = LocalFileStore(self.em_dir)

        self.embedder = CacheBackedEmbeddings.from_bytes_store(
            embeddings_model, 
            self.store, 
            namespace=getattr(embeddings_model, 'model', getattr(embeddings_model, 'model_name', "default"))
        )

        # Initialize Pinecone
        self.db = models.get_pinecone_store(self.embedder)

        # Preload knowledge files
        if self.kn_dir:
            self.preload_knowledge(self.kn_dir, self.db_dir)

    def preload_knowledge(self, kn_dir: str, db_dir: str):
        index_path = files.get_abs_path(db_dir, "knowledge_import.json")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        index: dict[str, knowledge_import.KnowledgeImport] = {}
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
       
        index = knowledge_import.load_knowledge(self.logger, kn_dir, index)
        
        for file in index:
            if index[file]['state'] in ['changed', 'removed'] and index[file].get('ids', []):
                self.delete_documents_by_ids(index[file]['ids'])
            if index[file]['state'] == 'changed':
                index[file]['ids'] = self.insert_documents(index[file]['documents'])

        index = {k: v for k, v in index.items() if v['state'] != 'removed'}
        
        for file in index:
            if "documents" in index[file]: del index[file]['documents'] # type: ignore
            if "state" in index[file]: del index[file]['state'] # type: ignore
        with open(index_path, 'w') as f:
            json.dump(index, f)      
        
    def search_similarity(self, query, results=3):
        return self.db.similarity_search(query, k=results)
    
    def search_similarity_threshold(self, query, results=3, threshold=0.5):
        docs_and_scores = self.db.similarity_search_with_score(query, k=results)
        return [doc for doc, score in docs_and_scores if score <= threshold]

    def search_max_rel(self, query, results=3):
        # Pinecone doesn't have a direct equivalent to max_marginal_relevance_search
        # Fallback to regular similarity search
        return self.search_similarity(query, results)

    def delete_documents_by_query(self, query: str, threshold=0.1):
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

    def delete_documents_by_ids(self, ids: list[str]):
        self.db.delete(ids=ids)
        return len(ids)
        
    def insert_text(self, text):
        id = str(uuid.uuid4())
        self.db.add_documents(documents=[Document(page_content=text, metadata={"id": id})], ids=[id])
        return id
    
    def insert_documents(self, docs: list[Document]):
        ids = [str(uuid.uuid4()) for _ in range(len(docs))]
        for doc, id in zip(docs, ids):
            doc.metadata["id"] = id
        self.db.add_documents(documents=docs, ids=ids)
        return ids