# Greek macron expansion

## Problem

Word lists that mark accent/breathing but not vowel length leave α, ι, υ ambiguous:
short or long, no way to tell from the text alone.
Pedagogical texts, by contrast,
often mark long instances of these three vowels with a macron
layered on top of whatever accent/breathing the vowel already carries.
Example:
a long alpha with smooth breathing appears as ᾱ̓ in a macron-marked text,
but as plain ἀ in a macron-less source.

`reglem`'s `--macrons` flag (`SearchOptions(with_macrons=True)` in the library)
expands each ambiguous vowel in a lemma into `(?:plain|macron)`,
so one search matches both spellings.

## Unicode detail

Precomposed macron-vowel characters exist: ᾱ ῑ ῡ.
Precomposed macron+breathing or macron+accent characters do NOT exist —
those are the macron-vowel codepoint followed by ordinary *combining* marks:

- U+0313 combining comma above (smooth breathing, psili)
- U+0314 combining reversed comma above (rough breathing, dasia)
- U+0301 combining acute accent (oxia)
- U+0300 combining grave accent (varia)

Order: breathing before accent.
Verified against Python `unicodedata`, both directions:

```python
>>> import unicodedata
>>> unicodedata.normalize("NFC", "ᾱ" + "̓" + "́") == "ᾱ" + "̓" + "́"
True  # already canonical, NFC doesn't reorder/recompose further
```

Also verified:
NFC always resolves the alpha/iota/upsilon + acute double-encoding
(polytonic U+1F71 vs. monotonic U+03AC "tonos") down to one codepoint.
Most Greek lemma sources give NFC text already,
so no dual-encoding to handle on the plain side.

## Circumflex excluded on purpose

Circumflex forms (ᾶ, ἆ, ἇ, ι/υ equivalents) are NOT in the macron table.
A circumflex accent can only sit on a long vowel —
already unambiguous, no separate macron form needed.

## Known simplification

The table maps every bare/accented/breathed α, ι, υ,
including ones that are actually the first or second vowel of a diphthong
(αι, αυ, ει, ευ, οι, ου, υι) —
positions where a macron would never really be written.
Effect:
a generated pattern gets a few extra alternation branches that can never match anything real.
Not incorrect, just slightly bigger than the minimum.
Reliable diphthong detection would be much more machinery
than the false-positive cost justifies.

## Table size

27 entries:
9 each for α, ι, υ
(bare, acute, grave, smooth, rough, smooth+acute, rough+acute, smooth+grave, rough+grave).
