#!/usr/bin/env python3
"""Tests for the PDF text repair pass.  Run: python3 scripts/test_bcm_text.py"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcm_text as t


class CleanParagraph(unittest.TestCase):
    def test_rejoins_hyphenated_line_break(self):
        self.assertEqual(t.clean_paragraph("moun-\ntain weather"), "mountain weather")

    def test_keeps_real_compound_and_closes_it_up(self):
        self.assertEqual(t.clean_paragraph("Anti-\nGravity skis"), "Anti-Gravity skis")

    def test_expands_ligatures(self):
        self.assertEqual(t.clean_paragraph("the ﬁrst ﬂake"), "the first flake")

    def test_joins_wrapped_lines_but_keeps_paragraphs(self):
        self.assertEqual(
            t.clean_paragraph("a line that\nwrapped.\n\nA new graf."),
            "a line that wrapped.\n\nA new graf.")

    def test_curls_quotes(self):
        self.assertEqual(t.clean_paragraph('He said "fine" today.'),
                         "He said “fine” today.")

    def test_curls_possessive_and_contraction(self):
        self.assertEqual(t.clean_paragraph("Liam's skis didn't break."),
                         "Liam’s skis didn’t break.")

    def test_elision_apostrophe_faces_the_right_way(self):
        # The case a naive straight-to-curly pass gets backwards.
        self.assertEqual(t.clean_paragraph("back in the '80s"), "back in the ’80s")
        self.assertEqual(t.clean_paragraph("'til dark"), "’til dark")

    def test_double_hyphen_becomes_tight_em_dash(self):
        self.assertEqual(t.clean_paragraph("fine--then wind"), "fine—then wind")

    def test_number_range_becomes_en_dash(self):
        self.assertEqual(t.clean_paragraph("200 - 300 feet"), "200–300 feet")

    def test_strips_invisibles_and_odd_spaces(self):
        self.assertEqual(t.clean_paragraph("a­b c"), "ab c")

    def test_converts_print_end_mark_when_asked(self):
        self.assertEqual(t.clean_paragraph("the end. ∎", end_mark=True),
                         "the end. ❆")

    def test_removes_stray_end_mark_when_not_the_last_graf(self):
        self.assertEqual(t.clean_paragraph("the end. ∎"), "the end.")

    def test_fixes_space_before_punctuation(self):
        self.assertEqual(t.clean_paragraph("cold ."), "cold.")


class CaptionCredit(unittest.TestCase):
    def test_splits_trailing_name(self):
        self.assertEqual(
            t.split_caption_credit("Skiers climb at dawn. Liam McGee"),
            ("Skiers climb at dawn.", "Liam McGee"))

    def test_credit_only(self):
        self.assertEqual(t.split_caption_credit("Teton County Search and Rescue"),
                         (None, "Teton County Search and Rescue"))

    def test_labelled_credit(self):
        self.assertEqual(
            t.split_caption_credit("Dropping in at first light. Photo by Brian Mohr"),
            ("Dropping in at first light.", "Brian Mohr"))

    def test_caption_with_no_credit_stays_whole(self):
        self.assertEqual(
            t.split_caption_credit("A caption that just describes the scene."),
            ("A caption that just describes the scene.", None))

    def test_empty(self):
        self.assertEqual(t.split_caption_credit(""), (None, None))


class Furniture(unittest.TestCase):
    def test_strips_running_head_repeated_across_pages(self):
        pages = ["27 / Gear Test Week\nreal copy here\n42",
                 "27 / Gear Test Week\nmore real copy\n43",
                 "27 / Gear Test Week\nstill more copy\n44"]
        out = t.strip_furniture(pages)
        for page in out:
            self.assertNotIn("Gear Test Week", page)
        self.assertIn("real copy here", out[0])

    def test_strips_bare_folio_numbers(self):
        out = t.strip_furniture(["12\nbody copy\n", "13\nmore body\n"])
        self.assertNotIn("12", out[0])
        self.assertIn("body copy", out[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
