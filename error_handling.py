"""
Global error handling helpers.
- Installs a sys.excepthook to log uncaught exceptions.
- Provides a decorator `handle_exceptions` to wrap functions and log exceptions.
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('error_handling')


def _excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let the default handler handle keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

# Install as the global excepthook
try:
    sys.excepthook = _excepthook
except Exception:
    # if something goes wrong, don't crash importers
    pass


def handle_exceptions(func):
    """Decorator to catch exceptions in functions, log them, and re-raise.

    Use this to wrap entry points or important functions:
        @handle_exceptions
        def main():
            ...
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception("Exception in %s", getattr(func, '__name__', str(func)))
            raise
    wrapper.__name__ = getattr(func, '__name__', 'wrapper')
    wrapper.__doc__ = getattr(func, '__doc__', None)
    return wrapper
