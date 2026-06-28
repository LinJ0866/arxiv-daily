"""
认证 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.config import settings
from app.database import get_db
from app.models.user import User, UserPreference
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["认证"])

# OAuth2 方案（必须认证）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# OAuth2 方案（可选认证，不自动报错）
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def create_access_token(data: dict) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（FastAPI 依赖注入）

    用于需要认证的接口：
    ```python
    @router.get("/protected")
    def protected_route(user: User = Depends(get_current_user)):
        return {"user": user.username}
    ```
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def get_optional_user(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> User | None:
    """
    获取当前用户（可选）

    用于可选认证的接口：
    ```python
    @router.get("/public")
    def public_route(user: User | None = Depends(get_optional_user)):
        if user:
            return {"msg": f"Hello {user.username}"}
        return {"msg": "Hello anonymous"}
    ```
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        return None

    return db.query(User).filter(User.id == user_id).first()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    - **username**: 用户名（3-50 字符）
    - **password**: 密码（至少 6 字符）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 创建用户
    hashed_password = hash_password(user_data.password)
    user = User(username=user_data.username, password_hash=hashed_password)
    db.add(user)
    db.flush()  # 获取 user.id

    # 创建空的偏好设置
    preference = UserPreference(user_id=user.id, keywords=[], authors=[])
    db.add(preference)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    返回 JWT Token
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    需要认证
    """
    return current_user


from pydantic import BaseModel

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class ProfileUpdate(BaseModel):
    username: str = None


@router.put("/password")
def update_password(
    data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（至少 6 字符）
    """
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )

    # 验证旧密码
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # 更新密码
    current_user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"status": "success", "message": "Password updated"}


@router.put("/profile")
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改个人信息

    - **username**: 新用户名（可选）
    """
    if data.username:
        # 检查用户名是否已存在
        existing = db.query(User).filter(
            User.username == data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = data.username

    db.commit()
    db.refresh(current_user)

    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
        }
    }
