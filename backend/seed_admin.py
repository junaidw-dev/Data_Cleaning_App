import asyncio
import os

from auth import AuthService
from database import DatabaseService
from config import get_supabase_client


def get_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


async def seed_admin_user() -> None:
    email = get_env("ADMIN_EMAIL")
    password = get_env("ADMIN_PASSWORD")
    full_name = os.getenv("ADMIN_NAME", "Admin User").strip() or "Admin User"

    db = DatabaseService(get_supabase_client())
    existing = await db.get_user_by_email(email)
    password_hash = AuthService.hash_password(password)

    if existing:
        await db.update_user(existing["id"], {
            "full_name": full_name,
            "password_hash": password_hash,
        })
        print(f"Updated admin user: {email}")
        return

    user = await db.create_user(email=email, password_hash=password_hash, full_name=full_name)
    if not user:
        raise RuntimeError("Failed to create admin user")

    print(f"Created admin user: {email}")


if __name__ == "__main__":
    asyncio.run(seed_admin_user())
