"""Mock database service for development/testing without Supabase."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import json

class MockDatabaseService:
    """In-memory mock database for development."""
    
    def __init__(self):
        self.users = {
            "admin@test.com": {
                "id": "admin-001",
                "email": "admin@test.com",
                "password_hash": "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcg7b3XeKeUxWdeS86E36DRcT86",  # hashed "password"
                "full_name": "Admin User",
                "subscription_tier": "pro",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        self.projects = {}
        self.datasets = {}
        self.analyses = {}
        self.team_members = {}
        self.api_keys = {}
    
    # User operations
    def create_user(self, email: str, password_hash: str, full_name: str):
        if email in self.users:
            return None
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "subscription_tier": "free",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.users[email] = user
        return user
    
    def get_user_by_email(self, email: str):
        return self.users.get(email)
    
    def get_user_by_id(self, user_id: str):
        for user in self.users.values():
            if user["id"] == user_id:
                return user
        return None
    
    def update_user(self, user_id: str, data: Dict[str, Any]):
        for user in self.users.values():
            if user["id"] == user_id:
                user.update(data)
                user["updated_at"] = datetime.utcnow().isoformat()
                return user
        return None
    
    def update_user_password(self, user_id: str, password_hash: str):
        return self.update_user(user_id, {"password_hash": password_hash})
    
    # Project operations
    def create_project(self, user_id: str, name: str, description: Optional[str] = None):
        project_id = str(uuid4())
        project = {
            "id": project_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.projects[project_id] = project
        return project
    
    def get_project(self, project_id: str, user_id: str):
        p = self.projects.get(project_id)
        if p and p["user_id"] == user_id:
            return p
        return None
    
    def get_user_projects(self, user_id: str):
        return [p for p in self.projects.values() if p["user_id"] == user_id]
    
    def update_project(self, project_id: str, user_id: str, data: Dict[str, Any]):
        p = self.projects.get(project_id)
        if p and p["user_id"] == user_id:
            p.update(data)
            p["updated_at"] = datetime.utcnow().isoformat()
            return p
        return None
    
    def delete_project(self, project_id: str, user_id: str):
        p = self.projects.get(project_id)
        if p and p["user_id"] == user_id:
            del self.projects[project_id]
    
    # Dataset operations
    def create_dataset(self, project_id: str, filename: str, file_path: str, size_bytes: int, metadata: Optional[Dict] = None):
        dataset_id = str(uuid4())
        dataset = {
            "id": dataset_id,
            "project_id": project_id,
            "filename": filename,
            "file_path": file_path,
            "size_bytes": size_bytes,
            "metadata": metadata,
            "upload_date": datetime.utcnow().isoformat(),
            "health_score": 75.0,
            "last_analysis_date": None
        }
        self.datasets[dataset_id] = dataset
        return dataset
    
    def get_dataset(self, dataset_id: str):
        return self.datasets.get(dataset_id)
    
    def get_project_datasets(self, project_id: str):
        return [d for d in self.datasets.values() if d["project_id"] == project_id]
    
    def update_dataset(self, dataset_id: str, data: Dict[str, Any]):
        d = self.datasets.get(dataset_id)
        if d:
            d.update(data)
            return d
        return None
    
    def delete_dataset(self, dataset_id: str):
        if dataset_id in self.datasets:
            del self.datasets[dataset_id]
    
    # Analysis operations
    def create_analysis(self, dataset_id: str, health_score: float, profile: Dict, recommendations: List[Dict]):
        analysis_id = str(uuid4())
        analysis = {
            "id": analysis_id,
            "dataset_id": dataset_id,
            "health_score": health_score,
            "profiling_data": profile,
            "recommendations": recommendations,
            "created_at": datetime.utcnow().isoformat()
        }
        self.analyses[analysis_id] = analysis
        return analysis
    
    def get_analysis(self, analysis_id: str):
        return self.analyses.get(analysis_id)
    
    def get_latest_analysis(self, dataset_id: str):
        analyses = [a for a in self.analyses.values() if a["dataset_id"] == dataset_id]
        return max(analyses, key=lambda x: x["created_at"]) if analyses else None
    
    def get_dataset_analyses(self, dataset_id: str):
        return [a for a in self.analyses.values() if a["dataset_id"] == dataset_id]
    
    # Team members
    def add_team_member(self, project_id: str, user_id: str, role: str = "editor"):
        member_id = str(uuid4())
        member = {
            "id": member_id,
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }
        self.team_members[member_id] = member
        return member
    
    def get_project_members(self, project_id: str):
        return [m for m in self.team_members.values() if m["project_id"] == project_id]
    
    def remove_team_member(self, member_id: str):
        if member_id in self.team_members:
            del self.team_members[member_id]
    
    # API Keys
    def create_api_key(self, user_id: str, name: str, key_hash: str):
        key_id = str(uuid4())
        key = {
            "id": key_id,
            "user_id": user_id,
            "name": name,
            "key_hash": key_hash,
            "created_at": datetime.utcnow().isoformat()
        }
        self.api_keys[key_id] = key
        return key
    
    def get_user_api_keys(self, user_id: str):
        return [k for k in self.api_keys.values() if k["user_id"] == user_id]
    
    def verify_api_key(self, key_hash: str) -> Optional[str]:
        for key in self.api_keys.values():
            if key["key_hash"] == key_hash:
                return key["user_id"]
        return None
    
    def delete_api_key(self, key_id: str):
        if key_id in self.api_keys:
            del self.api_keys[key_id]


# Global singleton instance
_mock_db = None

def get_mock_database():
    global _mock_db
    if _mock_db is None:
        _mock_db = MockDatabaseService()
    return _mock_db
