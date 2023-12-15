from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address
from fastapi.middleware.gzip import GZipMiddleware

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

@app.get("/protected")
def protected_endpoint():
    return {"message": "只有授权IP才能访问的API端点"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)