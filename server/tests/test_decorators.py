import time
import pytest
import finance.decorators as deco
from typing import Callable, Any

@pytest.mark.parametrize("func, args, expected", [
    (sum, [1, 2, 3, 4], 10),
    (all, [True, False, False, True], False),
    (lambda x: 0, None, 0)
])
class TestCaptureLogsDecorator:
    def test_capture_logs_no_returns(self, func: Callable, args: Any, expected: Any) -> None:
        """Test the `capture_logs` decorator for functions without return values but with stdout logs

        Args:
            func (Callable): Function to be decorated
            args (Any): Arguments for the decorated function
            expected (Any): Expected log from stdout
        """
        @deco.capture_logs
        def test_func(args):
            print(func(args), end="")

        assert test_func(args) == (None, f"{expected}")

    def test_capture_logs_no_logs(self, func: Callable, args: Any, expected: Any) -> None:
        """Test the `capture_logs` decorator for functions without stdout logs but with return values

        Args:
            func (Callable): Function to be decorated
            args (Any): Arguments for the decorated function
            expected (Any): Expected return values
        """
        @deco.capture_logs
        def test_func(args):
            return func(args)

        assert test_func(args) == (expected, "")

    def test_capture_logs_with_returns_and_logs(self, func: Callable, args: Any, expected: Any) -> None:
        """Test the `capture_logs` decorator for functions with both return values and stdout logs
        Args:
            func (Callable): Function to be decorated
            args (Any): Arguments for the decorated function
            expected (Any): Expected return values and stdout logs
        """
        @deco.capture_logs
        def test_func(args):
            result = func(args)
            print(result, end="")
            return result

        assert test_func(args) == (expected, f"{expected}")


class TestDataCacheDecorator:
    def test_data_cache(self) -> None:
        """Test whether the `data_cache` decorator correctly cache evaluation results
        """
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

    def test_data_cache_expiration(self) -> None:
        """Test whether the `data_cache` decorator correctly re-evaluate expired results
        """
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

    def test_data_cache_overflow(self) -> None:
        """Test whether the `data_cache` decorator correctly remove old results when the cache is full
        """
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
