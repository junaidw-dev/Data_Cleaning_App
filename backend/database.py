from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import Client
from uuid import uuid4

class DatabaseService:
    """Database operations service."""
    
    def __init__(self, client: Client):
        self.db = client
    
    # ==================== User Operations ====================
    
    def create_user(self, email: str, password_hash: str, full_name: str):
        """Create a new user."""
        user_id = str(uuid4())
        response = self.db.table("users").insert({
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "subscription_tier": "free",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_email(self, email: str):
        """Get user by email."""
        response = self.db.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_id(self, user_id: str):
        """Get user by ID."""
        response = self.db.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    def update_user(self, user_id: str, data: Dict[str, Any]):
        """Update user profile."""
        data["updated_at"] = datetime.utcnow().isoformat()
        response = self.db.table("users").update(data).eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    def update_user_password(self, user_id: str, password_hash: str):
        """Update user password."""
        return self.update_user(user_id, {"password_hash": password_hash})
    
    # ==================== Project Operations ====================
    
    def create_project(self, user_id: str, name: str, description: Optional[str] = None):
        """Create a new project."""
        project_id = str(uuid4())
        response = self.db.table("projects").insert({
            "id": project_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def get_project(self, project_id: str, user_id: str):
        """Get project by ID (with ownership check)."""
        response = (
            self.db.table("projects")
            .select("*")
            .eq("id", project_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None
    
    def get_user_projects(self, user_id: str):
        """Get all projects for a user."""
        response = (
            self.db.table("projects")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    
    def update_project(self, project_id: str, user_id: str, data: Dict[str, Any]):
        """Update project."""
        data["updated_at"] = datetime.utcnow().isoformat()
        response = (
            self.db.table("projects")
            .update(data)
            .eq("id", project_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None
    
    def delete_project(self, project_id: str, user_id: str):
        """Delete a project and its datasets."""
        self.db.table("projects").delete().eq("id", project_id).eq("user_id", user_id).execute()
    
    # ==================== Dataset Operations ====================
    
    def create_dataset(self, project_id: str, filename: str, file_path: str, size_bytes: int, metadata: Optional[Dict] = None):
        """Create a new dataset record."""
        dataset_id = str(uuid4())
        response = self.db.table("datasets").insert({
            "id": dataset_id,
            "project_id": project_id,
            "filename": filename,
            "file_path": file_path,
            "size_bytes": size_bytes,
            "metadata": metadata,
            "upload_date": datetime.utcnow().isoformat(),
        }).execute()
        return response.data[0] if response.data else None
    
    def get_dataset(self, dataset_id: str):
        """Get dataset by ID."""
        response = self.db.table("datasets").select("*").eq("id", dataset_id).execute()
        return response.data[0] if response.data else None
    
    def get_project_datasets(self, project_id: str):
        """Get all datasets in a project."""
        response = (
            self.db.table("datasets")
            .select("*")
            .eq("project_id", project_id)
            .order("upload_date", desc=True)
            .execute()
        )
        return response.data
    
    def update_dataset(self, dataset_id: str, data: Dict[str, Any]):
        """Update dataset."""
        response = self.db.table("datasets").update(data).eq("id", dataset_id).execute()
        return response.data[0] if response.data else None
    
    def delete_dataset(self, dataset_id: str):
        """Delete a dataset."""
        self.db.table("datasets").delete().eq("id", dataset_id).execute()
    
    # ==================== Analysis Results ====================
    
    def create_analysis(self, dataset_id: str, health_score: float, profile: Dict, recommendations: List[Dict]):
        """Create an analysis result."""
        analysis_id = str(uuid4())
        response = self.db.table("analysis_results").insert({
            "id": analysis_id,
            "dataset_id": dataset_id,
            "health_score": health_score,
            "profiling_data": profile,
            "recommendations": recommendations,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def get_analysis(self, analysis_id: str):
        """Get analysis by ID."""
        response = self.db.table("analysis_results").select("*").eq("id", analysis_id).execute()
        return response.data[0] if response.data else None
    
    def get_latest_analysis(self, dataset_id: str):
        """Get the latest analysis for a dataset."""
        response = (
            self.db.table("analysis_results")
            .select("*")
            .eq("dataset_id", dataset_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
    
    def get_dataset_analyses(self, dataset_id: str):
        """Get all analyses for a dataset."""
        response = (
            self.db.table("analysis_results")
            .select("*")
            .eq("dataset_id", dataset_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    
    # ==================== Team Members ====================
    
    def add_team_member(self, project_id: str, user_id: str, role: str = "editor"):
        """Add a team member to a project."""
        member_id = str(uuid4())
        response = self.db.table("team_members").insert({
            "id": member_id,
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def get_project_members(self, project_id: str):
        """Get all team members for a project."""
        response = (
            self.db.table("team_members")
            .select("*")
            .eq("project_id", project_id)
            .execute()
        )
        return response.data
    
    def remove_team_member(self, member_id: str):
        """Remove a team member."""
        self.db.table("team_members").delete().eq("id", member_id).execute()
    
    # ==================== API Keys ====================
    
    def create_api_key(self, user_id: str, name: str, key_hash: str):
        """Create an API key."""
        key_id = str(uuid4())
        response = self.db.table("api_keys").insert({
            "id": key_id,
            "user_id": user_id,
            "name": name,
            "key_hash": key_hash,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    
    def get_user_api_keys(self, user_id: str):
        """Get all API keys for a user."""
        response = (
            self.db.table("api_keys")
            .select("id, name, key_hash, created_at, last_used")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    
    def verify_api_key(self, key_hash: str) -> Optional[str]:
        """Verify an API key and return the user_id."""
        response = self.db.table("api_keys").select("user_id").eq("key_hash", key_hash).execute()
        return response.data[0]["user_id"] if response.data else None
    
    def delete_api_key(self, key_id: str):
        """Delete an API key."""
        self.db.table("api_keys").delete().eq("id", key_id).execute()
