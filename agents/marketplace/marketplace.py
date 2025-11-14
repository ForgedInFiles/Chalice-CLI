"""
Chalice Agent Marketplace
Community hub for discovering, sharing, and installing agents
"""
import json
import os
import shutil
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class AgentMetadata:
    """Agent metadata structure"""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.name = data.get('name', '')
        self.version = data.get('version', '1.0.0')
        self.description = data.get('description', '')
        self.author = data.get('author', '')
        self.tags = data.get('tags', [])
        self.category = data.get('category', 'general')
        self.capabilities = data.get('capabilities', [])
        self.dependencies = data.get('dependencies', [])
        self.rating = data.get('rating', 0.0)
        self.downloads = data.get('downloads', 0)
        self.created_at = data.get('created_at', '')
        self.updated_at = data.get('updated_at', '')
        self.file_url = data.get('file_url', '')
        self.file_hash = data.get('file_hash', '')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'tags': self.tags,
            'category': self.category,
            'capabilities': self.capabilities,
            'dependencies': self.dependencies,
            'rating': self.rating,
            'downloads': self.downloads,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'file_url': self.file_url,
            'file_hash': self.file_hash
        }


class AgentReview:
    """Agent review structure"""

    def __init__(self, data: Dict[str, Any]):
        self.agent_id = data.get('agent_id', '')
        self.user = data.get('user', '')
        self.rating = data.get('rating', 0)
        self.comment = data.get('comment', '')
        self.created_at = data.get('created_at', '')
        self.helpful_count = data.get('helpful_count', 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'user': self.user,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at,
            'helpful_count': self.helpful_count
        }


