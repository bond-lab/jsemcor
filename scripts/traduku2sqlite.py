"""Convert the traduku MySQL dump into a sanitised SQLite database.

traduku was the web interface used to translate SemCor into Japanese.
The raw dump contains personal data, so this script:

- drops the ``users`` (passwords) and ``log`` (IP addresses) tables
- drops the empty ``class`` table
- replaces translator user names with stable pseudonyms (t01, t02, ...),
  numbered in order of each translator's first saved translation

It also adds a ``file`` table mapping traduku's ``file_id`` to the Brown
Corpus file name used in SemCor and in ``data/``.

Usage:
    python scripts/traduku2sqlite.py DUMP.sql FILEMAP.tsv OUT.sqlite
"""

import logging
import re
import sqlite3
import sys
from collections.abc import Iterator
from pathlib import Path

SCHEMA = """
-- Languages used in the interface: 1 = English, 2 = Japanese.
CREATE TABLE language (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL  -- Language name in English
) STRICT;

-- Brown Corpus text translated (one per data/br-*.xml file); added on export.
CREATE TABLE file (
    file_id INTEGER PRIMARY KEY,   -- traduku's internal file number
    brown   TEXT NOT NULL UNIQUE   -- Brown/SemCor file name, e.g. 'br-a01'
) STRICT;

-- Source sentences: one row per SemCor sentence shown to translators.
CREATE TABLE phrase (
    id          INTEGER PRIMARY KEY,
    file_id     INTEGER REFERENCES file(file_id),  -- Text the sentence is from
    sentence_id INTEGER,  -- SemCor sentence number (snum) within the file
    lang_id     INTEGER NOT NULL REFERENCES language(id),  -- Always 1 (English)
    text        TEXT DEFAULT ''  -- Space-separated SemCor tokens, HTML-escaped (&quot;)
) STRICT;

-- Sense-tagged tokens of each phrase. For lang_id 1 a row is the English
-- lemma; for lang_id 2 each row is one Japanese candidate offered for that English
-- token (members of the Japanese Wordnet synset), so a token can have many.
CREATE TABLE word (
    id        INTEGER NOT NULL,  -- 1-based token index in the phrase, counting punctuation
    phrase_id INTEGER NOT NULL REFERENCES phrase(id),  -- Sentence the token is in
    lang_id   INTEGER NOT NULL REFERENCES language(id),
    text      TEXT NOT NULL DEFAULT '',  -- English lemma or Japanese candidate
    PRIMARY KEY (id, lang_id, phrase_id, text)
) STRICT;

-- Japanese words a translator chose (clicked) or typed for an English token.
-- text need not be one of the offered candidates in word.
CREATE TABLE chosen (
    phrase_id  INTEGER NOT NULL REFERENCES phrase(id),
    translator TEXT NOT NULL,  -- Pseudonym, e.g. 't01' (replaces the user name)
    lang_id    INTEGER NOT NULL REFERENCES language(id),  -- Always 2 (Japanese)
    word_id    INTEGER NOT NULL,  -- word.id of the English token (same phrase)
    text       TEXT,  -- Word chosen or typed (usually Japanese)
    PRIMARY KEY (phrase_id, translator, lang_id, word_id)
) STRICT;

-- Word pairs added by hand to the candidate lists.
CREATE TABLE manual (
    from_lang_id INTEGER NOT NULL REFERENCES language(id),
    from_word    TEXT NOT NULL DEFAULT '',  -- Source word
    to_lang_id   INTEGER NOT NULL REFERENCES language(id),
    to_word      TEXT NOT NULL DEFAULT '',  -- Translation offered as a candidate
    PRIMARY KEY (from_lang_id, from_word, to_lang_id, to_word)
) STRICT;

-- The Japanese translation of each sentence (one per phrase).
CREATE TABLE translation (
    phrase_id  INTEGER PRIMARY KEY REFERENCES phrase(id),
    translator TEXT NOT NULL,  -- Pseudonym, e.g. 't01' (replaces the user name)
    lang_id    INTEGER NOT NULL REFERENCES language(id),  -- Always 2 (Japanese)
    text       TEXT DEFAULT '',  -- Japanese translation
    comments   TEXT DEFAULT '',  -- Translator's comments, mostly on the candidates
    updated    INTEGER,  -- Last save, Unix time (seconds)
    committed  INTEGER,  -- Unix time marked final; always 0 in this dump
    notes      TEXT NOT NULL DEFAULT '',  -- Free-text notes (unused in this dump)
    jap1       INTEGER DEFAULT 0,  -- Interface flags 1-5 (0/1); meaning undocumented
    jap2       INTEGER DEFAULT 0,
    jap3       INTEGER DEFAULT 0,
    jap4       INTEGER DEFAULT 0,
    jap5       INTEGER DEFAULT 0
) STRICT;
"""

# Column positions in the dump that hold integers, per table.
INT_COLS = {
    "language": {0},
    "phrase": {0, 1, 2, 3},
    "word": {0, 1, 2},
    "chosen": {0, 2, 3},
    "manual": {0, 2},
    "translation": {0, 2, 5, 6, 8, 9, 10, 11, 12},
}
NCOLS = {
    "language": 2,
    "phrase": 5,
    "word": 4,
    "chosen": 5,
    "manual": 4,
    "translation": 13,
}
USER_COL = {"chosen": 1, "translation": 1}
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0"}

