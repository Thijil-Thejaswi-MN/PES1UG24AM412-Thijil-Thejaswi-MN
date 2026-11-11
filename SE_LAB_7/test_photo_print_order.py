"""
Fuzz Testing Suite for photo_print_order.py using Hypothesis
Software Engineering Lab 7: Fuzz Testing and Input Validation Bug Fixes
Student: Thijil Thejaswi M.N. (PES1UG24AM412)
"""

import math
from hypothesis import given, settings, strategies as st
from photo_print_order import parse_order, file_size_average, payable_amount


# Strategy for arbitrary unexpected inputs: strings, None, numbers, bytes
arbitrary_unexpected_input = (
    st.text()
    | st.none()
    | st.integers()
    | st.floats()
    | st.binary()
)


def is_valid_integer(value):
    """Helper to check if a string can be parsed as an integer after stripping."""
    try:
        int(value.strip())
        return True
    except ValueError:
        return False


# ============================================================================
# 1. parse_order() Fuzz & Property Tests
# ============================================================================

@settings(max_examples=100)
@given(arbitrary_unexpected_input)
def test_parse_order_no_crash(s):
    """Fuzz test parse_order() with unexpected inputs: must not crash."""
    result = parse_order(s)
    if result is not None:
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str) and result[0] != ""
        assert isinstance(result[1], int) and result[1] >= 0


@settings(max_examples=100)
@given(
    st.one_of(
        # Empty string
        st.just(""),
        # Missing colon separator
        st.text().filter(lambda x: ":" not in x),
        # Multiple colon separators
        st.lists(st.text(min_size=1), min_size=3, max_size=5).map(lambda p: ":".join(p)),
        # Missing print size (:copies)
        st.integers().map(lambda c: f":{c}"),
        # Missing copy count (size:)
        st.text(min_size=1).filter(lambda x: ":" not in x).map(lambda s: f"{s}:"),
        # Non-numeric copy string
        st.tuples(
            st.text(min_size=1).filter(lambda x: ":" not in x),
            st.text().filter(lambda x: not is_valid_integer(x))
        ).map(lambda t: f"{t[0]}:{t[1]}"),
        # Negative copy count
        st.tuples(
            st.text(min_size=1).filter(lambda x: ":" not in x),
            st.integers(max_value=-1)
        ).map(lambda t: f"{t[0]}:{t[1]}"),
    )
)
def test_parse_order_malformed_inputs(text):
    """Verify that malformed or invalid inputs safely return None."""
    assert parse_order(text) is None


@settings(max_examples=100)
@given(
    size=st.from_regex(r"^[a-zA-Z0-9 ]+$", fullmatch=True).filter(lambda s: s.strip() != ""),
    copies=st.integers(min_value=0, max_value=100000)
)
def test_parse_order_valid_properties(size, copies):
    """Verify correct tuple structure and normalization for valid order formats."""
    text = f"{size}:{copies}"
    result = parse_order(text)
    assert result is not None
    assert result == (size.strip().upper(), copies)
    assert result[1] >= 0


# ============================================================================
# 2. file_size_average() Fuzz & Property Tests
# ============================================================================

@settings(max_examples=100)
@given(arbitrary_unexpected_input)
def test_file_size_average_no_crash(s):
    """Fuzz test file_size_average() with unexpected inputs: must not crash."""
    result = file_size_average(s)
    if result is not None:
        assert isinstance(result, int)
        assert result >= 0


@settings(max_examples=100)
@given(
    st.one_of(
        # Empty string
        st.just(""),
        # Whitespace-only string
        st.just("   "),
        # Empty CSV elements (e.g. leading, trailing, or double commas)
        st.sampled_from([",", ",,", "4,,8", "4,8,", ",4,8"]),
        # Non-integer tokens
        st.sampled_from(["4,abc,12", "hello", "4,8.5,12", "true,false"]),
        # Negative file sizes
        st.sampled_from(["4,-8,12", "-5", "-1,-2,-3"]),
    )
)
def test_file_size_average_malformed_inputs(text):
    """Verify that malformed CSV inputs safely return None."""
    assert file_size_average(text) is None


@settings(max_examples=100)
@given(
    sizes=st.lists(st.integers(min_value=0, max_value=1000000), min_size=1, max_size=50)
)
def test_file_size_average_valid_properties(sizes):
    """Verify that valid CSV integer inputs compute the correct integer average."""
    sizes_csv = ",".join(str(s) for s in sizes)
    result = file_size_average(sizes_csv)
    assert result is not None
    assert result == sum(sizes) // len(sizes)
    assert isinstance(result, int)


# ============================================================================
# 3. payable_amount() Fuzz & Property Tests
# ============================================================================

@settings(max_examples=100)
@given(arbitrary_unexpected_input)
def test_payable_amount_no_crash(s):
    """Fuzz test payable_amount() with unexpected inputs: must not crash."""
    result = payable_amount(s)
    if result is not None:
        assert isinstance(result, (int, float))
        assert not math.isnan(result)
        assert not math.isinf(result)
        assert result >= 0


@settings(max_examples=100)
@given(
    st.one_of(
        # Empty string
        st.just(""),
        # Missing pipe separator
        st.text().filter(lambda x: "|" not in x),
        # Multiple pipe separators
        st.lists(st.text(min_size=1), min_size=3, max_size=5).map(lambda p: "|".join(p)),
        # Invalid non-numeric strings
        st.sampled_from(["abc|50", "450|xyz", "foo|bar", "|", "450|", "|50"]),
        # Non-finite inputs: NaN, inf, or overflow
        st.sampled_from(["nan|50", "450|nan", "inf|50", "450|inf", "-inf|50", "1.7e308|0"]),
        # Negative amount or discount
        st.sampled_from(["-450|50", "450|-50", "-100|-20"]),
    )
)
def test_payable_amount_malformed_inputs(text):
    """Verify that malformed payable amount inputs safely return None."""
    assert payable_amount(text) is None


@settings(max_examples=100)
@given(
    amount=st.floats(min_value=0.0, max_value=1e5, allow_nan=False, allow_infinity=False),
    discount=st.floats(min_value=0.0, max_value=1e5, allow_nan=False, allow_infinity=False)
)
def test_payable_amount_valid_properties(amount, discount):
    """Verify correct payable amount calculation with 18% tax and discount floor."""
    text = f"{amount}|{discount}"
    result = payable_amount(text)
    assert result is not None
    expected = max(float(amount) * 1.18 - float(discount), 0.0)
    assert math.isclose(result, expected, rel_tol=1e-5, abs_tol=1e-5)
    assert result >= 0
