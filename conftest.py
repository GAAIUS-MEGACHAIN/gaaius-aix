import asyncio
import inspect

def pytest_pyfunc_call(pyfuncitem):
    """
    Fallback runner for async test functions when pytest-asyncio isn't
    available. This allows existing async tests (async def ...) to run
    by executing them in a fresh asyncio event loop.
    """
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(testfunction(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True
    # Not a coroutine function -> let pytest handle it
    return None
