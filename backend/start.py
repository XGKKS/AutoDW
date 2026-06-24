
import sys
import os

# 添加路径以便找到 app 模块
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
