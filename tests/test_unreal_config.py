import os
import unittest

from warlock_manager.config.unreal_config import UnrealConfig

here = os.path.dirname(os.path.realpath(__file__))


class TestUnrealConfig(unittest.TestCase):
    def test_init(self):
        cfg = UnrealConfig('test', '/tmp/test.ini')
        # Basic expectations
        self.assertIsInstance(cfg.options, dict)
        self.assertEqual(cfg.path, '/tmp/test.ini')

    def test_get_default_missing(self):
        cfg = UnrealConfig('test', '')
        # Requesting a default for a non-existent option should return an empty string
        val = cfg.get_default('this_option_does_not_exist')
        self.assertEqual(val, '')

    def test_simple_data(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_simple.ini'))
        # Configs are grouped by named parameters, so let's add some options
        cfg.add_option({
            'name': 'Key1',
            'section': 'SomeSection',
            'key': 'Key1',
        })
        cfg.add_option({
            'name': 'Key2',
            'section': 'SomeSection',
            'key': 'Key2',
            'type': 'int'
        })
        cfg.add_option({
            'name': 'Key3',
            'section': 'SomeSection',
            'key': 'Key3',
            'type': 'bool'
        })
        cfg.load()

        self.assertEqual(cfg.get_value('Key1'), 'Value1')
        self.assertEqual(cfg.get_value('Key2'), 42)
        self.assertEqual(cfg.get_value('Key3'), True)

        # These values should exist
        self.assertTrue(cfg.has_value('Key1'))
        self.assertTrue(cfg.has_value('Key2'))
        self.assertTrue(cfg.has_value('Key3'))

        # This value should not
        self.assertFalse(cfg.has_value('NonExistentKey'))

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())

        cfg.set_value('Key1', 'NewValue')
        self.assertEqual(cfg.get_value('Key1'), 'NewValue')

        cfg.set_value('Key2', 100)
        self.assertEqual(cfg.get_value('Key2'), 100)

        cfg.set_value('Key3', False)
        self.assertEqual(cfg.get_value('Key3'), False)

        # Ensure the generated data matches expectations
        expected = '''; This is a simple config file for testing purposes.

[SomeSection]
; This key is a string value
Key1=NewValue
; This key is an integer value
Key2=100
; This key is a boolean value
Key3=False
'''
        self.assertEqual(expected, cfg.fetch())

    def test_simple_create(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_simple.ini'))
        # Configs are grouped by named parameters, so let's add some options
        cfg.add_option({
            'name': 'Key1',
            'section': 'SomeSection',
            'key': 'Key1',
        })
        cfg.add_option({
            'name': 'Key2',
            'section': 'SomeSection',
            'key': 'Key2',
            'type': 'int'
        })
        cfg.add_option({
            'name': 'Key3',
            'section': 'SomeSection',
            'key': 'Key3',
            'type': 'bool'
        })
        cfg.set_value('Key1', 'NewValue')
        cfg.set_value('Key2', 100)
        cfg.set_value('Key3', False)

        # Ensure the generated data matches expectations
        expected = '''[SomeSection]
Key1=NewValue
Key2=100
Key3=False
'''
        self.assertEqual(expected, cfg.fetch())

    def test_duplicate_keys(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_duplicate_keys.ini'))
        cfg.add_option({
            'name': 'LastMapPlayed',
            'section': 'Player.Info',
            'key': 'LastMapPlayed',
        })
        cfg.add_option({
            'name': 'PlayedMaps',
            'section': 'Player.Info',
            'key': 'PlayedMaps',
            'type': 'list'
        })
        cfg.load()

        # The last occurrence of the duplicate key should be the one that is loaded
        self.assertEqual(cfg.get_value('LastMapPlayed'), 'BobsMissions_WP')
        self.assertIsInstance(cfg.get_value('PlayedMaps'), list)
        self.assertEqual(len(cfg.get_value('PlayedMaps')), 6)
        self.assertIn('ScorchedEarth_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('TheIsland_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('Ragnarok_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('Valguero_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('Amissa_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('BobsMissions_WP', cfg.get_value('PlayedMaps'))

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())

        # Update the played maps key with a new list.
        new_maps = ['NewMap1_WP', 'NewMap2_WP']
        cfg.set_value('PlayedMaps', new_maps)
        self.assertEqual(len(cfg.get_value('PlayedMaps')), 2)
        self.assertIn('NewMap1_WP', cfg.get_value('PlayedMaps'))
        self.assertIn('NewMap2_WP', cfg.get_value('PlayedMaps'))

        # Ensure the generated data matches expectations
        expected = '''[Player.Info]
LastMapPlayed=BobsMissions_WP
PlayedMaps=NewMap1_WP
PlayedMaps=NewMap2_WP
'''
        self.assertEqual(expected, cfg.fetch())

    def test_array_ops(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_array_ops.ini'))
        cfg.add_option({
            'name': 'NotAnArray',
            'section': 'Operator Test',
            'key': 'NotAnArray',
        })
        cfg.add_option({
            'name': 'SomeValue',
            'section': 'Operator Test',
            'key': 'SomeValue',
            'type': 'list'
        })
        cfg.load()

        self.assertEqual(cfg.get_value('NotAnArray'), 'Hello')
        self.assertEqual(len(cfg.get_value('SomeValue')), 3)
        self.assertEqual(cfg.get_value('SomeValue')[0], '42')
        self.assertEqual(cfg.get_value('SomeValue')[1], '8')
        self.assertEqual(cfg.get_value('SomeValue')[2], '15')

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())

    def test_vein(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_vein.ini'))
        cfg.add_option({
            'name': 'Server Description',
            'section': '/Script/Vein.VeinGameSession',
            'key': 'ServerDescription',
        })
        cfg.add_option({
            'name': 'Server Name',
            'section': '/Script/Vein.VeinGameSession',
            'key': 'ServerName',
        })
        cfg.add_option({
            'name': 'API Port',
            'section': '/Script/Vein.VeinGameSession',
            'key': 'HTTPPort',
            'type': 'int'
        })
        cfg.load()

        self.assertEqual(cfg.get_value('Server Description'), 'BitsNBytes VEIN Desc')
        self.assertEqual(cfg.get_value('Server Name'), 'BitsNBytes VEIN Test!')
        self.assertEqual(cfg.get_value('API Port'), 8080)

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())

    def test_palworld(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_palworld.ini'))
        cfg.add_option({
            'name': 'Difficulty',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/Difficulty',
            'type': 'str'
        })
        cfg.add_option({
            'name': 'Randomizer Seed',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/RandomizerSeed',
            'type': 'str'
        })
        cfg.add_option({
            'name': 'Randomizer Pal Level Random',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/bIsRandomizerPalLevelRandom',
            'type': 'bool'
        })
        cfg.add_option({
            'name': 'Day Time Speed Rate',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/DayTimeSpeedRate',
            'type': 'float'
        })
        cfg.add_option({
            'name': 'Crossplay Platforms',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/CrossplayPlatforms',
            'type': 'list'
        })
        cfg.load()

        self.assertEqual(cfg.get_value('Difficulty'), 'None')
        self.assertEqual(cfg.get_value('Randomizer Seed'), '')
        self.assertEqual(cfg.get_value('Randomizer Pal Level Random'), False)

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())

    def test_palworld_empty(self):
        """
        Test that the Palworld format works even when the ini is empty.

        :return:
        """
        cfg = UnrealConfig('test', '')
        cfg.add_option({
            'name': 'Randomizer Seed',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/RandomizerSeed',
            'type': 'str'
        })
        cfg.add_option({
            'name': 'Randomizer Pal Level Random',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/bIsRandomizerPalLevelRandom',
            'type': 'bool'
        })
        cfg.add_option({
            'name': 'Day Time Speed Rate',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/DayTimeSpeedRate',
            'type': 'float'
        })
        cfg.add_option({
            'name': 'Crossplay Platforms',
            'section': '/Script/Pal.PalGameWorldSettings',
            'key': 'OptionSettings/CrossplayPlatforms',
            'type': 'list'
        })

        cfg.set_value('Randomizer Seed', 'Random Seed')
        cfg.set_value('Randomizer Pal Level Random', True)
        cfg.set_value('Day Time Speed Rate', 1.5)
        cfg.set_value('Crossplay Platforms', ['Steam', 'Epic'])

        expected = '''[/Script/Pal.PalGameWorldSettings]
OptionSettings=(RandomizerSeed="Random Seed",bIsRandomizerPalLevelRandom=True,DayTimeSpeedRate=1.500000,CrossplayPlatforms=(Steam,Epic))
'''  # noqa: E501
        self.assertEqual(expected, cfg.fetch())

    def test_ark(self):
        """
        ARK has some complicated datatypes we need to support.
        :return:
        """
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_ark.ini'))
        cfg.load()

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())


if __name__ == '__main__':
    unittest.main()