class AgentMarketplace:
    """
    Agent Marketplace for discovering, installing, and managing community agents

    Features:
    - Agent discovery and search
    - One-click installation
    - Ratings and reviews
    - Version management
    - Dependency resolution
    """

    def __init__(self, marketplace_dir: Optional[Path] = None):
        """Initialize the marketplace"""
        if marketplace_dir is None:
            marketplace_dir = Path(__file__).parent

        self.marketplace_dir = Path(marketplace_dir)
        self.registry_file = self.marketplace_dir / "registry.json"
        self.reviews_file = self.marketplace_dir / "reviews.json"
        self.installed_agents_dir = Path(__file__).parent.parent / "custom"

        # Create directories
        self.marketplace_dir.mkdir(parents=True, exist_ok=True)
        self.installed_agents_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        self.registry = self._load_registry()
        self.reviews = self._load_reviews()

    def _load_registry(self) -> List[AgentMetadata]:
        """Load agent registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                return [AgentMetadata(agent) for agent in data]
        return []

    def _save_registry(self):
        """Save agent registry"""
        with open(self.registry_file, 'w') as f:
            json.dump([agent.to_dict() for agent in self.registry], f, indent=2)

    def _load_reviews(self) -> List[AgentReview]:
        """Load reviews"""
        if self.reviews_file.exists():
            with open(self.reviews_file, 'r') as f:
                data = json.load(f)
                return [AgentReview(review) for review in data]
        return []

    def _save_reviews(self):
        """Save reviews"""
        with open(self.reviews_file, 'w') as f:
            json.dump([review.to_dict() for review in self.reviews], f, indent=2)

    def search_agents(
        self,
        query: str = "",
        category: str = None,
        tags: List[str] = None,
        min_rating: float = 0.0,
        sort_by: str = "downloads"
    ) -> List[AgentMetadata]:
        """
        Search for agents in the marketplace

        Args:
            query: Search query string
            category: Filter by category
            tags: Filter by tags
            min_rating: Minimum rating filter
            sort_by: Sort by (downloads, rating, name, updated_at)

        Returns:
            List of matching agents
        """
        results = self.registry.copy()

        # Apply filters
        if query:
            query_lower = query.lower()
            results = [
                agent for agent in results
                if query_lower in agent.name.lower() or
                   query_lower in agent.description.lower() or
                   any(query_lower in tag.lower() for tag in agent.tags)
            ]

        if category:
            results = [agent for agent in results if agent.category == category]

        if tags:
            results = [
                agent for agent in results
                if any(tag in agent.tags for tag in tags)
            ]

        if min_rating > 0:
            results = [agent for agent in results if agent.rating >= min_rating]

        # Sort results
        sort_keys = {
            'downloads': lambda a: a.downloads,
            'rating': lambda a: a.rating,
            'name': lambda a: a.name,
            'updated_at': lambda a: a.updated_at
        }
        if sort_by in sort_keys:
            results.sort(key=sort_keys[sort_by], reverse=True)

        return results

    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent by ID"""
        for agent in self.registry:
            if agent.id == agent_id:
                return agent
        return None

    def install_agent(self, agent_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Install an agent from the marketplace

        Args:
            agent_id: Agent ID to install
            force: Force reinstall if already installed

        Returns:
            Installation result
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent not found: {agent_id}"
            }

        # Check if already installed
        agent_file = self.installed_agents_dir / f"{agent.name.lower().replace(' ', '_')}.md"
        if agent_file.exists() and not force:
            return {
                "success": False,
                "error": f"Agent already installed: {agent.name}",
                "installed_path": str(agent_file)
            }

        try:
            # Download agent file
            if agent.file_url.startswith('http'):
                # Download from URL
                response = requests.get(agent.file_url, timeout=30)
                response.raise_for_status()
                content = response.text
            else:
                # Load from local file (for testing/development)
                with open(agent.file_url, 'r') as f:
                    content = f.read()

            # Verify hash if provided
            if agent.file_hash:
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                if content_hash != agent.file_hash:
                    return {
                        "success": False,
                        "error": "File hash mismatch - potential security risk"
                    }

            # Install agent
            with open(agent_file, 'w') as f:
                f.write(content)

            # Update downloads count
            agent.downloads += 1
            self._save_registry()

            return {
                "success": True,
                "agent": agent.to_dict(),
                "installed_path": str(agent_file),
                "message": f"Agent '{agent.name}' installed successfully!"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def uninstall_agent(self, agent_id: str) -> Dict[str, Any]:
        """Uninstall an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent not found: {agent_id}"
            }

        agent_file = self.installed_agents_dir / f"{agent.name.lower().replace(' ', '_')}.md"
        if not agent_file.exists():
            return {
                "success": False,
                "error": f"Agent not installed: {agent.name}"
            }

        try:
            agent_file.unlink()
            return {
                "success": True,
                "message": f"Agent '{agent.name}' uninstalled successfully!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def add_review(
        self,
        agent_id: str,
        user: str,
        rating: int,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add a review for an agent

        Args:
            agent_id: Agent ID
            user: Username
            rating: Rating (1-5)
            comment: Review comment

        Returns:
            Result dictionary
        """
        if not 1 <= rating <= 5:
            return {
                "success": False,
                "error": "Rating must be between 1 and 5"
            }

        agent = self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent not found: {agent_id}"
            }

        review = AgentReview({
            'agent_id': agent_id,
            'user': user,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat(),
            'helpful_count': 0
        })

        self.reviews.append(review)
        self._save_reviews()

        # Update agent rating
        agent_reviews = [r for r in self.reviews if r.agent_id == agent_id]
        avg_rating = sum(r.rating for r in agent_reviews) / len(agent_reviews)
        agent.rating = round(avg_rating, 2)
        self._save_registry()

        return {
            "success": True,
            "review": review.to_dict(),
            "new_rating": agent.rating
        }

    def get_reviews(self, agent_id: str) -> List[AgentReview]:
        """Get reviews for an agent"""
        return [r for r in self.reviews if r.agent_id == agent_id]

    def list_categories(self) -> List[str]:
        """List all agent categories"""
        categories = set(agent.category for agent in self.registry)
        return sorted(list(categories))

    def list_installed(self) -> List[str]:
        """List installed agents"""
        installed = []
        for agent_file in self.installed_agents_dir.glob("*.md"):
            installed.append(agent_file.stem)
        return installed

    def publish_agent(
        self,
        agent_file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish an agent to the marketplace

        Args:
            agent_file_path: Path to agent markdown file
            metadata: Agent metadata

        Returns:
            Publication result
        """
        try:
            # Generate agent ID
            agent_id = f"{metadata['author']}_{metadata['name']}".lower().replace(' ', '_')

            # Calculate file hash
            with open(agent_file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Create metadata
            agent_data = {
                'id': agent_id,
                'name': metadata['name'],
                'version': metadata.get('version', '1.0.0'),
                'description': metadata['description'],
                'author': metadata['author'],
                'tags': metadata.get('tags', []),
                'category': metadata.get('category', 'general'),
                'capabilities': metadata.get('capabilities', []),
                'dependencies': metadata.get('dependencies', []),
                'rating': 0.0,
                'downloads': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'file_url': agent_file_path,  # In production, this would be a remote URL
                'file_hash': file_hash
            }

            agent_metadata = AgentMetadata(agent_data)

            # Check if agent already exists
            existing = self.get_agent(agent_id)
            if existing:
                # Update existing agent
                for i, agent in enumerate(self.registry):
                    if agent.id == agent_id:
                        self.registry[i] = agent_metadata
                        break
            else:
                # Add new agent
                self.registry.append(agent_metadata)

            self._save_registry()

            return {
                "success": True,
                "agent": agent_metadata.to_dict(),
                "message": f"Agent '{metadata['name']}' published successfully!"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global marketplace instance
_marketplace = None


def get_marketplace() -> AgentMarketplace:
    """Get the global marketplace instance"""
    global _marketplace
    if _marketplace is None:
        _marketplace = AgentMarketplace()
    return _marketplace
