"""Tests for scripts/traduku2sqlite.py."""

import importlib.util
import sqlite3
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "traduku2sqlite.py"
spec = importlib.util.spec_from_file_location("traduku2sqlite", SCRIPT)
t2s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t2s)

DUMP = r"""-- MySQL dump
INSERT INTO `language` VALUES (1,'English'),(2,'Japanese');
INSERT INTO `users` VALUES ('alice',1,'secret'),('bob',0,'hunter2');
INSERT INTO `log` VALUES (1300000000,'alice','192.0.2.1');
INSERT INTO `phrase` VALUES (1,7,1,1,'It &apos;s fine .'),(2,7,2,1,'No .');
INSERT INTO `word` VALUES (1,1,1,'it'),(3,1,1,'fine'),(3,1,2,'良い'),(3,1,2,'元気');
INSERT INTO `manual` VALUES (1,'okay',2,'大丈夫');
INSERT INTO `chosen` VALUES (1,'bob',2,3,'元気'),(2,'alice',2,1,'いいえ');
INSERT INTO `translation` VALUES (1,'bob',2,'元気だ。','it\'s\nok',1300000500,0,'',0,0,1,1,0),(2,'alice',2,'いいえ。','',1300000100,0,'',0,0,0,0,0);
"""


def test_tuples_unescapes_and_handles_null() -> None:
    # Arrange
    values = r"(1,'it\'s',NULL),(2,'a\nb',3)"

    # Act
    rows = list(t2s.tuples(values))

    # Assert
    assert rows == [["1", "it's", None], ["2", "a\nb", "3"]]


def test_tuples_keeps_empty_strings_and_parentheses_in_text() -> None:
    rows = list(t2s.tuples("(1,'',''),(2,'(x)','y,z')"))
    assert rows == [["1", "", ""], ["2", "(x)", "y,z"]]


def test_read_dump_skips_personal_tables_and_types_ints(tmp_path: Path) -> None:
    dump = tmp_path / "dump.sql"
    dump.write_text(DUMP, encoding="utf-8")

    tables = t2s.read_dump(dump)

    assert "users" not in tables and "log" not in tables
    assert tables["phrase"][0] == [1, 7, 1, 1, "It &apos;s fine ."]
    assert tables["translation"][0][4] == "it's\nok"


def test_read_dump_rejects_wrong_column_count(tmp_path: Path) -> None:
    dump = tmp_path / "dump.sql"
    dump.write_text("INSERT INTO `language` VALUES (1,'English',3);\n")

    with pytest.raises(ValueError):
        t2s.read_dump(dump)


def test_pseudonyms_ordered_by_first_translation() -> None:
    tables = {
        "translation": [[1, "bob", 2, "", "", 500], [2, "alice", 2, "", "", 100]],
        "chosen": [[1, "carol", 2, 1, "x"]],
    }

    names = t2s.pseudonyms(tables)

    assert names == {"alice": "t01", "bob": "t02", "carol": "t03"}


def test_main_writes_sanitised_db(tmp_path: Path) -> None:
    dump = tmp_path / "dump.sql"
    dump.write_text(DUMP, encoding="utf-8")
    filemap = tmp_path / "files.tsv"
    filemap.write_text("7\tbr-a01\n")
    out = tmp_path / "out.sqlite"

    t2s.main(dump, filemap, out)

    db = sqlite3.connect(out)
    tables = {
        r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert tables == {
        "language",
        "file",
        "phrase",
        "word",
        "chosen",
        "manual",
        "translation",
    }
    assert db.execute(
        "SELECT translator FROM translation ORDER BY phrase_id"
    ).fetchall() == [
        ("t02",),
        ("t01",),
    ]
    dumped = "\n".join(db.iterdump())
    for secret in ("alice", "bob", "secret", "hunter2", "192.0.2.1"):
        assert secret not in dumped


def test_write_db_enforces_foreign_keys(tmp_path: Path) -> None:
    tables = {t: [] for t in t2s.NCOLS}
    tables["phrase"] = [[1, 99, 1, 1, "x"]]

    with pytest.raises(sqlite3.IntegrityError):
        t2s.write_db(tmp_path / "out.sqlite", tables, [(7, "br-a01")])
