# Cancelled Error

https://docs.python.org/3.11/library/asyncio-runner.html#id3

Keyboard interruption with Ctrl+C or SIGINT when an asyncio loop is running triggers:
- an asyncio.CancelledError
- a KeyboardInterrupt
