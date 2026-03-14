import logging
import unittest

from warlock_manager.libs.sensitive_data_filter import SensitiveDataFilter


class TestSensitiveDataFilter(unittest.TestCase):
    def setUp(self):
        """Set up a test logger with the sensitive data filter."""
        self.filter = SensitiveDataFilter()
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)

        # Create a handler to capture log records
        self.handler = logging.StreamHandler()
        self.handler.addFilter(self.filter)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        """Clean up the logger."""
        self.logger.handlers.clear()

    def test_default_mask_value(self):
        """Test that the default mask is set correctly."""
        self.assertEqual(self.filter.mask, '********')

    def test_password_masking(self):
        """Test that password patterns are masked correctly."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='password set to MySecurePassword123!',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertIn('password', record.msg.lower())
        self.assertNotIn('MySecurePassword123!', record.msg)
        self.assertIn('********', record.msg)

    def test_password_masking_case_insensitive(self):
        """Test that password masking is case-insensitive."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='PASSWORD set to secret123',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertNotIn('secret123', record.msg)
        self.assertIn('********', record.msg)

    def test_no_sensitive_data(self):
        """Test that messages without sensitive patterns are unchanged."""
        message = 'This is a normal log message'
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertEqual(record.msg, message)

    def test_add_custom_pattern(self):
        """Test adding a custom sensitive data pattern."""
        custom_pattern = r'(api_key: )(.*)'
        self.filter.add_match(custom_pattern)

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='api_key: sk-1234567890abcdef',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertNotIn('sk-1234567890abcdef', record.msg)
        self.assertIn('api_key: ********', record.msg)

    def test_multiple_patterns_in_message(self):
        """Test masking when multiple sensitive patterns exist in one message."""
        self.filter.add_match(r'(token: )(.*?)(\s|$)')

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='password set to secret123 and token: abc123def456',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertNotIn('secret123', record.msg)
        self.assertNotIn('abc123def456', record.msg)

    def test_filter_returns_true(self):
        """Test that the filter always returns True to allow logging."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)

    def test_password_with_spaces(self):
        """Test masking passwords that contain spaces."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='password changed to My Secret Pass 123',
            args=(),
            exc_info=None
        )

        result = self.filter.filter(record)
        self.assertTrue(result)
        self.assertNotIn('My Secret Pass 123', record.msg)


if __name__ == '__main__':
    unittest.main()
