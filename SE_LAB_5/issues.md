# Static Code Analysis Issue Inventory — Restaurant Order System

**Student SRN:** PES1UG24AM412
**Target File:** `restaurant_order_system.py`
**Repository:** `https://github.com/SETAPESU26/L5_49_restaurant_order_system`
**Baseline Git Commit:** `a0182328c055af8da89d2a8d114018b81969b2a9`
**Baseline Pylint Score:** 4.81/10
**Baseline Bandit Issues:** 5 (High: 2, Medium: 1, Low: 2)
**Baseline Flake8 Violations:** 9

---

## 1. Summary Issue Table (Lab Handout Format)

| Issue | Type | Line(s) | Description | Fix Approach |
| :--- | :--- | :--- | :--- | :--- |
| Shell Process Injection (`B605`) | Security | 58 | `os.system` runs shell command with concatenated string | Replace shell invocation with standard Python file logging / safe output |
| Insecure Cryptographic Hash (`B324`) | Security | 47 | Insecure MD5 hash function used for ticket hashing | Replace MD5 with SHA-256 (`hashlib.sha256`) |
| Unsafe Expression Evaluation (`B307`, `W0123`) | Security / Bug | 42 | Arbitrary expression evaluation using `eval()` | Replace `eval` with validated discount rate calculation |
| Predictable Pseudo-Random Generator (`B311`) | Security | 51 | `random.randint` is insecure for PIN generation | Replace with `secrets.randbelow` / `secrets.SystemRandom` |
| Bare `except: pass` Block (`B110`, `E722`, `W0702`) | Security / Bug | 26-27 | Silences all exceptions indiscriminately | Catch specific `KeyError` or use safe dict removal (`dict.pop`) |
| Mutable Default Argument (`W0102`) | Bug | 15 | `order_log=[]` default persists across calls | Set default to `None` and initialize list within function |
| Unused Imports and Variables (`W0611`, `W0612`, `F401`, `F841`) | Quality | 6, 31, 41 | Unused import `math` and dead variables `service_tax`, `base_bill` | Remove unused import and eliminate dead variable assignments |
| Redefined Outer Scope (`W0621`) | Quality | 61 | Parameter `orders` shadows module-level `orders` dictionary | Rename parameter to `orders_dict` |
| Resource Management & Missing Encoding (`R1732`, `W1514`) | Quality | 55-57 | `open()` without `with` context manager or UTF-8 encoding | Use `with open(..., "w", encoding="utf-8") as f:` block |
| Non-PEP 8 Naming Conventions (`C0103`) | Style | 15, 23, 30, 40 | CamelCase function names violate snake_case standards | Refactor function names to PEP 8 compliant snake_case |
| Hardcoded Sensitive Credential (Manual Review) | Security | 71 | Plaintext credential `pos_terminal_key` in code | Retrieve secret from environment variable via `os.getenv` |

---

## 2. Detailed Issue Inventory

### Issue 1: Shell Execution with Possible Command Injection
- **Identifier & Tool:** Bandit `B605:start_process_with_a_shell`
- **Actual Line Number:** 58
- **Severity & Confidence:** Severity: High | Confidence: High (CWE-78)
- **Description & Potential Impact:** The program executes `os.system("echo Ticket sent to kitchen printer: " + filename)`. Passing an unvalidated or attacker-manipulated filename through the system shell allows arbitrary command injection and unauthorized execution on the host operating system.
- **Proposed Fix:** Eliminate the external shell call entirely. Replace with Python standard output / logging: `print(f"Ticket sent to kitchen printer: {filename}")`.
- **Verification Method:** Run `bandit -r restaurant_order_system.py` to confirm issue `B605` is resolved; verify ticket export message appears correctly at runtime.

### Issue 2: Weak Cryptographic Hash Function (MD5)
- **Identifier & Tool:** Bandit `B324:hashlib`
- **Actual Line Number:** 47
- **Severity & Confidence:** Severity: High | Confidence: High (CWE-327)
- **Description & Potential Impact:** `hashlib.md5(table_id.encode()).hexdigest()` generates ticket hashes using MD5, which is cryptographically broken and prone to collision attacks.
- **Proposed Fix:** Replace MD5 with a secure, standard collision-resistant hashing algorithm such as SHA-256 (`hashlib.sha256(table_id.encode()).hexdigest()`).
- **Verification Method:** Run `bandit -r restaurant_order_system.py` to confirm `B324` is eliminated; execute script to ensure valid hexadecimal hash generation.

