"""Tests for IniConfig and PropertiesConfig."""

import pytest

from warlock_manager import IniConfig, PropertiesConfig


class TestIniConfig:
    def test_get_existing_value(self, tmp_path):
        cfg_file = tmp_path / "server.ini"
        cfg_file.write_text("[server]\nport=27015\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        assert cfg.get("server", "port") == "27015"

    def test_get_fallback(self, tmp_path):
        cfg_file = tmp_path / "server.ini"
        cfg_file.write_text("[server]\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        assert cfg.get("server", "missing", fallback="default") == "default"

    def test_set_creates_section_and_key(self, tmp_path):
        cfg = IniConfig(tmp_path / "new.ini")
        cfg.set("game", "maxplayers", "64")
        assert cfg.get("game", "maxplayers") == "64"

    def test_save_and_reload(self, tmp_path):
        cfg_file = tmp_path / "server.ini"
        cfg = IniConfig(cfg_file)
        cfg.set("network", "ip", "0.0.0.0")
        cfg.save()
        reloaded = IniConfig(cfg_file)
        assert reloaded.get("network", "ip") == "0.0.0.0"

    def test_sections(self, tmp_path):
        cfg_file = tmp_path / "s.ini"
        cfg_file.write_text("[a]\n[b]\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        assert "a" in cfg.sections()
        assert "b" in cfg.sections()

    def test_has_section(self, tmp_path):
        cfg_file = tmp_path / "s.ini"
        cfg_file.write_text("[existing]\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        assert cfg.has_section("existing")
        assert not cfg.has_section("missing")

    def test_items(self, tmp_path):
        cfg_file = tmp_path / "s.ini"
        cfg_file.write_text("[sec]\nk=v\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        assert ("k", "v") in cfg.items("sec")

    def test_options(self, tmp_path):
        cfg_file = tmp_path / "s.ini"
        cfg_file.write_text("[sec]\nalpha=1\nbeta=2\n", encoding="utf-8")
        cfg = IniConfig(cfg_file)
        opts = cfg.options("sec")
        assert "alpha" in opts
        assert "beta" in opts

    def test_nonexistent_file_creates_empty_config(self, tmp_path):
        cfg = IniConfig(tmp_path / "ghost.ini")
        assert cfg.sections() == []

    def test_repr(self, tmp_path):
        cfg = IniConfig(tmp_path / "x.ini")
        assert "x.ini" in repr(cfg)

    def test_save_creates_parent_dirs(self, tmp_path):
        cfg = IniConfig(tmp_path / "a" / "b" / "c.ini")
        cfg.set("s", "k", "v")
        cfg.save()
        assert (tmp_path / "a" / "b" / "c.ini").exists()


class TestPropertiesConfig:
    def test_get_existing_value(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("max-players=20\n", encoding="utf-8")
        cfg = PropertiesConfig(f)
        assert cfg.get("max-players") == "20"

    def test_get_fallback(self, tmp_path):
        cfg = PropertiesConfig(tmp_path / "empty.properties")
        assert cfg.get("missing", fallback="default") == "default"

    def test_set_and_get(self, tmp_path):
        cfg = PropertiesConfig(tmp_path / "new.properties")
        cfg.set("difficulty", "hard")
        assert cfg.get("difficulty") == "hard"

    def test_save_and_reload(self, tmp_path):
        f = tmp_path / "server.properties"
        cfg = PropertiesConfig(f)
        cfg.set("level-name", "world")
        cfg.save()
        reloaded = PropertiesConfig(f)
        assert reloaded.get("level-name") == "world"

    def test_comments_ignored(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("# This is a comment\n! Also a comment\nkey=value\n", encoding="utf-8")
        cfg = PropertiesConfig(f)
        assert cfg.get("key") == "value"
        assert "# This is a comment" not in cfg.keys()

    def test_colon_separator(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("host: localhost\n", encoding="utf-8")
        cfg = PropertiesConfig(f)
        assert cfg.get("host") == "localhost"

    def test_keys(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("a=1\nb=2\n", encoding="utf-8")
        cfg = PropertiesConfig(f)
        assert set(cfg.keys()) == {"a", "b"}

    def test_items(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("x=10\n", encoding="utf-8")
        cfg = PropertiesConfig(f)
        assert ("x", "10") in cfg.items()

    def test_nonexistent_file_creates_empty_config(self, tmp_path):
        cfg = PropertiesConfig(tmp_path / "ghost.properties")
        assert cfg.keys() == []

    def test_repr(self, tmp_path):
        cfg = PropertiesConfig(tmp_path / "server.properties")
        assert "server.properties" in repr(cfg)

    def test_save_creates_parent_dirs(self, tmp_path):
        cfg = PropertiesConfig(tmp_path / "a" / "b" / "c.properties")
        cfg.set("k", "v")
        cfg.save()
        assert (tmp_path / "a" / "b" / "c.properties").exists()
