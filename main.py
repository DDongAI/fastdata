import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.v1.api import api_router
from config.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS，仅允许特定的域名或IP访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["192.168.140.84", "127.0.0.1"],  # 仅允许该域名或IP访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def restrict_access(request: Request, call_next):
    """
    自定义中间件，进一步限制访问来源
    :param request:
    :param call_next:
    :return:
    """
    # 定义允许的来源列表
    allowed_origins = ["192.168.140.84", "127.0.0.1", "192.168.0.100"]
    origin = request.headers.get("origin")
    client_ip = request.client.host  # 获取客户端的IP地址
    client_port = request.client.port
    print(f"origin: {origin}, client_ip: {client_ip}, client_port：{client_port}")
    client = client_ip + ":" + str(client_port)
    print(client)
    # 如果客户端 IP 不在允许的来源列表中，则返回 403 错误
    if client_ip not in allowed_origins:
        return JSONResponse(
            content={"code": 403, "message": "Forbidden: Access denied"},
            status_code=403,
        )
    response = await call_next(request)
    return response


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "code": 200,
        "message": "success",
        "data": "非法访问，请停止您的行为！",
    }


# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn main:app --host=0.0.0.0  --port=8000
