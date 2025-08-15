import time
import logging


def retry(
    tries=-1, delay=0, max_delay=None, backoff=1, exceptions=Exception, log=False
):
    """Retry Decorator with arguments
    Args:
        tries (int): The maximum number of attempts. Defaults to -1 (infinite)
        delay (int, optional): Delay between attempts (seconds). Defaults to 0
        max_delay (int, optional): The maximum value of delay (seconds). Defaults to None (Unlimited)
        backoff (int, optional): Multiplier applied to delay between attempts (seconds). Defaults to 1 (No backoff)
        exceptions (tuple, optional): Types of exceptions to catch. Defaults to Exception (all)
        log (bool, optional): Print debug logs. Defaults to False
    """

    def retry_decorator(func):
        def retry_wrapper(*args, **kwargs):
            nonlocal tries, delay, max_delay, backoff, exceptions, log
            while tries:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    tries -= 1

                    # Reached to maximum tries
                    if not tries:
                        raise

                    # Log the retry logs for the given function
                    if log:
                        logging.error(f"Retrying {func.__name__} in {delay} seconds")

                    # Apply delay between requests
                    time.sleep(delay)

                    # Adjust the next delay according to backoff
                    delay *= backoff

                    # Adjust maximum delay duration
                    if max_delay is not None:
                        delay = min(delay, max_delay)

        return retry_wrapper

    return retry_decorator
