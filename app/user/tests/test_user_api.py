import pytest
from assertpy import assert_that
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

client = APIClient()


@pytest.fixture
def user_data_payload():
    payload = {
        "email": "test_pytest4@test.com",
        "password": "testingPassw0rd1253",
        "name": "Jan",
    }
    return payload


@pytest.fixture
def user_force_auth_response(user_data_payload):
    user = get_user_model().objects.create_user(
        email=user_data_payload["email"],
        password=user_data_payload["password"],
        name=user_data_payload["name"],
    )
    response = client.force_authenticate(user=user)
    return response


def user_api_general_assertions(user_data):
    response = client.post(CREATE_USER_URL, user_data, format="json")
    response_data = response.json()
    user = get_user_model().objects.get(email=user_data["email"])
    assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
    assert_that(response_data["email"]).is_equal_to(user_data["email"])
    assert_that(response_data["name"]).is_equal_to(user_data["name"])
    assert_that(user_data["password"]).is_not_in(response_data)
    assert_that(user.check_password(user_data["password"]))


@pytest.mark.django_db
def test_create_user_api(user_data_payload):
    """Test user creation"""
    user_api_general_assertions(user_data_payload)


@pytest.mark.django_db
def test_create_user_email_required(user_data_payload):
    """Test if email is required during user creation"""
    del user_data_payload["email"]
    response = client.post(CREATE_USER_URL, user_data_payload, format="json")
    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_create_token_for_user(user_data_payload):
    """Test generates token for valid credentials"""
    response = client.post(CREATE_USER_URL, user_data_payload, format="json")
    response = client.post(
        TOKEN_URL,
        data={
            "email": user_data_payload["email"],
            "password": user_data_payload["password"],
        },
    )
    response_data = response.json()
    assert_that(response_data).contains_key("token")
    assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)


@pytest.mark.django_db
def test_create_token_wrong_credentials(user_data_payload):
    """Test returns errors if credentials invalid"""
    response = client.post(CREATE_USER_URL, user_data_payload, format="json")
    payload = {"email": "wrong_email@testwrong.com", "password": "bad_passw0rd1"}
    response = client.post(TOKEN_URL, payload)
    response_data = response.json()
    assert_that(response_data).does_not_contain_key("token")
    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_create_token_blank_password(user_data_payload):
    response = client.post(CREATE_USER_URL, user_data_payload, format="json")
    payload = {"email": user_data_payload["email"], "password": ""}
    response = client.post(TOKEN_URL, payload)
    assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_retrieve_user_unauthorized(user_data_payload):
    """Test authentication is required for users."""
    response = client.get(ME_URL, user_data_payload)
    assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
def test_retrieve_profile_success(user_force_auth_response, user_data_payload):
    """Test retrieving profile for logged in user."""
    response = user_force_auth_response
    response = client.get(ME_URL)
    response_data = response.json()
    assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
    assert_that(response_data["email"]).is_equal_to(user_data_payload["email"])


@pytest.mark.django_db
def test_post_me_not_allowed(user_force_auth_response):
    """Test POST is not allowed for the user/me endpoint."""
    response = user_force_auth_response
    response = client.post(ME_URL, {})
    assert_that(response.status_code).is_equal_to(status.HTTP_405_METHOD_NOT_ALLOWED)


@pytest.mark.django_db
def test_update_user(user_force_auth_response, user_data_payload):
    """Test updating the user profile for the authenticated user."""
    response = user_force_auth_response
    payload = {"name": "Janusz", "password": "TheNEwesetPassw0rdEver2"}
    response = client.patch(ME_URL, payload)
    user = get_user_model().objects.get(email=user_data_payload["email"])
    assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
    assert_that(user.name).is_equal_to(payload["name"])
    assert_that(user.check_password(payload["password"])).is_true()
