"""
Branch Coverage Test Suite for photo_print_order.py
Software Engineering Lab 6: Code and Branch Coverage
Student: Thijil Thejaswi M.N. (PES1UG24AM412)

This test suite targets 100% Branch Coverage by exercising:
1. Every decision outcome (True and False) for each conditional statement.
2. Compound condition sub-decisions (MC/DC & condition coverage).
3. Boundary value analysis on included print counts, copy limits, file sizes,
   extra-copy thresholds (> 50), and dispatch cutoff intervals.
4. Exception paths and error states.
"""

import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ============================================================================
# 1. extra_print_charge() - Decision & Branch Coverage
# ============================================================================

class TestExtraPrintChargeBranches:
    """Branch and decision coverage for extra_print_charge()."""

    # --- Decision: print_size not in INCLUDED_PRINTS ---
    def test_invalid_print_size_branch_true(self):
        """Branch TRUE: unknown print size raises ValueError."""
        with pytest.raises(ValueError, match="unknown print size"):
            extra_print_charge("poster", 10, "matte", False)

    def test_invalid_print_size_branch_false(self):
        """Branch FALSE: recognized print size proceeds past size check."""
        # Using a valid size and negative copies confirms it passed size check
        with pytest.raises(ValueError, match="invalid copies"):
            extra_print_charge("4x6", -1, "matte", False)

    # --- Decision: copies < 0 ---
    def test_negative_copies_branch_true(self):
        """Branch TRUE: negative copies raises ValueError."""
        with pytest.raises(ValueError, match="invalid copies"):
            extra_print_charge("5x7", -5, "matte", False)

    def test_negative_copies_branch_false_zero(self):
        """Branch FALSE: copies == 0 is valid and returns 0 charge."""
        assert extra_print_charge("5x7", 0, "matte", False) == 0

    # --- Compound Decision: is_member and print_size != "8x10" ---
    # Condition 1: is_member (T/F), Condition 2: print_size != "8x10" (T/F)

    def test_member_and_not_8x10_true_true_4x6(self):
        """T & T: is_member=True, size='4x6' -> included is 20 + 5 = 25."""
        # Exactly 25 copies -> extra = 0 -> 0 charge
        assert extra_print_charge("4x6", 25, "matte", True) == 0
        # 26 copies -> extra = 1 -> charge = 1 * 4 = 4
        assert extra_print_charge("4x6", 26, "matte", True) == 4

    def test_member_and_not_8x10_true_true_5x7(self):
        """T & T: is_member=True, size='5x7' -> included is 15 + 5 = 20."""
        # Exactly 20 copies -> extra = 0 -> 0 charge
        assert extra_print_charge("5x7", 20, "matte", True) == 0
        # 21 copies -> extra = 1 -> charge = 1 * 4 = 4
        assert extra_print_charge("5x7", 21, "matte", True) == 4

    def test_member_and_8x10_true_false(self):
        """T & F: is_member=True, size='8x10' -> NO bonus (+0), included remains 10."""
        # Exactly 10 copies -> extra = 0 -> 0 charge
        assert extra_print_charge("8x10", 10, "matte", True) == 0
        # 11 copies -> extra = 1 -> charge = 1 * 4 = 4
        assert extra_print_charge("8x10", 11, "matte", True) == 4

    def test_non_member_and_not_8x10_false_true(self):
        """F & T: is_member=False, size='4x6' -> included remains 20."""
        assert extra_print_charge("4x6", 20, "matte", False) == 0
        assert extra_print_charge("4x6", 21, "matte", False) == 4

    def test_non_member_and_8x10_false_false(self):
        """F & F: is_member=False, size='8x10' -> included remains 10."""
        assert extra_print_charge("8x10", 10, "matte", False) == 0
        assert extra_print_charge("8x10", 11, "matte", False) == 4

    # --- Decision: extra <= 0 ---
    def test_extra_less_than_zero(self):
        """Branch TRUE (strictly less): copies < included -> returns 0."""
        assert extra_print_charge("4x6", 10, "matte", False) == 0

    def test_extra_equal_zero_boundary(self):
        """Branch TRUE (boundary == 0): copies == included -> returns 0."""
        assert extra_print_charge("4x6", 20, "matte", False) == 0

    def test_extra_greater_than_zero_boundary(self):
        """Branch FALSE (boundary extra == 1): copies == included + 1."""
        assert extra_print_charge("4x6", 21, "matte", False) == 4

    # --- Decision: finish == "matte" ---
    def test_finish_matte_branch_true(self):
        """Branch TRUE: finish is 'matte' -> rate = 4."""
        # extra = 10, rate = 4 -> 40
        assert extra_print_charge("4x6", 30, "matte", False) == 40

    def test_finish_glossy_branch_false(self):
        """Branch FALSE: finish is 'glossy' -> rate = 7."""
        # extra = 10, rate = 7 -> 70
        assert extra_print_charge("4x6", 30, "glossy", False) == 70

    def test_finish_canvas_under_50_branch_false(self):
        """Branch FALSE: finish is 'canvas' (extra <= 50) -> rate = 7."""
        # extra = 10, rate = 7 -> 70
        assert extra_print_charge("4x6", 30, "canvas", False) == 70

    # --- Decision: extra > 50 ---
    def test_extra_boundary_50_branch_false(self):
        """Branch FALSE (boundary extra == 50): rate not increased."""
        # included = 20, copies = 70 -> extra = 50. rate = 4 -> 200
        assert extra_print_charge("4x6", 70, "matte", False) == 200

    def test_extra_boundary_51_branch_true_matte(self):
        """Branch TRUE (boundary extra == 51, matte): rate increases to 4 + 2 = 6."""
        # included = 20, copies = 71 -> extra = 51. rate = 6 -> 306
        assert extra_print_charge("4x6", 71, "matte", False) == 306

    def test_extra_over_50_branch_true_glossy(self):
        """Branch TRUE (extra > 50, glossy): rate increases to 7 + 2 = 9."""
        # included = 15, copies = 75 -> extra = 60. rate = 9 -> 540
        assert extra_print_charge("5x7", 75, "glossy", False) == 540

    # --- Decision: finish == "canvas" (when extra > 50) ---
    def test_extra_over_50_canvas_branch_true(self):
        """Branch TRUE: extra > 50 AND finish == 'canvas' -> rate = 7 + 2 + 5 = 14."""
        # included = 10, copies = 70 -> extra = 60. rate = 14 -> 840
        assert extra_print_charge("8x10", 70, "canvas", False) == 840

    def test_extra_over_50_non_canvas_branch_false(self):
        """Branch FALSE: extra > 50 AND finish != 'canvas' -> rate not +5."""
        # included = 10, copies = 70 -> extra = 60. finish = 'lustre' -> rate = 9 -> 540
        assert extra_print_charge("8x10", 70, "lustre", False) == 540


