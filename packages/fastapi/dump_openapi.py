import json


def dump_openapi(app):
    # Your route definitions here
    openapi_schema = app.openapi()
    
    # Dump to file
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
