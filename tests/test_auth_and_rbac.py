import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import Role, BusinessElement
from ..models.rbac import AccessRule

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, db_session: AsyncSession):
    admin_role = Role(id=1, name="admin")
    user_role = Role(id=3, name="user")
    db_session.add_all([admin_role, user_role])
    await db_session.commit()

    response = await client.post("/auth/register", json={
        "first_name": "John", "last_name": "Doe", 
        "email": "john@test.com", "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@test.com"

    login_response = await client.post("/auth/login", json={
        "email": "john@test.com", "password": "password123"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    
    assert "access_token" in client.cookies

@pytest.mark.asyncio
async def test_rbac_forbidden_and_allowed(client: AsyncClient, db_session: AsyncSession):
    admin_role = Role(id=1, name="admin")
    user_role = Role(id=2, name="user")
    db_session.add_all([admin_role, user_role])
    
    product_element = BusinessElement(id=1, name="products")
    db_session.add(product_element)
    await db_session.commit()

    await client.post("/auth/register", json={
        "first_name": "Jane", "last_name": "Doe", 
        "email": "jane@test.com", "password": "password123"
    })
    
    login_response = await client.post("/auth/login", json={
        "email": "jane@test.com", "password": "password123"
    })
    
    token = login_response.json()["access_token"]
    client.cookies.set("access_token", token)

    forbidden_response = await client.get("/products/")
    assert forbidden_response.status_code == 403

    rule = AccessRule(role_id=2, element_id=1, read=True, read_all=True)
    db_session.add(rule)
    await db_session.commit()

    allowed_response = await client.get("/products/")
    assert allowed_response.status_code == 200