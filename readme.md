# Open API

![img.png](docs/overview-0.1.1.png)

## TODO

- [ ] specific scenario-based prompt
- [ ] user management on database
- [ ] callable robuster api

## Features

- [x] 支持 openai / moonshot API (2024-03-28)

## Configuration

参考`.env.sample`配置对应环境变量到 `.env` 文件内。

```shell
poetry shell
poetry install
```

## Run

```shell
uvicorn main:app --reload
```

访问 `http://localhost:8000/docs` 查看各 API。

## Bugfix

### NotGiven

如果不加这个的话，swagger 里会显示为 null
