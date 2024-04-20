from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Tuple

PipelineFunc = Callable[[str, str, logging.LoggerAdapter], Tuple[str, str]]
"""A function for dictionary builds that checks and/or
transforms a Grascii string and its translation in a dictionary entry.

The first parameter is a Grascii string, the second parameter is its translation,
and the third parameter is a logger. The function must return a Grascii string
and a translation or raise a ``CancelPipeline`` exception.
"""


class CancelPipeline(Exception):
    """An Exception that can be thrown from a pipeline function to cancel the
    entire pipeline for a given entry."""

    pass


def create_grascii_check(ignore_case: bool = True) -> PipelineFunc:
    """Create a pipeline function that validates the Grascii string.

    :param ignore_case: Whether to ignore the case of the Grascii string. If
        ``False``, the Grascii string must be uppercase.
    :type ignore_case: bool
    """
    from grascii.parser import GrasciiValidator

    # Disable cache for now
    # It could be enabled, but we have to be careful about clearing the
    # cache after grammar changes
    validator = GrasciiValidator(ignore_case=ignore_case)

    def check_grascii(grascii: str, translation: str, logger: logging.LoggerAdapter):
        if not validator.validate(grascii):
            logger.error(f"Failed to parse {grascii}")
            raise CancelPipeline
        return grascii, translation

    return check_grascii


def create_spell_check(words_file: os.PathLike) -> PipelineFunc:
    """Create a pipeline function that checks the words in a translation using
    the words from a file.

    :param words_file: A path to a line-delimited words file.
    :type words_file: os.PathLike
    """

    words = set()
    with Path(words_file).open("r") as f:
        words |= set(line.strip().upper() for line in f)

    def spell_check(grascii: str, translation: str, logger: logging.LoggerAdapter):
        translation_words = [w.upper() for w in translation.split()]
        for translation_word in translation_words:
            if translation_word not in words:
                logger.warning(f"{translation_word} not in words file")
        return grascii, translation

    return spell_check


def remove_boundaries(grascii: str, translation: str, logger: logging.LoggerAdapter):
    """A pipeline function that removes boundary characters from the Grascii string."""
    return grascii.replace("-", ""), translation


def standardize_case(grascii: str, translation: str, logger: logging.LoggerAdapter):
    """A pipeline function that uppercases the Grascii string and capitalizes
    each word in the translation.
    """
    capitalized = " ".join(w.capitalize() for w in translation.split())
    return grascii.upper(), capitalized
