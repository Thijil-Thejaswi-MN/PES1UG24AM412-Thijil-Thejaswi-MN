"""
Code Coverage Test Suite for photo_print_order.py
Software Engineering Lab 6: Code and Branch Coverage
Student: Thijil Thejaswi M.N. (PES1UG24AM412)
"""

import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ============================================================================
# Tests for extra_print_charge()
# ============================================================================

def test_extra_print_charge_invalid_size():
    """Verify that an unsupported print size raises a ValueError."""
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("11x14", 10, "matte", False)


def test_extra_print_charge_negative_copies():
    """Verify that negative copies raise a ValueError."""
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_extra_print_charge_within_included_non_member():
    """Verify 0 charge when copies do not exceed included prints (non-member)."""
    assert extra_print_charge("4x6", 20, "matte", False) == 0
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_extra_print_charge_within_included_member():
    """Verify member bonus (+5 prints) for eligible print sizes like 4x6 and 5x7."""
    # 4x6 included is 20 + 5 = 25 for members
    assert extra_print_charge("4x6", 25, "matte", True) == 0
    # 5x7 included is 15 + 5 = 20 for members
    assert extra_print_charge("5x7", 20, "matte", True) == 0


def test_extra_print_charge_member_8x10_no_bonus():
    """Verify that 8x10 does not receive the +5 member bonus."""
    # 8x10 included is 10; 15 copies gives 5 extra prints
    assert extra_print_charge("8x10", 15, "matte", True) == 20


def test_extra_print_charge_matte_finish_standard():
    """Verify extra prints charge with matte finish (rate = 4) when extra <= 50."""
    # 4x6 included = 20; 25 copies -> extra = 5; rate = 4; total = 20
    assert extra_print_charge("4x6", 25, "matte", False) == 20


def test_extra_print_charge_other_finish_standard():
    """Verify extra prints charge with non-matte finish (rate = 7) when extra <= 50."""
    # 5x7 included = 15; 25 copies -> extra = 10; rate = 7; total = 70
    assert extra_print_charge("5x7", 25, "glossy", False) == 70


def test_extra_print_charge_extra_over_50_matte():
    """Verify rate increase by 2 for extra > 50 with matte finish (rate = 6)."""
    # 4x6 included = 20; 80 copies -> extra = 60; rate = 4 + 2 = 6; total = 360
    assert extra_print_charge("4x6", 80, "matte", False) == 360


def test_extra_print_charge_extra_over_50_canvas():
    """Verify canvas bonus (+5) along with standard extra > 50 rate (+2), rate = 14."""
    # 8x10 included = 10; 70 copies -> extra = 60; rate = 7 + 2 + 5 = 14; total = 840
    assert extra_print_charge("8x10", 70, "canvas", False) == 840


def test_extra_print_charge_extra_over_50_non_canvas():
    """Verify non-canvas non-matte finish with extra > 50 (rate = 7 + 2 = 9)."""
    # 5x7 included = 15; 75 copies -> extra = 60; rate = 7 + 2 = 9; total = 540
    assert extra_print_charge("5x7", 75, "glossy", False) == 540


# ============================================================================
# Tests for order_valid()
# ============================================================================

def test_order_valid_rush_allowed():
    """Verify rush order valid when copies <= 50."""
    assert order_valid(10, 50, True) is True


def test_order_valid_rush_exceeded():
    """Verify rush order invalid when copies > 50."""
    assert order_valid(10, 51, True) is False


def test_order_valid_regular_file_too_large():
    """Verify regular order rejected when file size > 25 MB."""
    assert order_valid(26, 10, False) is False


def test_order_valid_regular_valid():
    """Verify regular order accepted when file <= 25 MB and copies <= 500."""
    assert order_valid(20, 500, False) is True


def test_order_valid_regular_copies_exceeded():
    """Verify regular order rejected when copies > 500."""
    assert order_valid(15, 501, False) is False


# ============================================================================
# Tests for dispatch_status()
# ============================================================================

def test_dispatch_status_unframed_domestic_on_time():
    """Verify unframed domestic order (cutoff = 12) on time when hours >= 12."""
    assert dispatch_status(12, False, False) == "on_time"
    assert dispatch_status(20, False, False) == "on_time"


def test_dispatch_status_unframed_domestic_tight():
    """Verify unframed domestic order (cutoff = 12) tight when 6 <= hours < 12."""
    assert dispatch_status(11, False, False) == "tight"
    assert dispatch_status(6, False, False) == "tight"


def test_dispatch_status_unframed_domestic_missed():
    """Verify unframed domestic order (cutoff = 12) missed when hours < 6."""
    assert dispatch_status(5, False, False) == "missed"
    assert dispatch_status(0, False, False) == "missed"


def test_dispatch_status_framed_domestic():
    """Verify framed domestic order (cutoff = 24)."""
    assert dispatch_status(24, True, False) == "on_time"
    assert dispatch_status(18, True, False) == "tight"
    assert dispatch_status(17, True, False) == "missed"


def test_dispatch_status_framed_international():
    """Verify framed international order (cutoff = 24 + 24 = 48)."""
    assert dispatch_status(48, True, True) == "on_time"
    assert dispatch_status(42, True, True) == "tight"
    assert dispatch_status(41, True, True) == "missed"


def test_dispatch_status_unframed_international():
    """Verify unframed international order (cutoff = 12 + 24 = 36)."""
    assert dispatch_status(36, False, True) == "on_time"
    assert dispatch_status(30, False, True) == "tight"
    assert dispatch_status(29, False, True) == "missed"

