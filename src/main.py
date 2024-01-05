# 主程序入口
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address
from fastapi.middleware.gzip import GZipMiddleware
from src.articles import router as articles_router
from src.config import settings


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 仅允许本地和特定服务器访问
@app.middleware("http")
async def add_ip_filter_middleware(request: Request, call_next):
    response = await call_next(request)
    client_ip = ip_address(request.client.host)
    if client_ip not in [ip_address(ip) for ip in settings.allowed_ips]:
        return JSONResponse(status_code=403, content='IP ERROR' + str(client_ip))
    return response


app.include_router(articles_router.router)

# 启动命令 uvicorn src.main:app --reload --host 0.0.0.0 或直接运行该文件， --host 0.0.0.0 是为了本地程序可以连接，需要用本地ip：http://192.168.0.196:8000
if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True)
