import sys
from io import StringIO
from typing import Callable, Any, Tuple


def capture_logs(func: Callable[..., Any]) -> Callable[..., Tuple[Any, str]]:
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, str]:
        captured_stdout = sys.stdout
        sys.stdout = captured_buffer = StringIO()
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = captured_stdout

        captured_logs = captured_buffer.getvalue()
        return result, captured_logs

    return wrapper
