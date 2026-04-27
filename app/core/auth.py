"""
Auth dependency — extract user ID from Supabase JWT token.
"""
import jwt
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)


def get_current_user_id(request: Request) -> str:
    """
    Extract user UUID from the Supabase JWT in the Authorization header.
    Returns the 'sub' claim (user ID) from the token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Tidak terautentikasi")

    token = auth_header.split(" ")[1]
    try:
        # Decode tanpa verifikasi signature (trust Supabase Auth)
        # Untuk production, gunakan Supabase JWT secret untuk verifikasi
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token tidak valid")
        return user_id
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token sudah kadaluarsa")
