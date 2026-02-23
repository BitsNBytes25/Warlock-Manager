import os
import unittest

from warlock_manager.config.unreal_config import UnrealConfig

here = os.path.dirname(os.path.realpath(__file__))


class TestUnrealConfigArkSpawnEntities(unittest.TestCase):
    def test_ark_spawn_entities_config(self):
        cfg = UnrealConfig('test', os.path.join(here, 'data', 'unreal_ark_npc_spawn_entities.ini'))
        cfg.load()

        # This data is never registered as options, so we just check the raw data
        self.assertEqual('section', cfg._data[0][0]['type'])
        self.assertEqual('/script/shootergame.shootergamemode', cfg._data[0][0]['value'])

        self.assertEqual('ConfigAddNPCSpawnEntriesContainer', cfg._data[0][1]['key'])
        self.assertEqual('keystruct', cfg._data[0][1]['type'])
        self.assertIsInstance(cfg._data[0][1]['value'], dict)

        val1 = cfg._data[0][1]['value']
        self.assertEqual('Zaldrir Juvenile', val1['NPCSpawnEntries'][0]['AnEntryName'])
        self.assertEqual({'X': '0', 'Y': '0', 'Z': '35'}, val1['NPCSpawnEntries'][0]['GroupSpawnOffset'])

        # Ensure the generated data matches expectations
        with open(cfg.path, 'r') as f:
            expected = f.read()
        self.assertEqual(expected, cfg.fetch())


if __name__ == '__main__':
    unittest.main()
