import math


def parse_order(text):
    """
    Parse a print order string in the format 'size:copies'.
    
    Returns:
        tuple: (size.upper(), copies) if valid.
        None: If input is invalid, malformed, non-string, or copies < 0.
    """
    if not isinstance(text, str):
        return None
    
    if text.count(':') != 1:
        return None
    
    size_str, copies_str = text.split(':')
    size_clean = size_str.strip()
    copies_clean = copies_str.strip()
    
    if not size_clean or not copies_clean:
        return None
    
    try:
        copies = int(copies_clean)
    except ValueError:
        return None
    
    if copies < 0:
        return None
    
    return size_clean.upper(), copies


def file_size_average(sizes_csv):
    """
    Calculate the integer floor average of file sizes provided as a CSV string.
    
    Returns:
        int: sum(sizes) // len(sizes) if valid.
        None: If input is invalid, empty, contains non-integers, or negative sizes.
    """
    if not isinstance(sizes_csv, str):
        return None
    
    cleaned = sizes_csv.strip()
    if not cleaned:
        return None
    
    tokens = cleaned.split(',')
    if not tokens:
        return None
    
    values = []
    for token in tokens:
        t = token.strip()
        if not t:
            return None
        try:
            val = int(t)
        except ValueError:
            return None
        if val < 0:
            return None
        values.append(val)
    
    if not values:
        return None
    
    return sum(values) // len(values)


def payable_amount(text):
    """
    Calculate the payable amount with 18% tax and discount: max(amount * 1.18 - discount, 0).
    
    Returns:
        float: Payable amount if valid.
        None: If input is invalid, malformed, non-numeric, non-finite (NaN/inf),
              negative, or results in calculated floating-point overflow.
    """
    if not isinstance(text, str):
        return None
    
    if text.count('|') != 1:
        return None
    
    amount_str, discount_str = text.split('|')
    amount_clean = amount_str.strip()
    discount_clean = discount_str.strip()
    
    if not amount_clean or not discount_clean:
        return None
    
    try:
        amount = float(amount_clean)
        discount = float(discount_clean)
    except ValueError:
        return None
    
    if not math.isfinite(amount) or not math.isfinite(discount):
        return None
    
    if amount < 0 or discount < 0:
        return None
    
    total = amount * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0.0)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter print size:copies (e.g. 4x6:25): ")
    result = parse_order(user_input)
    print("Size and Copies:", result)

    print("\n==== Running file_size_average ====")
    user_input = input("Enter file sizes in MB as CSV (e.g. 4,8,12): ")
    result = file_size_average(user_input)
    print("Average File Size:", result)

    print("\n==== Running payable_amount ====")
    user_input = input("Enter amount|discount (e.g. 450|50): ")
    result = payable_amount(user_input)
    print("Payable Amount:", result)


if __name__ == "__main__":
    main()
