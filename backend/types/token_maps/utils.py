from functools import wraps


def display_creation_kickoff_message(message: str):
    def wrapper(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if '{}' in message:
                print(message.format(args[0].data_file_name))
            else:
                print(message)

            return func(*args, **kwargs)
        return func_wrapper
    return wrapper