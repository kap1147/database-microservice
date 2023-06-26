import logging
from typing import Callable

def call_validate_func_on_data(data, validate_func: Callable, app_logger: logging = None) -> bool:
    try:
        validate_func(data)
        return True
    except Exception as err:
        if app_logger:
            app_logger.exception(f"The following data failed check using function {str(validate_func)}: {data}\nErr: {err}")
        print(err)
        return False