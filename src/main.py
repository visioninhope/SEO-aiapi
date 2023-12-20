# 主程序入口
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address
from fastapi.middleware.gzip import GZipMiddleware
from src.articles import router as articles_router

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 允许访问的IP列表
ALLOWED_IPS = ['127.0.0.1', '35.87.195.44']

# 仅允许本地和特定服务器访问
@app.middleware("http")
async def add_ip_filter_middleware(request: Request, call_next):
    response = await call_next(request)
    client_ip = ip_address(request.client.host)
    if client_ip not in [ip_address(ip) for ip in ALLOWED_IPS]:
        return JSONResponse(status_code=403, content='IP ERROR')
    return response


app.include_router(articles_router.router)

# 启动命令 uvicorn src.main:app --reload 或直接运行该文件
if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True)
