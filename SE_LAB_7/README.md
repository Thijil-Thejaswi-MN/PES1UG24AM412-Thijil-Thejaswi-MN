# SE Lab 7: Fuzz Testing and Input Validation Bug Fixes

## Student Details
- **Name:** Thijil Thejaswi M.N.
- **SRN:** PES1UG24AM412
- **Course:** Software Engineering Lab (UE24CS252AA)
- **Topic:** Fuzz Testing and Input Validation Bug Fixes

---

## 1. Experiment Overview & Objectives

Traditional example-based unit tests typically only test expected, well-formed inputs. In production environments, applications frequently encounter malformed, unexpected, or adversarial inputs. This experiment applies **property-based fuzz testing** using the **Hypothesis** framework to identify crash vulnerabilities and harden a Python photo print order processing application.

Key objectives:
1. **Automated Defect Discovery:** Use Hypothesis strategies to generate unexpected input types (arbitrary Unicode, None, numbers, bytes, malformed strings).
2. **Root-Cause Analysis:** Utilize Hypothesis automatic test-case shrinking to find minimal reproducible counterexamples.
3. **Application Hardening:** Fix input validation defects in `photo_print_order.py` using explicit, safe checks without broad exception suppression.
4. **Verification:** Confirm that malformed inputs are handled safely (returning `None`) while normal valid-input behavior remains 100% intact.

---

## 2. Tools & Environment

- **Python Version:** 3.11.9
- **Test Framework:** `pytest` (v9.2.0)
- **Fuzz Testing Framework:** `hypothesis` (v6.170.15)
- **Operating System:** Windows 11

---

## 3. Application Architecture

The module `photo_print_order.py` provides three core functions:

1. `parse_order(text)`:
   - **Valid Format:** `size:copies` (e.g., `'4x6:25'`).
   - **Output:** Tuple `(size.upper(), copies)` where `copies >= 0`.
2. `file_size_average(sizes_csv)`:
   - **Valid Format:** Comma-separated non-negative integer file sizes (e.g., `'4,8,12'`).
   - **Output:** Integer floor average `sum(values) // len(values)`.
3. `payable_amount(text)`:
   - **Valid Format:** `amount|discount` (e.g., `'450|50'`).
   - **Output:** Calculated payable amount with 18% tax and discount floor: `max(amount * 1.18 - discount, 0.0)`.

---

## 4. Discovered Bugs & Minimal Counterexamples (Before Fix)

Running the Hypothesis fuzz suite against the original application exposed **6 critical failures** across all functions:

| Function | Minimal Counterexamples | Observed Exceptions / Behavior | Root Cause |
|:---|:---|:---|:---|
| `parse_order` | `s = ''`<br/>`s = None`<br/>`s = b''`<br/>`text = ':25'`<br/>`text = '4x6:-5'` | `ValueError: not enough values to unpack`<br/>`AttributeError: 'NoneType' has no split`<br/>`TypeError: bytes-like object required`<br/>Empty print size accepted<br/>Negative copies accepted | Direct `.split(':')` call without type check or delimiter count validation; no validation on size string or non-negative copy count. |
| `file_size_average` | `s = ''`<br/>`s = None`<br/>`text = ','`<br/>`text = '4,abc,12'`<br/>`text = '-1,-2,-3'` | `ValueError: invalid literal for int()`<br/>`AttributeError: 'NoneType' has no split`<br/>Calculated negative average (`-2`) | Unchecked `.split(',')` iteration converting empty/non-numeric tokens directly with `int()`; no validation for empty elements or non-negative ranges. |
| `payable_amount` | `s = ''`<br/>`s = None`<br/>`s = '|'`<br/>`text = 'nan|50'`<br/>`text = 'abc|50'`<br/>`text = '1.7e308|0'` | `ValueError: not enough values to unpack`<br/>`ValueError: could not convert string to float`<br/>Returns `nan` (numeric corruption)<br/>Calculated float overflow (`inf`) | Split on `\|` without token count check; direct `float()` conversion allowing `NaN`/`Infinity`; no checks against negative values or calculation overflow. |

---

## 5. Summary of Fixes Applied (Application Hardening)

A consistent invalid-input contract was implemented: **all functions safely return `None` when given invalid, malformed, or out-of-range input**. Broad `except Exception: return None` was avoided in favor of explicit validation:

1. **`parse_order(text)`**:
   - Validates `isinstance(text, str)`.
   - Validates exact delimiter count: `text.count(':') == 1`.
   - Strips whitespace and rejects empty print size.
   - Converts copies to integer with explicit `ValueError` handling.
   - Enforces `copies >= 0`.
   - Normalizes print size to uppercase (`size.upper()`).
2. **`file_size_average(sizes_csv)`**:
   - Validates `isinstance(sizes_csv, str)` and non-empty after stripping.
   - Splits on comma and verifies no empty tokens (e.g. leading, trailing, or double commas).
   - Validates every token as integer with explicit `ValueError` handling.
   - Enforces non-negative values (`val >= 0`).
   - Ensures non-empty list before integer floor division `sum(values) // len(values)`.
3. **`payable_amount(text)`**:
   - Validates `isinstance(text, str)`.
   - Validates exact delimiter count: `text.count('|') == 1`.
   - Safely converts amount and discount to float with explicit `ValueError` handling.
   - Rejects non-finite values using `math.isfinite(amount)` and `math.isfinite(discount)` (filtering NaN and infinity).
   - Rejects negative amounts or discounts (`amount >= 0`, `discount >= 0`).
   - Guards against floating-point overflow after computing total (`math.isfinite(total)`).
   - Applies the business formula `max(amount * 1.18 - discount, 0.0)`.

---

## 6. Execution Commands & Test Results

### 6.1. Running the Application Interactively
```bash
python photo_print_order.py
```
**Sample Inputs and Results:**
- Print size and copies: `4x6:25` $\rightarrow$ `('4X6', 25)`
- File sizes in MB: `4,8,12` $\rightarrow$ `8`
- Amount and discount: `450|50` $\rightarrow$ `481.0`

### 6.2. Running Hypothesis Fuzz Tests
```bash
python -m pytest -v test_photo_print_order.py
```

### 6.3. Summary of Test Results
- **Total Test Functions:** 9
- **Total Inputs Evaluated:** 900+ automatically generated test cases
- **Pre-Fix Result:** 6 Failed, 3 Passed
- **Post-Fix Result:** **9 Passed, 0 Failed (100% Success Rate)**

---

## 7. Deliverable Structure

```text
SE_LAB_7/
│
├── photo_print_order.py          # Hardened application code
├── test_photo_print_order.py     # Hypothesis property-based fuzz tests
├── README.md                     # Experiment documentation
├── Lab7_FuzzTesting_Report.pdf   # Complete formatted PDF report
│
└── screenshots/
    ├── 01_original_application.jpeg       # Original application run with valid inputs
    ├── 02_fuzz_failures_before_fix.jpeg   # Hypothesis failures on original code
    ├── 03_fixed_application.jpeg          # Hardened application run with valid inputs
    └── 04_fuzz_tests_after_fix.jpeg       # All 9 Hypothesis tests passing after fixes
```
