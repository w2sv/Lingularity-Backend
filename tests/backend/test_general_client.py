from backend.src.database.general_client import GeneralMongoDBClient


def test_general_client():
    client = GeneralMongoDBClient()

    username = 'doctor_pepper'

    client.initialize_user('doctor_pepper', 'doctorpepper@poppers.com', 'doctorpepperpassword')

    assert client.usernames() == [username]
    assert client.query_password(username) == 'doctorpepperpassword'
    assert list(client.mail_addresses()) == ['doctorpepper@poppers.com']

    client.remove_user(username)

    assert client.usernames() == []
    assert not list(client.mail_addresses())
