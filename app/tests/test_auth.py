from app.auth.auth_schemas import UserCreateModel

auth_prefix = f"/api/auth"


def test_user_creation(fake_session, fake_user_service, test_client):
    signup_data = {
        "username": "string",
        "email": "string",
        "password": "stringst",
        "first_name": "string",
        "last_name": "string",
    }

    response = test_client.post(url=f"{auth_prefix}/signup", json=signup_data)

    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.user_exists_called_once_with(
        signup_data["email"], fake_session
    )
    assert fake_user_service.create_user_called_once_with(
        signup_data["email"], fake_session
    )
