from tests.conftest import MONGODB_TEST_LANGUAGE, MONGODB_TEST_USER


def test_instantiation(mongodb_instance):
    assert mongodb_instance.user == MONGODB_TEST_USER
    assert mongodb_instance.language == MONGODB_TEST_LANGUAGE

