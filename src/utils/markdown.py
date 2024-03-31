from markdownify import MarkdownConverter as RawMarkdownConverter


class MarkdownConverter(RawMarkdownConverter):
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """
    
    def convert_img(self, el, text, convert_as_inline):
        alt = el.attrs.get('alt', None) or ''
        src = (
            el.attrs.get('src', None)
            or el.attrs.get('data-src', None)  # wechat-article
            or ''
        )
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        if (convert_as_inline
            and el.parent.name not in self.options['keep_inline_images_in']):
            return alt
        
        return '![%s](%s%s)' % (alt, src, title_part)
