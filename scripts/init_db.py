#!/usr/bin/env python3
"""
数据库初始化脚本

使用方法：
    python scripts/init_db.py

功能：
    1. 创建所有数据库表
    2. 可选：插入测试数据（包括 admin 用户）
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import *  # noqa: F401 - 导入所有模型以注册


def init_database():
    """创建所有数据库表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def insert_test_data():
    """插入测试数据（可选）"""
    db = SessionLocal()
    try:
        from app.models.user import User, UserPreference
        from app.utils.security import hash_password

        # 创建 admin 用户（如果不存在）
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                is_admin=True,
                weight_vector=0.7,
                weight_keyword=0.3,
                author_bonus=0.5
            )
            db.add(admin_user)
            db.flush()

            # 创建 admin 偏好设置
            admin_pref = UserPreference(
                user_id=admin_user.id,
                keywords=[],
                authors=[]
            )
            db.add(admin_pref)
            print("Admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Is Admin: True")
        else:
            # 确保现有用户有 is_admin 字段
            if not hasattr(admin_user, 'is_admin') or not admin_user.is_admin:
                admin_user.is_admin = True
                print("Updated admin user with is_admin=True")
            else:
                print("Admin user already exists, skipping...")

        # 创建普通测试用户（如果不存在）
        test_user = db.query(User).filter(User.username == "test").first()
        if not test_user:
            test_user = User(
                username="test",
                password_hash=hash_password("test123"),
                is_admin=False,
                weight_vector=0.7,
                weight_keyword=0.3,
                author_bonus=0.5
            )
            db.add(test_user)
            db.flush()

            # 创建测试用户偏好
            test_pref = UserPreference(
                user_id=test_user.id,
                keywords=["transformer", "diffusion", "large language model"],
                authors=["Yann LeCun", "Geoffrey Hinton"]
            )
            db.add(test_pref)
            print("\nTest user created:")
            print("  Username: test")
            print("  Password: test123")
            print("  Is Admin: False")
        else:
            print("Test user already exists, skipping...")

        db.commit()
        print("\nTest data inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error inserting test data: {e}")
        raise
    finally:
        db.close()


def set_admin(username: str):
    """设置指定用户为 admin"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            return

        user.is_admin = True
        db.commit()
        print(f"User '{username}' is now an admin")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("arXiv Daily - Database Initialization")
    print("=" * 50)

    # 创建表
    init_database()

    # 处理命令行参数
    if "--with-test-data" in sys.argv:
        insert_test_data()
    elif "--set-admin" in sys.argv:
        # 查找 --set-admin 后面的用户名
        try:
            idx = sys.argv.index("--set-admin")
            if idx + 1 < len(sys.argv):
                username = sys.argv[idx + 1]
                set_admin(username)
            else:
                print("Error: --set-admin requires a username argument")
                print("Usage: python scripts/init_db.py --set-admin <username>")
        except ValueError:
            pass
    else:
        print("\nOptions:")
        print("  --with-test-data    Insert test data (admin + test users)")
        print("  --set-admin <user>  Set specified user as admin")

    print("\nDone!")


if __name__ == "__main__":
    main()
