import time
import pytest
import finance.decorators as deco


@pytest.mark.parametrize("func, args, expected", [
    (sum, [1, 2, 3, 4], 10),
    (all, [True, False, False, True], False),
    (lambda x: 0, None, 0)
])
class TestCaptureLogsDecorator:
    def test_capture_logs_no_returns(self, func, args, expected):
        @deco.capture_logs
        def test_func(args):
            print(func(args), end="")

        assert test_func(args) == (None, f"{expected}")

    def test_capture_logs_no_logs(self, func, args, expected):
        @deco.capture_logs
        def test_func(args):
            return func(args)

        assert test_func(args) == (expected, "")

    def test_capture_logs_with_returns_and_logs(self, func, args, expected):
        @deco.capture_logs
        def test_func(args):
            result = func(args)
            print(result, end="")
            return result

        assert test_func(args) == (expected, f"{expected}")


class TestDataCacheDecorator:
    def test_data_cache(self):
        @deco.capture_logs
        @deco.data_cache(maxsize=128, expiration_seconds=3600)
        def add_one(x):
            return x + 1

        _, output = add_one(1)
        assert output == ""
        _, output = add_one(1)
        assert "Cache hit" in output
        _, output = add_one(2)
        assert "Cache hit" not in output

    def test_data_cache_expiration(self):
        @deco.capture_logs
        @deco.data_cache(maxsize=128, expiration_seconds=0.5)
        def add_one(x):
            return x + 1

        _, output = add_one(1)
        assert output == ""
        _, output = add_one(1)
        assert "Cache hit" in output
        time.sleep(0.5)
        _, output = add_one(1)
        assert "Cache expired" in output

    def test_data_cache_maxsize(self):
        @deco.capture_logs
        @deco.data_cache(maxsize=2, expiration_seconds=3600)
        def add_one(x):
            return x + 1

        _, output = add_one(1)
        assert output == ""
        _, output = add_one(2)
        assert output == ""
        _, output = add_one(3)
        assert "Cache full" in output
