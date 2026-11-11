"""Verify only the bundled synthetic example; not a production catalog auditor.

Run: python -m unittest discover -s . -p "check_example.py" -v
No third-party packages, network access or file writes.
"""

import csv
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
TARGET = Decimal("0.40")
CENT = Decimal("0.01")


def read_rows(name):
    with (ROOT / "examples" / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def floor_price(cost):
    return (cost / (Decimal(1) - TARGET)).quantize(CENT, rounding=ROUND_CEILING)


class SyntheticExampleChecks(unittest.TestCase):
    """Fixed-fixture checks, not an input-validation/security test suite."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = read_rows("catalog.csv")
        cls.supplier = read_rows("supplier.csv")
        cls.expected = read_rows("expected-audit.csv")
        cls.by_sku = defaultdict(list)
        for row in cls.supplier:
            cls.by_sku[row["Supplier SKU"]].append(row)

    def test_example_sizes(self):
        self.assertEqual(len(self.catalog), 6)
        self.assertEqual(len(self.supplier), 7)
        self.assertEqual(len(self.expected), 6)

    def test_expected_classifications_and_amounts(self):
        for index, (item, report) in enumerate(zip(self.catalog, self.expected), 1):
            with self.subTest(sku=item["SKU"]):
                sku = item["SKU"]
                matches = self.by_sku[sku]
                self.assertEqual(report["Catalog data row"], str(index))
                safe_sku = "'" + sku if sku.isdigit() else sku
                self.assertEqual(report["SKU (spreadsheet-safe text)"], safe_sku)
                if not matches:
                    status = "No supplier match"
                elif len(matches) != 1:
                    status = "Duplicate supplier SKU"
                else:
                    price = Decimal(item["Price"])
                    cost = Decimal(matches[0]["Unit cost"])
                    margin = (price - cost) / price
                    status = "Below target" if margin < TARGET else "At/above target"
                    self.assertEqual(Decimal(report["Selling price"]), price)
                    self.assertEqual(Decimal(report["Supplier cost"]), cost)
                    rounded_margin = (margin * 100).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                    self.assertEqual(Decimal(report["Gross margin percent"]), rounded_margin)
                    self.assertEqual(Decimal(report["Target-floor price"]), floor_price(cost))
                self.assertEqual(report["Status"], status)
                if len(matches) != 1:
                    for name in ("Selling price", "Supplier cost", "Gross margin percent", "Target-floor price"):
                        self.assertEqual(report[name], "")

    def test_summary(self):
        self.assertEqual(Counter(row["Status"] for row in self.expected), {
            "Below target": 2,
            "At/above target": 2,
            "No supplier match": 1,
            "Duplicate supplier SKU": 1,
        })

    def test_leading_zero_sku_is_text(self):
        self.assertEqual(self.catalog[0]["SKU"], "00124")
        self.assertNotIn("124", self.by_sku)
        self.assertEqual(self.expected[0]["SKU (spreadsheet-safe text)"], "'00124")

    def test_supplier_only_item_not_in_report(self):
        catalog_skus = {row["SKU"] for row in self.catalog}
        supplier_skus = set(self.by_sku)
        self.assertEqual(supplier_skus - catalog_skus, {"NEW-55"})
        self.assertNotIn("NEW-55", {row["SKU (spreadsheet-safe text)"] for row in self.expected})

    def test_rounding_up_preserves_target(self):
        cost = Decimal("14")
        proposed = floor_price(cost)
        self.assertEqual(proposed, Decimal("23.34"))
        self.assertGreaterEqual((proposed - cost) / proposed, TARGET)
        lower = proposed - CENT
        self.assertLess((lower - cost) / lower, TARGET)

    def test_markup_is_not_margin(self):
        cost = Decimal("14")
        markup_price = cost * Decimal("1.40")
        self.assertEqual(markup_price, Decimal("19.60"))
        self.assertLess((markup_price - cost) / markup_price, TARGET)

    def test_expected_report_is_not_an_import_template(self):
        self.assertIn("Catalog data row", self.expected[0])
        self.assertIn("Notes", self.expected[0])
        for row in self.expected:
            self.assertTrue(row["Notes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
