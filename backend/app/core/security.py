"""安全相关工具函数。"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 当前项目仍兼容原始明文密码字段，但这里先准备好 bcrypt 能力，后续升级时可直接切换。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希密码是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """把明文密码转换为可持久化保存的哈希字符串。"""
    return pwd_context.hash(password)


def create_access_token(subject: str) -> str:
    """为指定主体生成 JWT 访问令牌。"""
    # 目前 token 的 subject 约定为用户主键 ID。
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """解码 JWT 访问令牌并返回其中的载荷。"""
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


__all__ = [
    "JWTError",
    "create_access_token",
    "decode_access_token",
    "get_password_hash",
    "pwd_context",
    "verify_password",
]
