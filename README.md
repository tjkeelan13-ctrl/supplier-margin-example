# Supplier margin audit: a worked CSV example

A small, reproducible example for store owners who receive supplier price lists. It shows how a cost change affects **gross margin**, why margin differs from markup, and which SKU matches must be reviewed rather than guessed.

**Status:** public example and feedback pilot. No checkout, no orders accepted, no merchant outcome claims. All data in this repository is synthetic.

## Try the example

1. Open [the catalog CSV](examples/catalog.csv) and [the supplier CSV](examples/supplier.csv).
2. Read [the expected audit report](examples/expected-audit.csv).
3. With Python 3.10 or newer, verify the bundled example:

   ```sh
   python -m unittest discover -s . -p "check_example.py" -v
   ```

   The verifier uses only Python's standard library. It checks these fixed example files; it is **not** a general-purpose catalog auditor or the downloadable product.

## The useful calculation

The catalog sells SKU `00124`, a canvas tote, for **20.00**. The supplier now charges **14.00** per unit.

- Gross margin = `(selling price - unit cost) / selling price`.
- Here: `(20 - 14) / 20 = 30%`.
- A 40% **markup** on cost would give `14 × 1.4 = 19.60`, which is only about 28.57% gross margin.
- A 40% **gross-margin** target instead requires `14 / (1 - 0.40) = 23.333…`.
- Rounding the floor **up** to a cent gives **23.34**, not 23.33.

The example has six catalog rows: two below the 40% target, two at/above it, and two requiring review. `OLD-99` has no supplier match. `DUP-1` occurs twice in the supplier list, so choosing either cost silently would be wrong. `NEW-55` is supplier-only and is not added to the catalog report.

Keep SKUs as text: `00124` is not `124`. The report uses a leading apostrophe for numeric-looking SKUs to help preserve them in spreadsheets. These files use exact, case-sensitive SKU matches and one currency; they do not include currency symbols or thousands separators.

**This is not a store-import file.** Do not import the audit report into a live shop. Unit-cost gross margin excludes payment fees, shipping, tax, discounts, returns and overhead. It is not net profit or a recommendation to change a real price.

## The product idea being tested

Supplier Price Check is a separate, prelaunch, standalone HTML utility that accepts your own two CSVs, maps SKU and amount columns, flags low margins and ambiguous matches, and downloads an audit report. The proposed offer is **US$19 once for one business**, not a subscription. The paid utility and its source are not included in this example repository.

The candidate distinction is a file you can keep and run offline, without a store connection or an account. It does not support native XLSX, historical supplier comparisons, inventory, store write-back, currency conversion or net-profit accounting. There is no promise of lifetime support or updates.

**You may not need to pay.** Spreadsheet formulas or [CostRift's free plan](https://costrift.com/pricing) may already be sufficient. We have not established that the standalone-file distinction is worth $19 to buyers.

## Tell us about the last real workflow

[Open a workflow-feedback issue](https://github.com/tjkeelan13-ctrl/supplier-margin-example/issues/new?template=workflow-feedback.md) if you actually deal with supplier lists and want to explain what is painful, what already works, or what would make this product worth paying for. A GitHub account is required. The template also lets you state non-binding interest at the proposed price; no reservation, order, invoice or payment is created.

**Issues are public.** Do not attach real catalogs, supplier lists, customer information, passwords, payment details or confidential commercial data. Describe column names and workflow in general terms, using invented values only. We will not ask for money or contact you elsewhere based on an issue. We may reply in the issue.

There is no payment link yet. Payments must eventually use a verified seller account controlled by this project's owner; no third-party or agent wallet is involved. This pilot has no verified sales or product-specific buyer validation.

## License and scope

The [MIT license](LICENSE) covers only the public example files in this repository, not the separate prelaunch product. This project is independent and is not affiliated with Shopify, WooCommerce or CostRift.
