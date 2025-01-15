import time
import inspect
import os
debug_mode_enabled = False


def get_debug_mode():
    global debug_mode_enabled
    return debug_mode_enabled


def toggle_debug_mode():
    global debug_mode_enabled
    debug_mode_enabled = not debug_mode_enabled


def print_debug(*args, **kwargs):
    global debug_mode_enabled
    if not debug_mode_enabled:
        return
    # Get the current frame (f_back gives the previous frame where the print_with_location was called)
    frame = inspect.currentframe().f_back
    # Get the file name and line number
    file_name = frame.f_code.co_filename
    line_number = frame.f_lineno

    # Add the file name and line number to the output
    print(
        f"debug - {os.path.basename(file_name)}:{line_number} - ", *args, **kwargs)


def get_debug_str(filename, lineno):
    current_time_with_ms = time.strftime(
        "%Y-%m-%d %H:%M:%S") + f".{int(time.time() * 1000) % 1000:03d}"
    if filename is not None:
        return f"[{current_time_with_ms}] [{os.path.basename(filename)}:{lineno}]"
    else:
        return f"[{current_time_with_ms}] {lineno}"


def d_print(*args, **kwargs):
    frame = inspect.stack()[1]  # Get the caller's frame
    filename = frame.filename
    lineno = frame.lineno
    print(get_debug_str(filename, lineno), *args, **kwargs)


def debug_func(func):
    def wrapper(*args, **kwargs):
        # if not get_debug_mode():
        #    return func(*args, **kwargs)
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(get_debug_str(None, f"'{func.__name__}' function"),
              f"executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper
# Example usage:
# print_with_location_and_time("This is a test message.")
