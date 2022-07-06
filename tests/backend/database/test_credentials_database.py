import pytest

from backend.src.database.credentials_database import CredentialsDatabase


@pytest.fixture(autouse=True)
def credentials_database() -> CredentialsDatabase:
    return CredentialsDatabase()


def test_credentials_database(credentials_database):
    username = 'doctor_pepper'

    credentials_database.initialize_user(username, 'doctorpepper@poppers.com', 'doctorpepperpassword')

    assert credentials_database.usernames() == [username]
    assert credentials_database.query_password(username) == 'doctorpepperpassword'
    assert list(credentials_database.mail_addresses()) == ['doctorpepper@poppers.com']

    credentials_database.remove_user(username)

    assert credentials_database.usernames() == []
    assert not list(credentials_database.mail_addresses())
