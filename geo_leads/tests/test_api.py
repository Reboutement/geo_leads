import frappe
from frappe.tests.utils import FrappeTestCase

from geo_leads import api


class TestHelpers(FrappeTestCase):
    def test_normalize_phone(self):
        self.assertEqual(api._normalize_phone("06 12 34 56 78"), "0612345678")
        self.assertEqual(api._normalize_phone("+33 6 12 34 56 78"), "+33612345678")
        self.assertEqual(api._normalize_phone("12"), "")

    def test_split_name(self):
        self.assertEqual(api._split_name("Marie Dupont Martin"), ("Marie", "Dupont Martin"))
        self.assertEqual(api._split_name("Marie"), ("Marie", ""))

    def test_notes_skip_empty(self):
        notes = api._build_notes({"type": "audit", "zip": "56850", "symptoms": ["Buee"]})
        self.assertIn("Type de demande : audit", notes)
        self.assertIn("Symptomes : Buee", notes)
        self.assertNotIn("Message", notes)

    def test_notes_include_commercial_and_summary(self):
        notes = api._build_notes({"commercial": "Marc", "summary": "HR 68 %"})
        self.assertIn("Commercial : Marc", notes)
        self.assertIn("Résumé de la visite : HR 68 %", notes)
