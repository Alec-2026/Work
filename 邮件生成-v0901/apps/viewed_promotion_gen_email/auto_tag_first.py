import html
import os
import re
from urllib.parse import urlsplit, urlunsplit

import pandas as pd

from apps.uploaded_artwork_gen_email.auto_tag_first import AutoTag as _BaseAutoTag


class AutoTag(_BaseAutoTag):
    """Reuse the existing text-generation/JSON pipeline for promotion emails."""

    def __init__(self):
        super().__init__()
        self.prompt_name = '独立站-邮件生成-viewed-promotion话术.md'
        self.prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt')
        self.prompt_fp = os.path.join(self.prompt_dir, self.prompt_name)
        self.business_name = self.prompt_name.split('.')[0]

    @staticmethod
    def _value_or_default(value, default=''):
        if value is None or value == '' or pd.isna(value):
            return default
        return str(value).strip()

    @staticmethod
    def _clean_promotion_url(value):
        value = AutoTag._value_or_default(value)
        if not value:
            return ''
        parsed = urlsplit(value)
        if not parsed.scheme or not parsed.netloc:
            return value.split('?', 1)[0]
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))

    def fill_prompt(self, row):
        params = dict(row)
        params['first_name'] = self._value_or_default(params.get('first_name'), 'unknow').title()
        params['sender_name'] = self._value_or_default(params.get('sender_name'))
        params['last_viewed_promotion_page_slug'] = self._value_or_default(
            params.get('last_viewed_promotion_page_slug'), 'general promotion'
        )
        params['loyalty_tier'] = self._value_or_default(params.get('loyalty_tier'))
        params['promotion_url'] = self._clean_promotion_url(params.get('promotion_url'))
        self._current_promotion_url = params['promotion_url']

        prompt = self.llm.get_prompt(self.prompt_fp).compile(**params)
        # The source SOP intentionally uses single-brace placeholders in examples;
        # resolve only the runtime URL after loading it so no query parameters leak.
        return prompt.replace('{promotion_url}', params['promotion_url'])

    @staticmethod
    def _render_promotion_link(email_body, promotion_url):
        """Replace the model's link marker with the only trusted HTML link."""
        marker_pattern = r'\[\[PROMOTION_LINK\|([^\[\]]+?)\]\]'
        markers = re.findall(marker_pattern, email_body)

        if not promotion_url:
            if markers:
                raise ValueError('Promotion URL 为空时不得生成 Promotion 链接')
            return email_body

        if len(markers) != 1:
            raise ValueError('Promotion 邮件必须包含且只能包含一个 Promotion 链接标记')

        link_text = html.escape(markers[0].strip())
        safe_url = html.escape(promotion_url, quote=True)
        rendered_link = f'<a href="{safe_url}">{link_text}</a>'
        rendered_body = re.sub(marker_pattern, rendered_link, email_body, count=1)

        if '[[PROMOTION_LINK|' in rendered_body:
            raise ValueError('Promotion 链接标记未完全替换')
        if re.search(r'https?://', re.sub(r'<a\s+href="[^"]+">', '', rendered_body)):
            raise ValueError('Promotion 邮件正文中不得直接显示 URL')
        if re.search(r'\[[^\]]+\]\(https?://', rendered_body):
            raise ValueError('Promotion 邮件正文中不得使用 Markdown 链接')

        return rendered_body

    def fix_response(self, response):
        response = super().fix_response(response)
        response['email_body'] = self._render_promotion_link(
            response['email_body'],
            self._current_promotion_url,
        )
        return response
