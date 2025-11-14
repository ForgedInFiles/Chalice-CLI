"""
Vector Store for Memory System
Efficient vector storage and similarity search for long-term memory
"""
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib


class VectorStore:
    """
    Vector store for embedding-based memory

    Provides efficient storage and retrieval of vector embeddings
    with metadata for context persistence
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize vector store

        Args:
            storage_path: Path to store vectors (default: memory/vectors/)
        """
        if storage_path is None:
            storage_path = Path(__file__).parent / "vectors"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.index_file = self.storage_path / "index.json"

        self._load_index()

    def _load_index(self):
        """Load index from disk"""
        if not self.index_file.exists():
            return

        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)

            for entry in index_data:
                vector_file = self.storage_path / entry['vector_file']
                if vector_file.exists():
                    vector = np.load(vector_file)
                    self.vectors.append(vector)
                    self.metadata.append(entry['metadata'])

        except Exception as e:
            print(f"Error loading index: {e}")

    def _save_index(self):
        """Save index to disk"""
        try:
            index_data = []
            for i, meta in enumerate(self.metadata):
                vector_file = f"vector_{i}_{meta['id']}.npy"
                np.save(self.storage_path / vector_file, self.vectors[i])

                index_data.append({
                    'vector_file': vector_file,
                    'metadata': meta
                })

            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)

        except Exception as e:
            print(f"Error saving index: {e}")

    def add(
        self,
        vector: np.ndarray,
        content: str,
        source: str = "unknown",
        tags: List[str] = None,
        **kwargs
    ) -> str:
        """
        Add a vector to the store

        Args:
            vector: Embedding vector
            content: Original content
            source: Source of the content
            tags: Tags for categorization
            **kwargs: Additional metadata

        Returns:
            str: Vector ID
        """
        # Generate ID
        vector_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Create metadata
        metadata = {
            'id': vector_id,
            'content': content,
            'source': source,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }

        # Add to store
        self.vectors.append(vector)
        self.metadata.append(metadata)

        # Save
        self._save_index()

        return vector_id

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            filters: Metadata filters

        Returns:
            List of matching results with metadata and scores
        """
        if not self.vectors:
            return []

        # Calculate cosine similarities
        similarities = []
        for i, vec in enumerate(self.vectors):
            # Apply filters
            if filters:
                meta = self.metadata[i]
                if not self._matches_filters(meta, filters):
                    continue

            sim = self._cosine_similarity(query_vector, vec)
            if sim >= min_similarity:
                similarities.append((i, sim))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top k
        results = []
        for idx, sim in similarities[:top_k]:
            results.append({
                **self.metadata[idx],
                'similarity': float(sim)
            })

        return results

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata:
                return False

            if isinstance(value, list):
                # Check if any value matches
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False

        return True

    def delete(self, vector_id: str) -> bool:
        """
        Delete a vector

        Args:
            vector_id: Vector ID to delete

        Returns:
            bool: True if deleted
        """
        for i, meta in enumerate(self.metadata):
            if meta['id'] == vector_id:
                del self.vectors[i]
                del self.metadata[i]
                self._save_index()
                return True

        return False

    def get_by_id(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata by vector ID"""
        for meta in self.metadata:
            if meta['id'] == vector_id:
                return meta

        return None

    def count(self) -> int:
        """Get number of stored vectors"""
        return len(self.vectors)

    def clear(self):
        """Clear all vectors"""
        self.vectors = []
        self.metadata = []
        self._save_index()


class MemoryManager:
    """
    Memory Manager with context persistence

    Manages long-term memory using vector stores
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize memory manager"""
        if storage_path is None:
            storage_path = Path(__file__).parent

        self.storage_path = Path(storage_path)
        self.vector_store = VectorStore(storage_path / "vectors")
        self.conversation_file = storage_path / "conversations.json"
        self.knowledge_file = storage_path / "knowledge.json"

        self.conversations: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}

        self._load_data()

    def _load_data(self):
        """Load conversation and knowledge data"""
        if self.conversation_file.exists():
            with open(self.conversation_file, 'r') as f:
                self.conversations = json.load(f)

        if self.knowledge_file.exists():
            with open(self.knowledge_file, 'r') as f:
                self.knowledge_base = json.load(f)

    def _save_data(self):
        """Save conversation and knowledge data"""
        with open(self.conversation_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)

        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def add_conversation(
        self,
        messages: List[Dict[str, str]],
        session_id: str,
        tags: List[str] = None
    ):
        """Add conversation to memory"""
        conversation = {
            'id': hashlib.md5(f"{session_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'session_id': session_id,
            'messages': messages,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat()
        }

        self.conversations.append(conversation)
        self._save_data()

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        return sorted(
            self.conversations,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]

    def search_conversations(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search conversations by keyword"""
        results = []

        for conv in self.conversations:
            # Simple keyword search
            text = ' '.join([msg['content'] for msg in conv['messages']])
            if query.lower() in text.lower():
                results.append(conv)

        return sorted(results, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def add_knowledge(
        self,
        key: str,
        value: Any,
        category: str = "general",
        tags: List[str] = None
    ):
        """Add knowledge to base"""
        self.knowledge_base[key] = {
            'value': value,
            'category': category,
            'tags': tags or [],
            'updated': datetime.now().isoformat()
        }

        self._save_data()

    def get_knowledge(self, key: str) -> Optional[Any]:
        """Get knowledge by key"""
        entry = self.knowledge_base.get(key)
        return entry['value'] if entry else None

    def search_knowledge(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search knowledge base"""
        results = {}

        for key, entry in self.knowledge_base.items():
            if category and entry['category'] != category:
                continue

            if tags:
                if not any(tag in entry['tags'] for tag in tags):
                    continue

            results[key] = entry

        return results


# Global memory manager instance
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
