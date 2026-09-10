def calculate_repayment(principal, annual_rate, months):
    """
    Calculate an illustrative monthly repayment using
    the standard amortizing/reducing-balance formula.

    This function is deterministic:
    the same input always produces the same output.
    """

    if principal <= 0:
        raise ValueError("Principal must be greater than zero.")

    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")

    if months <= 0:
        raise ValueError("Loan term must be greater than zero.")

    monthly_rate = annual_rate / 100 / 12

    # Handle a zero-interest case
    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** months
            / ((1 + monthly_rate) ** months - 1)
        )

    total_repayment = monthly_payment * months
    total_interest = total_repayment - principal

    return {
        "principal": round(principal, 2),
        "annual_interest_rate": round(annual_rate, 2),
        "term_months": months,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_repayment, 2),
        "calculation_method": "Reducing balance / amortized payment",
        "is_illustrative": True
    }


def generate_schedule(principal, annual_rate, months):
    """
    Generate a month-by-month illustrative repayment schedule.
    """

    summary = calculate_repayment(
        principal,
        annual_rate,
        months
    )

    monthly_payment = summary["monthly_payment"]
    monthly_rate = annual_rate / 100 / 12

    balance = principal
    schedule = []

    for month in range(1, months + 1):

        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest

        # Correct final repayment for small rounding differences
        if month == months:
            principal_payment = balance
            payment = principal_payment + interest
        else:
            payment = monthly_payment

        closing_balance = balance - principal_payment

        if closing_balance < 0:
            closing_balance = 0

        schedule.append({
            "month": month,
            "opening_balance": round(balance, 2),
            "payment": round(payment, 2),
            "principal_payment": round(principal_payment, 2),
            "interest": round(interest, 2),
            "closing_balance": round(closing_balance, 2)
        })

        balance = closing_balance

    return schedule