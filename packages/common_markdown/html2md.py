from markdownify import MarkdownConverter as RawMarkdownConverter


class MarkdownConverter(RawMarkdownConverter):
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """
    
    def __init__(self, md_with_img=False, **kwargs):
        super().__init__(**kwargs)
        self.md_with_img = md_with_img
    
    def convert_img(self, el, text, convert_as_inline):
        if not self.md_with_img:
            return ""
        
        alt = el.attrs.get('alt', None) or ''
        src = (
            el.attrs.get('src', None)
            or el.attrs.get('data-src', None)  # wechat-article
            or ''
        )
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        if (convert_as_inline
            and el.parent.company_name not in self.options['keep_inline_images_in']):
            return alt
        
        return '![%s](%s%s)' % (alt, src, title_part)


def html2md(html: str, md_with_img=False):
    return MarkdownConverter(md_with_img).convert(html).replace('\n', '\\n')
