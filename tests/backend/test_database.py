def test_instantiation(mongodb_instance):
    assert mongodb_instance.user == 'janek'
    assert mongodb_instance.language == 'Italian'