logger = logging.getLogger(__name__)


def tuples(values: str) -> Iterator[list[str | None]]:
    """Yield rows from a MySQL ``VALUES (...),(...)`` string.

    Args:
        values: The text after ``VALUES`` in an extended INSERT statement

    Returns:
        An iterator over rows, each a list of field strings; quoted strings
        are unescaped and an unquoted NULL becomes None

    """
    row: list[str | None] | None = None
    field: list[str] = []
    inq = raw = False
    i, n = 0, len(values)
    while i < n:
        c = values[i]
        if inq:
            if c == "\\":
                nxt = values[i + 1]
                field.append(ESCAPES.get(nxt, nxt))
                i += 2
                continue
            if c == "'":
                inq, raw = False, True
            else:
                field.append(c)
        elif c == "'":
            inq, raw = True, False
        elif c == "(":
            row, field, raw = [], [], True
        elif c in ",)":
            if row is not None and (field or raw or c == ","):
                s = "".join(field)
                row.append(None if s == "NULL" else s)
                field = []
            if c == ")" and row is not None:
                yield row
                row = None
        elif c not in " \n" and row is not None:
            field.append(c)
        i += 1


def read_dump(path: Path) -> dict[str, list[list]]:
    """Read the tables in NCOLS from a MySQL dump, with integer columns typed.

    Args:
        path: The uncompressed MySQL dump

    Returns:
        A dict from table name to its rows; tables not in NCOLS are skipped

    Raises:
        ValueError: If a row has the wrong number of columns
    """
    tables: dict[str, list[list]] = {t: [] for t in NCOLS}
    with path.open(encoding="utf-8") as f:
        for line in f:
            m = re.match(r"INSERT INTO `(\w+)` VALUES (.*);\s*$", line)
            if not m or m.group(1) not in NCOLS:
                continue
            table = m.group(1)
            for row in tuples(m.group(2)):
                if len(row) != NCOLS[table]:
                    raise ValueError(f"{table}: expected {NCOLS[table]} columns: {row}")
                tables[table].append(
                    [
                        int(v) if j in INT_COLS[table] and v is not None else v
                        for j, v in enumerate(row)
                    ]
                )
    return tables


def pseudonyms(tables: dict[str, list[list]]) -> dict[str, str]:
    """Map each user name to t01, t02, ... by time of first saved translation.

    Args:
        tables: Rows by table, as returned by read_dump

    Returns:
        A dict from user name to pseudonym; users with no saved translation
        come last, in name order
    """
    first: dict[str, float] = {}
    for row in tables["translation"]:
        user, updated = row[1], row[5]
        first[user] = min(first.get(user, float("inf")), updated or float("inf"))
    for row in tables["chosen"]:
        first.setdefault(row[1], float("inf"))
    order = sorted(first, key=lambda u: (first[u], u))
    return {u: f"t{i:02d}" for i, u in enumerate(order, 1)}


def read_filemap(path: Path) -> list[tuple[int, str]]:
    """Read the tab-separated file_id to Brown file name mapping.

    Args:
        path: TSV file with rows ``file_id<TAB>brown``

    Returns:
        A list of (file_id, brown) pairs
    """
    rows = [line.split("\t") for line in path.read_text().splitlines() if line]
    return [(int(fid), brown) for fid, brown in rows]


def write_db(
    out: Path, tables: dict[str, list[list]], files: list[tuple[int, str]]
) -> None:
    """Create ``out`` from SCHEMA and insert the rows, checking foreign keys.

    Args:
        out: Path of the SQLite database to create (replaced if it exists)
        tables: Rows by table, with user names already pseudonymised
        files: (file_id, brown) pairs for the file table

    Raises:
        sqlite3.IntegrityError: If any row violates a foreign key
    """
    out.unlink(missing_ok=True)
    db = sqlite3.connect(out)
    db.execute("PRAGMA foreign_keys = ON")
    with db:
        db.executescript(SCHEMA)
        db.executemany("INSERT INTO file VALUES (?, ?)", files)
        for table, rows in tables.items():
            marks = ", ".join("?" * NCOLS[table])
            db.executemany(f"INSERT INTO {table} VALUES ({marks})", rows)
    for table in ["file", *NCOLS]:
        count = db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        logger.info("%s: %d rows", table, count)
    db.execute("VACUUM")
    db.close()


def main(dump: Path, filemap: Path, out: Path) -> None:
    """Convert the traduku dump into a sanitised SQLite database.

    Args:
        dump: The uncompressed MySQL dump
        filemap: TSV mapping traduku file_id to Brown file name
        out: Path of the SQLite database to create
    """
    tables = read_dump(dump)
    names = pseudonyms(tables)
    for table, col in USER_COL.items():
        for row in tables[table]:
            row[col] = names[row[col]]
    write_db(out, tables, read_filemap(filemap))
    logger.info("translators: %d", len(names))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(sys.argv) != 4:
        logger.error("usage: %s DUMP.sql FILEMAP.tsv OUT.sqlite", sys.argv[0])
        sys.exit(1)
    main(*(Path(a) for a in sys.argv[1:4]))
