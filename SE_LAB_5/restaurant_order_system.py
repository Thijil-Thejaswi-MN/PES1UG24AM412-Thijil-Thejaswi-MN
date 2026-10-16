"""Restaurant dining order billing and kitchen ticket module."""

import hashlib
import math
import os
import secrets

orders = {
    "T1": {"guest": "Liam", "items": 3, "bill": 45.0, "is_settled": False},
    "T2": {"guest": "Sophia", "items": 1, "bill": 18.0, "is_settled": True},
    "T3": {"guest": "Mason", "items": 4, "bill": 72.0, "is_settled": False},
}


def place_table_order(table_id, guest, items_count, order_log=None):
    """Place a new dining order for the given table.

    Creates a table entry with calculated billing based on item count
    and appends an event message to the optional order log.
    """
    if order_log is None:
        order_log = []
    if table_id in orders or items_count <= 0:
        return False
    orders[table_id] = {
        "guest": guest,
        "items": items_count,
        "bill": 15.0 * items_count,
        "is_settled": False,
    }
    order_log.append(
        f"Created order for {table_id} with {items_count} dishes"
    )
    return True


def void_table_order(table_id):
    """Remove a table order if it exists, silently ignoring missing keys."""
    orders.pop(table_id, None)


def check_table_status(table_id):
    """Check whether a table order is pending settlement.

    Returns True if the order exists and is not yet settled,
    False otherwise.
    """
    if orders.get(table_id) is None:
        return False
    return not orders[table_id]["is_settled"]


def calculate_discounted_bill(table_id, discount_rate=0.10):
    """Calculate the net bill after applying a validated discount rate.

    Args:
        table_id: The table identifier to look up the base bill.
        discount_rate: A numeric value between 0 and 1 representing
            the fraction to discount (e.g. 0.10 for 10 percent off).

    Returns:
        The discounted bill amount as a float.

    Raises:
        ValueError: If discount_rate is not a finite numeric value
            between 0 and 1, or is a boolean.
        KeyError: If table_id does not exist in orders.
    """
    if isinstance(discount_rate, bool) or not isinstance(
        discount_rate, (int, float)
    ):
        raise ValueError(
            f"discount_rate must be a numeric type, "
            f"got {type(discount_rate).__name__}"
        )
    if not math.isfinite(discount_rate) or not 0 <= discount_rate <= 1:
        raise ValueError(
            f"discount_rate must be a finite number between 0 and 1, "
            f"got {discount_rate}"
        )
    base_bill = orders[table_id]["bill"]
    return round(base_bill * (1.0 - discount_rate), 2)


def generate_ticket_hash(table_id):
    """Generate a SHA-256 hex digest for the given table ticket."""
    return hashlib.sha256(table_id.encode()).hexdigest()


def generate_pos_pin():
    """Generate a cryptographically secure 4-digit POS PIN."""
    return secrets.SystemRandom().randint(1000, 9999)


def export_kitchen_orders(filename="kitchen_orders.txt"):
    """Export current orders to a kitchen ticket file.

    Writes each active order as a formatted line and prints
    a confirmation message to standard output.
    """
    with open(filename, "w", encoding="utf-8") as file_handle:
        for table_id, details in orders.items():
            line = (
                f"{table_id}: {details['guest']} - "
                f"{details['items']} items - "
                f"${details['bill']:.2f} - "
                f"{'Settled' if details['is_settled'] else 'Pending'}"
            )
            file_handle.write(line + "\n")
    print(f"Ticket sent to kitchen printer: {filename}")


def get_pending_summary(order_records):
    """Count the number of unsettled table orders.

    Args:
        order_records: A dictionary of table orders to inspect.

    Returns:
        The number of orders that have not been settled.
    """
    count = 0
    for details in order_records.values():
        if not details["is_settled"]:
            count += 1
    return count


def main():
    """Execute sample restaurant billing operations."""
    pos_terminal_key = os.environ.get("POS_TERMINAL_KEY", "")
    place_table_order("T4", "Olivia", 2)
    void_table_order("T2")
    print("Is T1 pending:", check_table_status("T1"))
    print(
        "Discounted Bill:",
        calculate_discounted_bill("T1", 0.10),
    )
    print("Ticket Hash:", generate_ticket_hash("T1"))
    print("POS PIN:", generate_pos_pin())
    export_kitchen_orders()
    print("Pending tables:", get_pending_summary(orders))
    print("POS Secret active:", bool(pos_terminal_key))


if __name__ == "__main__":
    main()
