"""
Tests for models.
"""
import pytest
from assertpy import assert_that
from core.models import User
from django.contrib.auth import get_user_model


@pytest.fixture()
def default_user() -> User:
    email = "test@example.com"
    password = "test123qwerty"
    name = "Jan"
    surname = "Kowalski"
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name,
        surname=surname,
    )
    return user


@pytest.mark.django_db
def test_create_default_user(default_user):
    """Test: creating a default user"""

    # Given
    user = default_user

    # Then
    assert_that(user.email).is_equal_to(default_user.email)
    assert_that(user.check_password(default_user.password))
    assert_that(user.name).is_equal_to(default_user.name)
    assert_that(user.surname).is_equal_to(default_user.surname)
    assert_that(user.is_active).is_equal_to(True)
    assert_that(user.is_staff).is_equal_to(False)


@pytest.mark.django_db
def test_create_superuser():
    """Test: creating a superuser"""

    # Given
    user = get_user_model().objects.create_superuser(
        email="test@example.com",
        password="test123",
    )

    # Then
    assert_that(user.is_superuser).is_true()
    assert_that(user.is_staff).is_true()
