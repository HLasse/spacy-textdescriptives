"""Calculation of various readability metrics"""
from spacy.tokens import Doc
from spacy.language import Language


@Language.factory("readability")
def create_readability_component(nlp: Language, name: str):
    return Readability(nlp)


class Readability:
    def __init__(self, nlp: Language):
        """Initialise components"""
        if not Doc.has_extension("readability"):
            Doc.set_extension("readability", getter=self.readability)

    def __call__(self, doc: Doc):
        """Run the pipeline component"""
        return doc

    def readability(self, doc: Doc) -> dict[str, float]:
        """Create output"""
        hard_words = len([syllable for syllable in doc._._n_syllables if syllable >= 3])
        long_words = len([t for t in doc._._filtered_tokens if len(t) > 6])

        return {
            "flesch_reading_ease": self._flesch_reading_ease(doc),
            "flesch_kincaid_grade": self._flesch_kincaid_grade(doc),
            "smog": self._smog(doc, hard_words),
            "gunning_fog": self._gunning_fog(doc, hard_words),
            "automated_readability_index": self._automated_readability_index(doc),
            "coleman_liau_index": self._coleman_liau_index(doc),
            "lix": self._lix(doc, long_words),
            "rix": self._rix(doc, long_words),
        }

    def _flesch_reading_ease(self, doc: Doc):
        """
        206.835 - (1.015 X avg sent len) - (84.6 * avg_syl_per_word)
        Higher = easier to read
        Works best for English
        """
        score = (
            206.835
            - (1.015 * doc._.sentence_length["sentence_length_mean"])
            - (84.6 * doc._.syllables["syllables_per_token_mean"])
        )
        return score

    def _flesch_kincaid_grade(self, doc: Doc):
        """
        Score = grade required to read the text
        """
        score = (
            0.39 * doc._.sentence_length["sentence_length_mean"]
            + 11.8 * doc._.syllables["syllables_per_token_mean"]
            - 15.59
        )
        return score

    def _smog(self, doc: Doc, hard_words: int):
        """
        grade level = 1.043( sqrt(30 * (hard words /n sentences)) + 3.1291
        Preferably need 30+ sentences. Will not work with less than 4
        """
        if doc._._n_sentences >= 3:
            smog = (1.043 * (30 * (hard_words / doc._._n_sentences)) ** 0.5) + 3.1291
            return smog
        else:
            return 0.0

    def _gunning_fog(self, doc, hard_words: int):
        """
        Grade level = 0.4 * ((avg_sentence_length) + (percentage hard words))
        hard words = 3+ syllables
        """
        avg_sent_len = doc._.sentence_length["sentence_length_mean"]
        percent_hard_words = (hard_words / doc._._n_tokens) * 100
        return 0.4 * (avg_sent_len + percent_hard_words)

    def _automated_readability_index(self, doc: Doc):
        """
        Score = grade required to read the text
        """
        score = (
            4.71 * doc._.token_length["token_length_mean"]
            + 0.5 * doc._.sentence_length["sentence_length_mean"]
            - 21.43
        )
        return score

    def _coleman_liau_index(self, doc: Doc):
        """
        score = 0.0588 * avg number of chars pr 100 words -
            0.296 * avg num of sents pr 100 words -15.8
        Score = grade required to read the text
        """
        l = doc._.token_length["token_length_mean"] * 100
        s = (doc._._n_sentences / doc._.sentence_length["sentence_length_mean"]) * 100
        return 0.0588 * l - 0.296 * s - 15.8

    def _lix(self, doc: Doc, long_words: int):
        """
        (n_words / n_sentences) + (n_words longer than 6 letters * 100) / n_words
        """
        percent_long_words = long_words / doc._._n_tokens * 100
        return doc._.sentence_length["sentence_length_mean"] + percent_long_words

    def _rix(self, doc: Doc, long_words: int):
        """n_long_words / n_sentences"""
        return long_words / doc._._n_sentences
