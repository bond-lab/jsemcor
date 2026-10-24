# Japanese SemCor (JSemCor)

A sense-tagged corpus of Japanese, created by translating the English
[SemCor](https://www.cse.unt.edu/~rada/downloads.html#semcor) corpus and
projecting the sense tags from English onto the Japanese translation.

The corpus consists of 116 texts from the Brown Corpus (14,161
sentences, 356,632 tokens). Of its 147,518 content words, 58,239 are
sense-tagged with synsets from the
[Japanese Wordnet](https://bond-lab.github.io/wnja/) (version 1.1), and
54,429 are linked to the English SemCor word they translate.

## Authors

- Francis Bond
- Timothy Baldwin
- Richard Fothergill
- Kiyotaka Uchimoto

## Citation

If you use this corpus, please cite:

> Francis Bond, Timothy Baldwin, Richard Fothergill, and Kiyotaka
> Uchimoto (2012). Japanese SemCor: A Sense-tagged Corpus of Japanese.
> In *Proceedings of the 6th Global WordNet Conference (GWC 2012)*,
> Matsue, pp. 56–63.
> [PDF](https://bond-lab.github.io/static/pdf/2012-gwc-jsemcor.pdf)

```bibtex
@inproceedings{bond-etal-2012-jsemcor,
  author    = {Francis Bond and Timothy Baldwin and Richard Fothergill and Kiyotaka Uchimoto},
  title     = {Japanese {SemCor}: A Sense-tagged Corpus of {Japanese}},
  booktitle = {Proceedings of the 6th Global WordNet Conference (GWC 2012)},
  address   = {Matsue},
  pages     = {56--63},
  year      = {2012},
  url       = {https://bond-lab.github.io/static/pdf/2012-gwc-jsemcor.pdf}
}
```

## Versions

| Version | Date | Contents |
|---|---|---|
| [1.0](https://github.com/bond-lab/jsemcor/tree/v1.0) | 2011-12-12 | Release described in the paper: open-class terms and Japanese Wordnet sense tags. |
| 1.1 (current) | 2012-03-05 | Adds closed-class terms, links to the English SemCor tokens, and sense-tag confidence. Revised translations for `br-f24`. |

Version 1.1 was produced by Richard Fothergill (University of Melbourne)
in March 2012 and added to this repository in October 2026. He
refactored the pipeline to produce the English alignment, so we compared
it with 1.0:

- **Tokenisation is unchanged.** In 115 of the 116 files every token has
  the same ID and text as in 1.0. The only other text-layer difference is
  the `sent` attribute of some empty boundary tokens.
- **`br-f24` has revised translations** for 10 of its 115 sentences. The
  translation database records these revisions on 2012-02-14, after the
  1.0 release.
- **Sense tags are almost unchanged.** 58,214 open-class terms have the
  same synset tags in both versions. 25 tags were dropped, 5 added and 1
  changed; the 44 terms of 1.0 missing from 1.1 are almost all in the
  revised `br-f24` sentences.
- **The English links are correct.** For example, `s72.90.7` in
  `br-a01.xml` is *trouble* in SemCor 3.0, aligned with もめ事 *momegoto*
  with synset `07372565-n`. Every English reference points to a SemCor
  token, and of the 47,643 terms that are both linked and sense-tagged,
  46,090 (96.7%) share a synset with their English word.

## Data

`data/` contains one file per Brown Corpus text: the subset of SemCor
translated in [MultiSemCor](https://doi.org/10.1017/S1351324905003839).
Files are named after the corresponding SemCor file (e.g. `br-a01.xml`).

Files are in the Kyoto Annotation Format (KAF), using only the text
(`<wf>`) and term (`<term>`) layers.

### Text layer

Word IDs have the form `w<para>.<sent>.<n>`, where `<para>` and `<sent>`
are the SemCor paragraph and sentence numbers (`pnum` and `snum`) and
`<n>` counts tokens from 1. Each sentence is bracketed by empty `<wf>`
elements, at position 0 and after the last token.

Translators could split an English sentence into several Japanese
sentences. The `sent` attribute then has a decimal part (`14.0`, `14.1`,
...), while the word IDs keep the English numbering (`w13.14.<n>`, with
`<n>` continuing across the parts).

### Term layer

Each token, or multi-token word, has a `<term>`. The term ID matches the
word ID; multi-token terms list the token numbers (`t72.90.2,3` spans
`w72.90.2` and `w72.90.3`) and have one `<component>` per token.

- `type` is `open` for content words and `close` for function words.
- `pos` is a KAF category plus WordNet part of speech (`N.n`, `V.v`,
  `G.a`, `A.r`) for words found in the Japanese Wordnet, and otherwise
  the MeCab IPAdic tag. `<component pos>` is always the IPAdic tag.

Content words have `externalRef` elements:

| `resource` | `reference` | Meaning |
|---|---|---|
| `WordNet jpn 1.1` | `jpn-11-<lemma>-<pos>` | Japanese Wordnet lemma |
| `WordNet jpn 1.1` | `jpn-11-<offset>-<pos>` | Synset (Princeton WordNet 3.0 offset), nested inside the lemma reference, with a `confidence` (always `1.0`) |
| `Semcor eng 3.0` | `s<para>.<sent>.<n>` | English SemCor 3.0 token this word translates |

In the English reference, `<n>` is the 1-based position of the token in
the SemCor 3.0 sentence (`<s snum=...>`), **counting both `<wf>` and
`<punc>` elements**. Ignoring punctuation gives the wrong token. A term can
link to more than one English token (3,255 terms do).

### Example

Sentence 90 of `br-a01.xml`, 「少しももめ事はなかった。」, translates
SemCor's *"There wasn't a bit of trouble."*. In SemCor 3.0 the sentence
has 9 tokens: 1 `` `` ``, 2 *There*, 3 *was*, 4 *n't*, 5 *a_bit*,
6 *of*, 7 *trouble*, 8 `''`, 9 *.*.

```xml
<text>
  <wf wid="w72.90.0" sent="90" para="72"/>
  <wf wid="w72.90.1" sent="90" para="72">「</wf>
  <wf wid="w72.90.2" sent="90" para="72">少し</wf>
  <wf wid="w72.90.3" sent="90" para="72">も</wf>
  <wf wid="w72.90.4" sent="90" para="72">もめ事</wf>
  <wf wid="w72.90.5" sent="90" para="72">は</wf>
  <wf wid="w72.90.6" sent="90" para="72">なかっ</wf>
  <wf wid="w72.90.7" sent="90" para="72">た</wf>
  <wf wid="w72.90.8" sent="90" para="72">。</wf>
  <wf wid="w72.90.9" sent="90" para="72">」</wf>
  <wf wid="w72.90.10" sent="90" para="72"/>
  ...
</text>
<terms>
  ...
  <term tid="t72.90.2,3" lemma="少しも" type="open" pos="A.r">
    <span>
      <target id="w72.90.2"/>
      <target id="w72.90.3"/>
    </span>
    <component lemma="少し" id="c72.90.2" pos="副詞.助詞類接続"/>
    <component lemma="も" id="c72.90.3" pos="助詞.係助詞"/>
    <externalReferences>
      <externalRef resource="WordNet jpn 1.1" reference="jpn-11-少しも-r"/>
    </externalReferences>
  </term>
  <term tid="t72.90.4" lemma="もめ事" type="open" pos="N.n">
    <span>
      <target id="w72.90.4"/>
    </span>
    <component lemma="もめ事" id="c72.90.4" pos="名詞.一般"/>
    <externalReferences>
      <externalRef resource="WordNet jpn 1.1" reference="jpn-11-もめ事-n">
        <externalRef confidence="1.0" resource="WordNet jpn 1.1" reference="jpn-11-07372565-n"/>
      </externalRef>
      <externalRef resource="Semcor eng 3.0" reference="s72.90.7"/>
    </externalReferences>
  </term>
  <term tid="t72.90.5" lemma="は" type="close" pos="助詞.係助詞">
    <span>
      <target id="w72.90.5"/>
    </span>
    <component lemma="は" id="c72.90.5" pos="助詞.係助詞"/>
  </term>
  ...
</terms>
```

もめ事 *momegoto* is sense-tagged and linked to token 7, *trouble*.
少しも *sukoshi mo* "(not) a bit" is linked to a Japanese Wordnet lemma
but not to a synset.

### Known issues

- `br-d02.xml` is empty: its 61 sentences contain only the boundary
  tokens, so only 115 texts have Japanese text.
- 444 tokens consist only of whitespace (a newline or an ideographic
  space, U+3000), left by the tokeniser.

## Translation database

`traduku/traduku.sqlite.xz` is the database of the web interface the
translators used (*traduku*), exported on 2014-01-16. It records, for each
English sentence, the Japanese candidates offered for each sense-tagged
word, the words the translators chose or typed, and their translation and
comments. Translations were made between 2008-08 and 2012-02.

The database has been sanitised: user accounts and access logs were
removed, and translator user names were replaced by pseudonyms (`t01` to
`t14`). It was created from the original dump with
[`scripts/traduku2sqlite.py`](scripts/traduku2sqlite.py); the SQL schema
there documents every column.

| Table | Rows | Contents |
|---|---|---|
| `file` | 116 | `file_id` to Brown file name (e.g. `br-a01`) |
| `language` | 2 | 1 = English, 2 = Japanese |
| `phrase` | 12,842 | English sentences: `(file_id, sentence_id)` is the SemCor file and `snum` |
| `word` | 1,514,223 | Per sense-tagged token (`id` is its 1-based position, counting punctuation): the English lemma (`lang_id` 1) and the Japanese candidates offered (`lang_id` 2) |
| `chosen` | 65,238 | The word each translator chose or typed for a token; 2,803 are not among the offered candidates |
| `translation` | 12,834 | Japanese translation of each sentence, with comments and timestamps |
| `manual` | 134 | Manually added English–Japanese word pairs |

Token positions in `word` and `chosen` use the same numbering as the
`Semcor eng 3.0` references in `data/`.

```sh
xz -dk traduku/traduku.sqlite.xz
sqlite3 traduku/traduku.sqlite "
  SELECT p.text, t.text
  FROM phrase p JOIN file f USING (file_id) JOIN translation t ON t.phrase_id = p.id
  WHERE f.brown = 'br-a01' AND p.sentence_id = 90"
```

## Related resources

- English SemCor 3.0:
  <https://www.cse.unt.edu/~rada/downloads.html#semcor>
  (also available through [NLTK](https://www.nltk.org/howto/corpus.html))
- MultiSemCor (English–Italian):
  Bentivogli and Pianta (2005), *Natural Language Engineering* 11(3)
- Japanese Wordnet: <https://bond-lab.github.io/wnja/>

## License

JSemCor is released under the same license as the English SemCor, the
Princeton WordNet license. See [LICENSE](LICENSE).
