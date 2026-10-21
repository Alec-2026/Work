import os

from apps.uploaded_artwork_gen_email.check_email import AutoTag as _BaseCheckEmail


class AutoTag(_BaseCheckEmail):
    """Reuse the shared QC implementation with promotion-specific rules."""

    def __init__(self):
        super().__init__()
        self.prompt_name = '独立站-邮件审核.md'
        self.prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt')
        self.prompt_fp = os.path.join(self.prompt_dir, self.prompt_name)
        self.business_name = self.prompt_name.split('.')[0]