# ============================================================================
# 2. order_valid() - Decision & Boundary Coverage
# ============================================================================

class TestOrderValidBranches:
    """Branch and boundary coverage for order_valid()."""

    # --- Decision: is_rush ---
    def test_rush_valid_at_boundary_50(self):
        """Branch is_rush TRUE, copies == 50 -> True."""
        assert order_valid(10, 50, True) is True

    def test_rush_valid_below_boundary(self):
        """Branch is_rush TRUE, copies < 50 -> True."""
        assert order_valid(10, 1, True) is True

    def test_rush_invalid_at_boundary_51(self):
        """Branch is_rush TRUE, copies == 51 -> False."""
        assert order_valid(10, 51, True) is False

    def test_rush_ignores_large_file_size(self):
        """Branch is_rush TRUE, file_mb > 25 but copies <= 50 -> still True."""
        assert order_valid(100, 30, True) is True

    # --- Regular Order (is_rush FALSE) -> Decision: file_mb > 25 ---
    def test_regular_file_mb_boundary_25_accepted(self):
        """Branch file_mb > 25 FALSE (boundary == 25) -> proceeds to copy check."""
        assert order_valid(25, 200, False) is True

    def test_regular_file_mb_boundary_25_point_1_rejected(self):
        """Branch file_mb > 25 TRUE (boundary == 25.1) -> returns False."""
        assert order_valid(25.1, 100, False) is False

    def test_regular_file_mb_large_rejected(self):
        """Branch file_mb > 25 TRUE (file_mb = 50) -> returns False."""
        assert order_valid(50, 10, False) is False

    # --- Regular Order -> Decision: copies <= 500 ---
    def test_regular_copies_boundary_500_accepted(self):
        """copies <= 500 TRUE (boundary == 500) -> returns True."""
        assert order_valid(20, 500, False) is True

    def test_regular_copies_boundary_501_rejected(self):
        """copies <= 500 FALSE (boundary == 501) -> returns False."""
        assert order_valid(20, 501, False) is False

    def test_regular_copies_nominal_accepted(self):
        """copies <= 500 TRUE (nominal value 100) -> returns True."""
        assert order_valid(10, 100, False) is True


