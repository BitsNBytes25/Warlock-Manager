import logging
import re


class SensitiveDataFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.mask = '********'
        # Default matches
        self.matches = []
        self.add_match(r'(password .* to )([^\s]+)')
        self.add_match(r'(password to )([^\s]+)')
        self.add_match(r'(password=)([^\s]+)')

    def _make_repl(self, mask_group):
        def repl(m):
            parts = list(m.groups())
            if len(parts) >= mask_group:
                parts[mask_group - 1] = self.mask
            return ''.join(parts)
        return repl

    def add_match(self, pattern, group_to_mask=2):
        compiled = re.compile(pattern, flags=re.IGNORECASE)
        repl = self._make_repl(group_to_mask)
        self.matches.append((compiled, repl))

    def filter(self, record):
        msg = record.getMessage()
        for compiled, repl in self.matches:
            msg = compiled.sub(repl, msg)
        record.msg = msg
        return True


# Module-level filter instance
sensitive_data_filter = SensitiveDataFilter()
