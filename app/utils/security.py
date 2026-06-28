"""
安全相关工具函数
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密

    Args:
        password: 明文密码

    Returns:
        哈希后的密码（UTF-8 字符串）
    """
    # bcrypt 需要 bytes 输入
    password_bytes = password.encode('utf-8')
    # 生成 salt 并哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 返回字符串形式
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        是否匹配
    """
    try:
        # 转换为 bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # 验证
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False
