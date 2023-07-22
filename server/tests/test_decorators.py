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

