import logging

from fastapi import Response, Request


async def exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected exception {request} {exc}")
    return Response(status_code=500)
