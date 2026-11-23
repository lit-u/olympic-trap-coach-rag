"""Standard-library regression checks for RAG v0.2 (python -m unittest discover)."""
import unittest

import retrieve


class KnowledgeV02Tests(unittest.TestCase):
    def test_complete_unique_ids(self):
        self.assertEqual(len(retrieve.load_chunks()), 52)
        index = retrieve.load_index()
        self.assertEqual(len(index["items"]), 52)
        self.assertEqual(len(index["edges"]), 36)
        required = {"discipline", "factor", "phase", "knowledge_kind",
                    "reliability", "esp32_measurement", "coach_use"}
        for entry in index["items"]:
            self.assertTrue(required.issubset(entry))
            self.assertTrue(all(entry[key] for key in required))

    def test_body_catch(self):
        ids = {x["id"] for x in retrieve.retrieve(
            "Kaip pagauti lekste ir sukti korpusa o ne rankomis?", 8)}
        self.assertIn("K-104", ids)
        self.assertIn("K-101", ids)

    def test_attention_and_rhythm(self):
        ids = {x["id"] for x in retrieve.retrieve(
            "Pavargsta akys, prarandu demesi ir ritma", 8)}
        self.assertIn("K-112", ids)
        self.assertIn("C-03", ids)

    def test_hit_modes(self):
        ids = {x["id"] for x in retrieve.retrieve(
            "Kuo skiriasi H1 H2 H3? Kaip treniruoti ritma?", 8)}
        self.assertIn("K-207", ids)
        self.assertIn("T-04", ids)

    def test_rifle_not_recommended(self):
        ids = {x["id"] for x in retrieve.retrieve(
            "Ar reikia sulaikyti kvepavima kaip su pneumatiniu sautuvu?", 8)}
        self.assertIn("C-12", ids)
        self.assertNotIn("K-112", ids)
        self.assertNotIn("S-SPANCKEN-2021",
                         retrieve.DOCUMENT.read_text(encoding="utf-8"))

    def test_valid_limits(self):
        with self.assertRaises(ValueError):
            retrieve.retrieve("trap", 9)


if __name__ == "__main__":
    unittest.main()