# ============================================================================
# 3. dispatch_status() - Decision, Cutoff & Interval Coverage
# ============================================================================

class TestDispatchStatusBranches:
    """Branch and boundary coverage for dispatch_status()."""

    # --- All 4 Combinations of (is_framed, is_international) ---
    # Unframed + Domestic: Cutoff = 12
    # Framed + Domestic: Cutoff = 24
    # Unframed + International: Cutoff = 12 + 24 = 36
    # Framed + International: Cutoff = 24 + 24 = 48

    @pytest.mark.parametrize("hours, expected", [
        (15, "on_time"),   # hours > cutoff
        (12, "on_time"),   # boundary: hours == cutoff (12)
        (11.9, "tight"),   # boundary: just below cutoff
        (6, "tight"),      # boundary: hours == cutoff - 6 (6)
        (5.9, "missed"),   # boundary: just below cutoff - 6
        (0, "missed"),     # well below cutoff - 6
    ])
    def test_unframed_domestic_all_intervals(self, hours, expected):
        """Test unframed domestic order (cutoff = 12) across all boundary intervals."""
        assert dispatch_status(hours, is_framed=False, is_international=False) == expected

    @pytest.mark.parametrize("hours, expected", [
        (30, "on_time"),   # hours > cutoff
        (24, "on_time"),   # boundary: hours == cutoff (24)
        (23.5, "tight"),   # boundary: just below cutoff
        (18, "tight"),     # boundary: hours == cutoff - 6 (18)
        (17.5, "missed"),  # boundary: just below cutoff - 6
        (5, "missed"),     # well below cutoff - 6
    ])
    def test_framed_domestic_all_intervals(self, hours, expected):
        """Test framed domestic order (cutoff = 24) across all boundary intervals."""
        assert dispatch_status(hours, is_framed=True, is_international=False) == expected

    @pytest.mark.parametrize("hours, expected", [
        (40, "on_time"),   # hours > cutoff
        (36, "on_time"),   # boundary: hours == cutoff (36)
        (35.5, "tight"),   # boundary: just below cutoff
        (30, "tight"),     # boundary: hours == cutoff - 6 (30)
        (29.5, "missed"),  # boundary: just below cutoff - 6
        (10, "missed"),    # well below cutoff - 6
    ])
    def test_unframed_international_all_intervals(self, hours, expected):
        """Test unframed international order (cutoff = 36) across all boundary intervals."""
        assert dispatch_status(hours, is_framed=False, is_international=True) == expected

    @pytest.mark.parametrize("hours, expected", [
        (50, "on_time"),   # hours > cutoff
        (48, "on_time"),   # boundary: hours == cutoff (48)
        (47.5, "tight"),   # boundary: just below cutoff
        (42, "tight"),     # boundary: hours == cutoff - 6 (42)
        (41.5, "missed"),  # boundary: just below cutoff - 6
        (1, "missed"),     # well below cutoff - 6
    ])
    def test_framed_international_all_intervals(self, hours, expected):
        """Test framed international order (cutoff = 48) across all boundary intervals."""
        assert dispatch_status(hours, is_framed=True, is_international=True) == expected