### Issue 3: Insecure Dynamic Code Execution via `eval()`
- **Identifier & Tool:** Bandit `B307:blacklist` / Pylint `W0123:eval-used`
- **Actual Line Number:** 42
- **Severity & Confidence:** Severity: Medium | Confidence: High (CWE-78)
- **Description & Potential Impact:** `net_total = eval(promo_expr)` evaluates arbitrary user-supplied string expressions inside the Python execution context. Any untrusted promo input can execute arbitrary Python commands (e.g., `__import__('os').system(...)`), causing complete system compromise.
- **Proposed Fix:** Remove `eval()`. Implement safe discount computation accepting either a validated numeric discount factor/rate or structured computation (e.g., `calculate_discounted_bill(table_id, discount_rate)` where `net_total = round(base_bill * (1.0 - discount_rate), 2)`).
- **Verification Method:** Run Bandit and Pylint to verify absence of `B307` and `W0123`; test discount calculation on table T1 to confirm exact expected arithmetic output ($45.0 * 0.90 = $40.5).

### Issue 4: Predictable Pseudo-Random Number Generator
- **Identifier & Tool:** Bandit `B311:blacklist`
- **Actual Line Number:** 51
- **Severity & Confidence:** Severity: Low | Confidence: High (CWE-330)
- **Description & Potential Impact:** `random.randint(1000, 9999)` relies on the Mersenne Twister PRNG, which is completely deterministic and unsuitable for security credentials, PINs, or tokens.
- **Proposed Fix:** Use Python's cryptographically secure random number module `secrets`: `secrets.SystemRandom().randint(1000, 9999)`.
- **Verification Method:** Run `bandit -r restaurant_order_system.py` to verify `B311` is cleared; run program to confirm 4-digit PIN output.

### Issue 5: Bare `except: pass` Silencing Exceptions
- **Identifier & Tool:** Bandit `B110:try_except_pass` / Flake8 `E722` / Pylint `W0702`
- **Actual Line Number:** 26-27
- **Severity & Confidence:** Severity: Low | Confidence: High (CWE-703)
- **Description & Potential Impact:** In `voidTableOrder`, the construct `except: pass` catches and suppresses every possible exception, including `KeyboardInterrupt`, `SystemExit`, and memory errors, obscuring critical bugs.
- **Proposed Fix:** Catch only expected exceptions (`KeyError`) or use safe dictionary removal: `orders.pop(table_id, None)`.
- **Verification Method:** Run Flake8, Pylint, and Bandit to verify `E722`, `W0702`, and `B110` are resolved.

### Issue 6: Mutable Default Argument in Function Definition
- **Identifier & Tool:** Pylint `W0102:dangerous-default-value`
- **Actual Line Number:** 15
- **Severity & Confidence:** Quality / High Logical Bug Risk
- **Description & Potential Impact:** `def placeTableOrder(..., order_log=[])` binds a single mutable list instance to the function object at definition time. All calls sharing the default will mutate the same list across different function invocations.
- **Proposed Fix:** Set the default parameter value to `None` and conditionally instantiate a new list inside the function:
  ```python
  if order_log is None:
      order_log = []
  ```
- **Verification Method:** Run `pylint restaurant_order_system.py` to verify `W0102` is resolved; test multiple calls without supplying `order_log` to confirm isolation.

### Issue 7: Unused Imports and Dead Local Variables
- **Identifier & Tool:** Pylint `W0611`, `W0612` / Flake8 `F401`, `F841`
- **Actual Line Numbers:** 6 (`math`), 31 (`service_tax`), 41 (`base_bill`), 63 (`t`)
- **Severity & Confidence:** Quality / Maintenance Debt
- **Description & Potential Impact:** `import math` is never used; `service_tax` in `checkTableStatus` is assigned but never referenced; loop variable `t` in `get_pending_summary` is unused. These degrade code clarity and waste resources.
- **Proposed Fix:** Remove unused `import math`, delete unused assignments, and use `_` or dictionary value iteration (`orders.values()`).
- **Verification Method:** Run Pylint and Flake8 to ensure `W0611`, `W0612`, `F401`, and `F841` are resolved.

