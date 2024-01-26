# 主程序入口
import http
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address
from fastapi.middleware.gzip import GZipMiddleware
from src.articles import router as articles_router
from src.documents import router as documents_router
from src.adventures import router as adventures_router
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO, filename=settings.log_file, format='%(asctime)s: %(levelname)s - %(message)s')

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 仅允许本地和特定服务器访问
@app.middleware("http")
async def add_ip_filter_middleware(request: Request, call_next):
    response = await call_next(request)
    client_ip = ip_address(request.client.host)
    if client_ip not in [ip_address(ip) for ip in settings.allowed_ips]:
        return JSONResponse(status_code=403, content='IP ERROR - ' + str(client_ip))
    return response

# 通用异常捕获
@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, e: Exception):
    logging.error(str(e))
    return JSONResponse(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, content={'message': str(e)})

app.include_router(articles_router.router)
app.include_router(documents_router.router)
app.include_router(adventures_router.router)

# 启动命令 uvicorn src.main:app --reload --host 0.0.0.0 或直接运行该文件， --host 0.0.0.0 是为了本地程序可以连接，需要用本地ip：http://192.168.0.196:8000
if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True, host='0.0.0.0')
