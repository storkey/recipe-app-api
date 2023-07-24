"""
Test custom Django management commands.
"""

from unittest.mock import patch

import pytest
from assertpy import assert_that
from django.core.management import call_command
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


@pytest.fixture
def patched_check():
    with patch("core.management.commands.wait_for_db.Command.check") as mock_check:
        yield mock_check


@pytest.fixture
def patched_sleep():
    with patch("time.sleep") as mock_sleep:
        yield mock_sleep


def test_wait_for_db_ready(patched_check, patched_sleep):
    patched_check.return_value = True
    call_command("wait_for_db")
    patched_check.assert_called_once_with(databases=["default"])


def test_wait_for_db_delay(patched_check):
    """Test waiting for database when getting OperationalError"""
    patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
    call_command("wait_for_db")
    assert_that(patched_check.call_count).is_equal_to(6)
    patched_check.assert_called_with(databases=["default"])
