from wechaty_puppet import FileBox as WechatPuppetFileBox
from wechaty_puppet.file_box import FileBoxOptionsBase, FileBoxOptionsUrl


class FileBox(WechatPuppetFileBox):
    
    def __init__(self, options: FileBoxOptionsBase):
        super().__init__(options)
        
        # 不加这个，图片会发不出去
        if isinstance(options, FileBoxOptionsUrl):
            self.url = options.url  # https://github.com/wechaty/python-wechaty/issues/356#issuecomment-1228024344
