from pprint import pprint

import yaml
from jinja2 import Environment, FileSystemLoader

from settings import settings
from src.path import PROJECT_PATH

env = Environment(loader=FileSystemLoader(PROJECT_PATH))
template = env.get_template('wechaty_bot.yml')

rendered_yaml = template.render({
    "version": settings.version
})
yaml_dict = yaml.safe_load(rendered_yaml)

pprint(yaml_dict)