### Issue 8: Scope Shadowing of Outer Variable
- **Identifier & Tool:** Pylint `W0621:redefined-outer-name`
- **Actual Line Number:** 61
- **Severity & Confidence:** Quality / Bug Risk
- **Description & Potential Impact:** The function parameter `orders` in `get_pending_summary(orders)` shadows the global dictionary `orders`, creating confusion over variable scope.
- **Proposed Fix:** Rename parameter to `orders_dict` or `order_records`.
- **Verification Method:** Run Pylint to confirm resolution of `W0621`.

### Issue 9: File Resource Leak and Unspecified Character Encoding
- **Identifier & Tool:** Pylint `R1732:consider-using-with`, `W1514:unspecified-encoding`
- **Actual Line Number:** 55-57
- **Severity & Confidence:** Quality / Reliability Risk
- **Description & Potential Impact:** Opening files via `f = open(...)` without a `with` statement risks leaving file descriptors open if an error occurs. Omitting encoding can corrupt data on systems with non-UTF-8 defaults.
- **Proposed Fix:** Use `with open(filename, "w", encoding="utf-8") as file:`.
- **Verification Method:** Run Pylint to confirm `R1732` and `W1514` are resolved.

### Issue 10: Non-PEP 8 Function Naming Conventions
- **Identifier & Tool:** Pylint `C0103:invalid-name`
- **Actual Line Numbers:** 15, 23, 30, 40
- **Severity & Confidence:** Style / Standards Violation
- **Description & Potential Impact:** Functions `placeTableOrder`, `voidTableOrder`, `checkTableStatus`, and `calculateDiscountedBill` use camelCase instead of PEP 8 snake_case.
- **Proposed Fix:** Rename functions to `place_table_order`, `void_table_order`, `check_table_status`, and `calculate_discounted_bill`. Provide backwards-compatible aliases if necessary.
- **Verification Method:** Run Pylint to confirm `C0103` is eliminated.

### Issue 11: Singleton Comparison with `== None`
- **Identifier & Tool:** Pylint `C0121:singleton-comparison` / Flake8 `E711`
- **Actual Line Number:** 32
- **Severity & Confidence:** Style / Best Practice
- **Description & Potential Impact:** `orders.get(table_id) == None` uses equality instead of identity checking (`is None`), which violates Python standards.
- **Proposed Fix:** Change to `if orders.get(table_id) is None:`.
- **Verification Method:** Run Pylint and Flake8 to verify `C0121` and `E711` are resolved.

### Issue 12: Missing Function Docstrings, Line Length & End-of-File Newline
- **Identifier & Tool:** Pylint `C0116`, `C0301`, `C0304` / Flake8 `E501`, `W292`
- **Actual Line Numbers:** 15, 18, 19, 23, 30, 40, 46, 50, 54, 61, 75, 83
- **Severity & Confidence:** Style / Documentation
- **Description & Potential Impact:** Missing function docstrings make the codebase undocumented. Lines exceed recommended lengths (110 chars on line 18). Missing final newline violates POSIX/PEP 8 file standards.
- **Proposed Fix:** Add comprehensive docstrings to all functions, wrap long lines to under 79 characters, and ensure trailing newline.
- **Verification Method:** Run Pylint and Flake8 to verify clean docstring and line-formatting reports.

---

## 3. Manual Code Review Findings (Beyond Tool Detection)

### Issue 13: Hardcoded Terminal Secret Token
- **Source:** Manual Code Review
- **Actual Line Number:** 71
- **Severity:** High (Security)
- **Description & Potential Impact:** `pos_terminal_key = "POS_TERMINAL_SECRET_TOKEN_2026"` hardcodes sensitive authorization credentials directly in source code, causing credential leakage when committed to version control.
- **Proposed Fix:** Retrieve the credential securely from an environment variable: `os.getenv("POS_TERMINAL_KEY", "DEFAULT_DEMO_KEY")`.
- **Verification Method:** Verify code does not contain raw hardcoded secret and runs with environment variable fallback.

### Issue 14: Unstructured Data Serialization in Kitchen Export
- **Source:** Manual Code Review
- **Actual Line Number:** 56
- **Severity:** Medium (Data Integrity)
- **Description & Potential Impact:** `f.write(str(orders))` serializes the internal Python string representation of a dictionary rather than standard formatted text or JSON, making it difficult for downstream kitchen printers or ticketing systems to ingest reliably.
- **Proposed Fix:** Serialize orders cleanly as formatted text or JSON.
- **Verification Method:** Inspect generated `kitchen_orders.txt` for readable, structured layout.
