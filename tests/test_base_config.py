
import unittest
from warlock_manager.config.base_config import BaseConfig


first_test = '''
[SomeSection]
Key1=Value1
Key2=42
Key3=True
'''


class TestConfig(BaseConfig):
    pass


class TestUnrealConfig(unittest.TestCase):

    def test_type_conversions(self):
        # Ensure BaseConfig conversion helpers behave as expected
        c = TestConfig('test')
        c.add_option({
            'name': 'TestBool',
            'key': 'test-bool',
            'type': 'bool',
        })
        c.add_option({
            'name': 'TestInt',
            'key': 'test-int',
            'type': 'int',
        })

        self.assertEqual('True', c.from_system_type('TestBool', True))
        self.assertEqual('False', c.from_system_type('TestBool', False))
        self.assertEqual('5', c.from_system_type('TestInt', 5))


if __name__ == '__main__':
    unittest.main()
