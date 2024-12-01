# shop-backend

一个基于FastAPI的在线商城后端。

本仓库将于**3个月后**转为私有。

学号：202230442159

姓名：卢俊杰


## 项目依赖

 - Python >= 3.12
 - `requirements.txt`中列出的所有包

这是推荐依赖。更旧的版本可能可以正常工作但未经测试。


## 启动项目

首先根据`config.py`创建`config.yaml`。

### Docker

```sh
# mkdir /srv/shop/{mysql,log,file}
# docker compose up
```

### 手动

 - 创建一个虚拟环境（可选）
 - `pip install -r requirements.txt`
 - `uvicorn app:app`


## 开发指引

源码树解释如下：

Dockerfile, docker-\*: Docker部署相关。

config.py: 加载用户配置。

alembic: alembic根目录，用于数据库迁移。

app: 应用源码。

 - models: sqlalchemy ORM 模型.
 - routers: API入口点与主要业务逻辑。
 - schemas: API参数与返回值schema.
 - utils: 实用工具。
 - auth.py: 鉴权逻辑。
 - db.py: 数据库会话管理。


## 小贴士

当你成功启动项目之后，如果在配置中启用了在线文档（`config.yaml`中的`enable_doc`配置项），你可以通过访问`http://${BaseURL}/docs`来获取一份详细的API定义文档。


