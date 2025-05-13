def test_runner():
    from core.runner import run_tests
    run_tests({"prompt": "test"})
    assert True