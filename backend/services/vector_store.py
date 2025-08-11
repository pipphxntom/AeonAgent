from typing import Dict, List, Any, Optional
from langchain.schema import BaseRetriever, Document
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import logging
import uuid

from core.config import settings

logger = logging.getLogger(__name__)


class QdrantRetriever(BaseRetriever):
    """Qdrant-based document retriever."""
    
    def __init__(self, collection_name: str, top_k: int = 5):
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.collection_name = collection_name
        self.top_k = top_k
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    
    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents for a query."""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=self.top_k
            )
            
            # Convert to LangChain documents
            documents = []
            for hit in search_result:
                doc = Document(
                    page_content=hit.payload.get("text", ""),
                    metadata={
                        "score": hit.score,
                        "chunk_id": hit.id,
                        "source": hit.payload.get("source", ""),
                        "page": hit.payload.get("page", 0)
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Sync version - not implemented for async-only usage."""
        raise NotImplementedError("Use async version _aget_relevant_documents")


class VectorStoreService:
    """Service for managing vector embeddings and retrieval."""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    
    async def create_collection(self, collection_name: str, vector_size: int = 1536):
        """Create a new Qdrant collection."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise
    
    async def add_documents(
        self, 
        collection_name: str, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents to a collection."""
        try:
            # Generate embeddings
            embeddings = await self.embeddings.aembed_documents(texts)
            
            # Create points for Qdrant
            points = []
            point_ids = []
            
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        **metadata
                    }
                )
                points.append(point)
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} documents to {collection_name}")
            return point_ids
            
        except Exception as e:
            logger.error(f"Error adding documents to {collection_name}: {e}")
            raise
    
    async def search_documents(
        self, 
        collection_name: str, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Format results
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents in {collection_name}: {e}")
            return []
    
    async def delete_collection(self, collection_name: str):
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            raise
    
    def get_retriever(self, collection_name: str, top_k: int = 5) -> QdrantRetriever:
        """Get a retriever for a specific collection."""
        return QdrantRetriever(collection_name, top_k)
