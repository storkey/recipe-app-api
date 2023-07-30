"""
Test for the Django admin modifications
"""
import pytest
from assertpy import assert_that
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def normal_user():
    user = get_user_model().objects.create_user(
        email="test@example.com", password="1231231password", name="Test User"
    )
    return user


@pytest.fixture
def admin_user():
    admin_user = get_user_model().objects.create_superuser(
        email="admin@example.com", password="test123qwerty"
    )
    return admin_user


@pytest.mark.django_db
def test_users_list(admin_user, normal_user):
    """Test that users are listed on page."""
    normal_user = normal_user
    admin_user = admin_user
    client = Client()
    client.force_login(admin_user)
    url = reverse("admin:core_user_changelist")
    response = client.get(url)
    assert_that(response.status_code).is_equal_to(status.HTTP_302_FOUND)
    user = get_user_model().objects.all()
    assert_that(user[0].name).is_equal_to(normal_user.name)
    assert_that(user[0].email).is_equal_to(normal_user.email)


@pytest.mark.django_db
def test_edit_user_page(normal_user, admin_user):
    """Test that user is listed on page."""
    normal_user = normal_user
    admin_user = admin_user
    client = Client()
    client.force_login(admin_user)
    url = reverse("admin:core_user_change", args=[normal_user.id])
    res = client.get(url)
    assert_that(res.status_code).is_equal_to(status.HTTP_302_FOUND)
