# Japanese SemCor (JSemCor)

A sense-tagged corpus of Japanese, created by translating the English
[SemCor](https://www.cse.unt.edu/~rada/downloads.html#semcor) corpus and
projecting the sense tags from English onto the Japanese translation.

The corpus consists of 14,169 sentences with 150,555 content words, of
which 58,265 are sense-tagged with synsets from the
[Japanese Wordnet](https://bond-lab.github.io/wnja/) (version 1.1).

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

## Data

`data/` contains one file per Brown Corpus text (116 texts, the subset of
SemCor translated in [MultiSemCor](https://doi.org/10.1017/S1351324905003839)),
named after the corresponding SemCor file (e.g. `br-a01.xml`).

Files are in the Kyoto Annotation Format (KAF), using only the text
(`<wf>`) and term (`<term>`) layers. Tokenisation and part-of-speech tags
come from MeCab (IPAdic). Sense tags are given as `externalRef` elements
with `resource="WordNet jpn 1.1"`:

- `jpn-11-<lemma>-<pos>`: the Japanese Wordnet lemma
- `jpn-11-<offset>-<pos>`: the synset, identified by its Princeton
  WordNet 3.0 offset (nested inside the lemma reference)

Each sentence is bracketed by empty `<wf>` elements (e.g. `w1.1.0` and
`w1.1.9` below). Only open-class words have `<term>` elements.

### Example

The first sentence of `br-k01.xml`, スコッティ は 学校 に 戻ら なかっ た 。
*Scotty ha gakkō ni modora nakat ta .*, the Japanese translation of
*Scotty did not go back to school* (Figure 3 in the paper). The words
学校 *gakkō* “school” and 戻る *modoru* “return” are linked to Japanese
Wordnet lemmas, but not to a specific synset.

```xml
<?xml version="1.0" encoding="utf-8"?>
<KAF lang="jpn">
  <kafHeader>
    <fileDesc filename="br-k01"/>
    <linguisticProcessors layer="text">
      <lp timestamp="2011-12-12T02:17:46" version="0.98" name="MeCab"/>
    </linguisticProcessors>
  </kafHeader>
  <text>
    <wf wid="w1.1.0" sent="1" para="1"/>
    <wf wid="w1.1.1" sent="1" para="1">スコッティ</wf>
    <wf wid="w1.1.2" sent="1" para="1">は</wf>
    <wf wid="w1.1.3" sent="1" para="1">学校</wf>
    <wf wid="w1.1.4" sent="1" para="1">に</wf>
    <wf wid="w1.1.5" sent="1" para="1">戻ら</wf>
    <wf wid="w1.1.6" sent="1" para="1">なかっ</wf>
    <wf wid="w1.1.7" sent="1" para="1">た</wf>
    <wf wid="w1.1.8" sent="1" para="1">。</wf>
    <wf wid="w1.1.9" sent="1" para="1"/>
    ...
  </text>
  <terms>
    <term tid="t1.1.1" lemma="スコッティ" type="open" pos="N.名詞.一般">
      <span>
        <target id="w1.1.1"/>
      </span>
      <component lemma="スコッティ" id="c1.1.1" pos="N.名詞.一般"/>
    </term>
    <term tid="t1.1.3" lemma="学校" type="open" pos="N.n">
      <span>
        <target id="w1.1.3"/>
      </span>
      <component lemma="学校" id="c1.1.3" pos="N.名詞.一般"/>
      <externalReferences>
        <externalRef resource="WordNet jpn 1.1" reference="jpn-11-学校-n"/>
      </externalReferences>
    </term>
    <term tid="t1.1.5" lemma="戻る" type="open" pos="V.v">
      <span>
        <target id="w1.1.5"/>
      </span>
      <component lemma="戻る" id="c1.1.5" pos="V.動詞.自立"/>
      <externalReferences>
        <externalRef resource="WordNet jpn 1.1" reference="jpn-11-戻る-v"/>
      </externalReferences>
    </term>
    ...
  </terms>
</KAF>
```

Where the synset is known, the lemma reference contains a nested
synset reference, for example (from `br-a01.xml`):

```xml
<externalRef resource="WordNet jpn 1.1" reference="jpn-11-もめ事-n">
  <externalRef resource="WordNet jpn 1.1" reference="jpn-11-07372565-n"/>
</externalRef>
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
