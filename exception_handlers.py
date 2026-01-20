from exceptions import EmailNotFound, PassEmailIncorrect
from fastapi.responses import JSONResponse
from fastapi import Request



def register_handlers(app):
    @app.exception_handler(EmailNotFound)
    async def email_not_found_handler(request: Request,exc: EmailNotFound):
        return JSONResponse(
            status_code=404,
            content={"detail":f"{exc}"}
        )
        
    @app.exception_handler(PassEmailIncorrect)
    async def pass_email_incorrect_handler(request: Request,exc: PassEmailIncorrect):
        return JSONResponse(
            status_code=404,
            content={"detail":f"{exc}"}
        )