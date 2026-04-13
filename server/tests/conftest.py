"""测试基础设施 — 异步 TestClient + 内存 SQLite + 伪造 JWT"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db
from app.main import app
from app.middleware.auth import create_token


# ---------- 内存 SQLite 引擎 ----------

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.commit()


# ---------- Fixtures ----------


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """为整个 session 提供一个 event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """每个测试用例前建表、后清表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """异步 HTTP 测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """直接获取测试用的 DB session"""
    async with TestSessionLocal() as session:
        yield session


# ---------- 辅助：创建社区 + 用户 + token ----------

async def _create_community_in_db(
    session: AsyncSession,
    name: str = "测试社区",
) -> "Community":
    """在数据库中创建社区"""
    from app.models.community import Community

    community = Community(name=name, total_units=500, total_area=30000.0, address="测试地址")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


async def _create_user_in_db(
    session: AsyncSession,
    openid: str = "dev_testuser",
    role: str = "owner",
    nickname: str = "测试用户",
    is_active: bool = True,
    community_id: str | None = None,
) -> "User":
    """在数据库中直接创建用户"""
    from app.models.user import User

    user = User(
        openid=openid,
        nickname=nickname,
        role=role,
        is_active=is_active,
        community_id=community_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_community(db_session: AsyncSession):
    """测试用社区"""
    return await _create_community_in_db(db_session)


@pytest_asyncio.fixture
async def owner_token(db_session: AsyncSession, test_community) -> str:
    """业主 token"""
    user = await _create_user_in_db(
        db_session, openid="dev_owner", role="owner", nickname="业主A",
        community_id=test_community.id,
    )
    return create_token(user.id, "owner")


@pytest_asyncio.fixture
async def property_token(db_session: AsyncSession, test_community) -> str:
    """物业 token"""
    user = await _create_user_in_db(
        db_session, openid="dev_property", role="property", nickname="物业A",
        community_id=test_community.id,
    )
    return create_token(user.id, "property")


@pytest_asyncio.fixture
async def committee_token(db_session: AsyncSession, test_community) -> str:
    """业委会 token"""
    user = await _create_user_in_db(
        db_session, openid="dev_committee", role="committee", nickname="业委会A",
        community_id=test_community.id,
    )
    return create_token(user.id, "committee")


@pytest_asyncio.fixture
async def owner_user(db_session: AsyncSession, test_community):
    """业主 User 对象"""
    return await _create_user_in_db(
        db_session, openid="dev_owner", role="owner", nickname="业主A",
        community_id=test_community.id,
    )


@pytest_asyncio.fixture
async def property_user(db_session: AsyncSession, test_community):
    """物业 User 对象"""
    return await _create_user_in_db(
        db_session, openid="dev_property", role="property", nickname="物业A",
        community_id=test_community.id,
    )


@pytest_asyncio.fixture
async def committee_user(db_session: AsyncSession, test_community):
    """业委会 User 对象"""
    return await _create_user_in_db(
        db_session, openid="dev_committee", role="committee", nickname="业委会A",
        community_id=test_community.id,
    )


def auth_header(token: str) -> dict:
    """构造 Authorization header"""
    return {"Authorization": f"Bearer {token}"}
