"""
SACCO Credit Calculation Tools

This module performs deterministic SACCO loan calculations:

1. Reducing-balance repayment schedule
2. Debt Service Ratio (DSR)
3. Savings-based loan limit
4. Security/collateral coverage
5. Guarantor coverage

The AI may select a calculation and provide inputs,
but the Python functions perform all arithmetic.

Run the API:
    python sacco_credit_calculation_tools.py

API endpoint:
    POST http://127.0.0.1:8000/calculate
"""

import calendar
import json
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP, getcontext
from wsgiref.simple_server import make_server

getcontext().prec = 28

ZERO = Decimal("0")
ONE = Decimal("1")


class ValidationError(ValueError):
    """Raised when calculation input is missing or invalid."""


def to_decimal(value, field_name, allow_zero=False):
    """
    Convert input to Decimal and validate it.
    """

    if value is None or value == "":
        raise ValidationError(f"MISSING_{field_name.upper()}")

    try:
        number = Decimal(str(value))
    except Exception:
        raise ValidationError(f"INVALID_{field_name.upper()}")

    if number < ZERO:
        raise ValidationError(f"INVALID_{field_name.upper()}")

    if number == ZERO and not allow_zero:
        raise ValidationError(f"INVALID_{field_name.upper()}")

    return number


def round_ugx(value):
    """
    Round a UGX amount to the nearest whole shilling.
    """

    return value.quantize(ONE, rounding=ROUND_HALF_UP)


def parse_date(value):
    """
    Convert YYYY-MM-DD text into a date.
    """

    if not value:
        raise ValidationError("MISSING_FIRST_REPAYMENT_DATE")

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("INVALID_FIRST_REPAYMENT_DATE")


def add_months(start_date, months_to_add):
    """
    Add months while handling month-end dates.

    Example:
    2026-10-31 plus one month becomes 2026-11-30.
    """

    month_index = start_date.month - 1 + months_to_add
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1

    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)

    return date(year, month, day)


def calculate_monthly_payment(principal, monthly_rate, number_of_payments):
    """
    Calculate the fixed monthly payment for a reducing-balance loan.

    Formula:
    Payment = P * r * (1 + r)^n / ((1 + r)^n - 1)

    P = loan principal
    r = monthly interest rate
    n = total monthly payments
    """

    if monthly_rate == ZERO:
        return principal / Decimal(number_of_payments)

    growth_factor = (ONE + monthly_rate) ** number_of_payments

    return (
        principal
        * monthly_rate
        * growth_factor
        / (growth_factor - ONE)
    )


def calculate_repayment_schedule(
    loan_amount_ugx,
    annual_interest_rate_percent,
    repayment_period_months,
    first_repayment_date,
    fees_ugx=0
):
    """
    Calculate a reducing-balance monthly repayment schedule.
    """

    principal = to_decimal(loan_amount_ugx, "loan_amount_ugx")
    annual_rate = to_decimal(
        annual_interest_rate_percent,
        "annual_interest_rate_percent",
        allow_zero=True
    )

    months = to_decimal(
        repayment_period_months,
        "repayment_period_months"
    )

    fees = to_decimal(
        fees_ugx,
        "fees_ugx",
        allow_zero=True
    )

    if months != months.to_integral_value():
        raise ValidationError("INVALID_REPAYMENT_PERIOD_MONTHS")

    if months > 360:
        raise ValidationError("INVALID_REPAYMENT_PERIOD_MONTHS")

    first_date = parse_date(first_repayment_date)

    months = int(months)

    monthly_rate = annual_rate / Decimal("1200")

    fixed_payment = round_ugx(
        calculate_monthly_payment(
            principal,
            monthly_rate,
            months
        )
    )

    balance = principal
    total_interest = ZERO
    total_installments = ZERO
    schedule = []

    for installment_number in range(1, months + 1):
        opening_balance = balance

        interest = round_ugx(
            opening_balance * monthly_rate
        )

        principal_payment = round_ugx(
            fixed_payment - interest
        )

        if principal_payment > opening_balance:
            principal_payment = opening_balance

        if installment_number == months:
            principal_payment = opening_balance

        installment_amount = round_ugx(
            principal_payment + interest
        )

        balance = round_ugx(
            opening_balance - principal_payment
        )

        due_date = add_months(
            first_date,
            installment_number - 1
        )

        schedule.append({
            "installment_number": installment_number,
            "due_date": due_date.isoformat(),
            "opening_balance_ugx": int(round_ugx(opening_balance)),
            "principal_ugx": int(round_ugx(principal_payment)),
            "interest_ugx": int(round_ugx(interest)),
            "installment_amount_ugx": int(round_ugx(installment_amount)),
            "closing_balance_ugx": int(round_ugx(balance))
        })

        total_interest += interest
        total_installments += installment_amount

    return {
        "status": "success",
        "calculation": "repayment_schedule",
        "interest_method": "reducing_balance_amortized",
        "loan_amount_ugx": int(round_ugx(principal)),
        "annual_interest_rate_percent": float(annual_rate),
        "repayment_period_months": months,
        "fees_ugx": int(round_ugx(fees)),
        "total_interest_ugx": int(round_ugx(total_interest)),
        "total_installments_ugx": int(round_ugx(total_installments)),
        "total_amount_payable_ugx": int(
            round_ugx(total_installments + fees)
        ),
        "schedule": schedule,
        "disclaimer": (
            "Illustrative calculation only. Loan officer review "
            "and Credit Committee approval are required."
        )
    }


def calculate_dsr(
    monthly_income_ugx,
    existing_monthly_debt_ugx,
    new_monthly_payment_ugx,
    allowed_dsr_percent=50,
    income_basis="net_income"
):
    """
    Calculate Debt Service Ratio.

    Formula:
    DSR = (existing monthly debt + new monthly payment)
          / monthly income * 100
    """

    income = to_decimal(
        monthly_income_ugx,
        "monthly_income_ugx"
    )

    existing_debt = to_decimal(
        existing_monthly_debt_ugx,
        "existing_monthly_debt_ugx",
        allow_zero=True
    )

    new_payment = to_decimal(
        new_monthly_payment_ugx,
        "new_monthly_payment_ugx",
        allow_zero=True
    )

    allowed_dsr = to_decimal(
        allowed_dsr_percent,
        "allowed_dsr_percent",
        allow_zero=True
    )

    total_debt = existing_debt + new_payment

    dsr_percent = (
        total_debt / income
    ) * Decimal("100")

    maximum_debt = (
        income * allowed_dsr
    ) / Decimal("100")

    remaining_capacity = maximum_debt - existing_debt

    if remaining_capacity < ZERO:
        remaining_capacity = ZERO

    return {
        "status": "success",
        "calculation": "dsr",
        "income_basis": income_basis,
        "monthly_income_ugx": int(round_ugx(income)),
        "existing_monthly_debt_ugx": int(round_ugx(existing_debt)),
        "new_monthly_payment_ugx": int(round_ugx(new_payment)),
        "total_monthly_debt_ugx": int(round_ugx(total_debt)),
        "dsr_percent": float(dsr_percent),
        "allowed_dsr_percent": float(allowed_dsr),
        "maximum_allowed_debt_ugx": int(round_ugx(maximum_debt)),
        "remaining_debt_capacity_ugx": int(
            round_ugx(remaining_capacity)
        ),
        "passes_limit": dsr_percent <= allowed_dsr,
        "formula": (
            "(existing monthly debt + new monthly payment) "
            "/ monthly income * 100"
        )
    }


def calculate_dsr_three_methods(
    gross_monthly_income_ugx,
    net_monthly_income_ugx,
    existing_monthly_debt_ugx,
    new_monthly_payment_ugx,
    gross_limit_percent=50,
    net_limit_percent=50,
    disposable_income_ugx=None,
    disposable_limit_percent=60
):
    """
    Calculate DSR using three income methods:

    1. Gross-income DSR
    2. Net-income DSR
    3. Disposable-income DSR
    """

    gross_income = to_decimal(
        gross_monthly_income_ugx,
        "gross_monthly_income_ugx"
    )

    net_income = to_decimal(
        net_monthly_income_ugx,
        "net_monthly_income_ugx"
    )

    existing_debt = to_decimal(
        existing_monthly_debt_ugx,
        "existing_monthly_debt_ugx",
        allow_zero=True
    )

    new_payment = to_decimal(
        new_monthly_payment_ugx,
        "new_monthly_payment_ugx",
        allow_zero=True
    )

    gross_limit = to_decimal(
        gross_limit_percent,
        "gross_limit_percent",
        allow_zero=True
    )

    net_limit = to_decimal(
        net_limit_percent,
        "net_limit_percent",
        allow_zero=True
    )

    disposable_limit = to_decimal(
        disposable_limit_percent,
        "disposable_limit_percent",
        allow_zero=True
    )

    total_debt = existing_debt + new_payment

    if disposable_income_ugx is None:
        disposable_income = net_income - existing_debt
    else:
        disposable_income = to_decimal(
            disposable_income_ugx,
            "disposable_income_ugx"
        )

    if disposable_income <= ZERO:
        raise ValidationError("INVALID_DISPOSABLE_INCOME_UGX")

    gross_dsr = (total_debt / gross_income) * Decimal("100")
    net_dsr = (total_debt / net_income) * Decimal("100")
    disposable_dsr = (
        total_debt / disposable_income
    ) * Decimal("100")

    return {
        "status": "success",
        "calculation": "three_dsr_methods",
        "total_monthly_debt_ugx": int(round_ugx(total_debt)),
        "gross_income_method": {
            "income_ugx": int(round_ugx(gross_income)),
            "dsr_percent": float(gross_dsr),
            "limit_percent": float(gross_limit),
            "passes_limit": gross_dsr <= gross_limit
        },
        "net_income_method": {
            "income_ugx": int(round_ugx(net_income)),
            "dsr_percent": float(net_dsr),
            "limit_percent": float(net_limit),
            "passes_limit": net_dsr <= net_limit
        },
        "disposable_income_method": {
            "income_ugx": int(round_ugx(disposable_income)),
            "dsr_percent": float(disposable_dsr),
            "limit_percent": float(disposable_limit),
            "passes_limit": disposable_dsr <= disposable_limit
        }
    }


def calculate_savings_based_limit(
    eligible_savings_ugx,
    savings_multiple,
    existing_loan_balance_ugx=0,
    requested_loan_amount_ugx=0
):
    """
    Calculate savings-based loan limit.

    Formula:
    Gross loan ceiling = eligible savings * savings multiple

    Available loan ceiling = gross loan ceiling
                             - existing loan balance
    """

    savings = to_decimal(
        eligible_savings_ugx,
        "eligible_savings_ugx"
    )

    multiple = to_decimal(
        savings_multiple,
        "savings_multiple"
    )

    existing_balance = to_decimal(
        existing_loan_balance_ugx,
        "existing_loan_balance_ugx",
        allow_zero=True
    )

    requested_amount = to_decimal(
        requested_loan_amount_ugx,
        "requested_loan_amount_ugx",
        allow_zero=True
    )

    gross_ceiling = savings * multiple

    available_ceiling = gross_ceiling - existing_balance

    if available_ceiling < ZERO:
        available_ceiling = ZERO

    return {
        "status": "success",
        "calculation": "savings_based_loan_limit",
        "eligible_savings_ugx": int(round_ugx(savings)),
        "approved_savings_multiple": float(multiple),
        "existing_loan_balance_ugx": int(
            round_ugx(existing_balance)
        ),
        "gross_loan_ceiling_ugx": int(
            round_ugx(gross_ceiling)
        ),
        "available_loan_ceiling_ugx": int(
            round_ugx(available_ceiling)
        ),
        "requested_loan_amount_ugx": int(
            round_ugx(requested_amount)
        ),
        "passes_limit": requested_amount <= available_ceiling,
        "formula": (
            "eligible savings * approved savings multiple "
            "- existing loan balance"
        )
    }


def calculate_security_coverage(
    loan_amount_ugx,
    security_items,
    minimum_coverage_percent=100
):
    """
    Calculate collateral or security coverage.

    Each security item must contain:
    name, market_value_ugx, haircut_percent

    Formula:
    Eligible security value =
    market value * (1 - haircut percent / 100)

    Coverage =
    eligible security value / loan amount * 100
    """

    loan_amount = to_decimal(
        loan_amount_ugx,
        "loan_amount_ugx"
    )

    minimum_coverage = to_decimal(
        minimum_coverage_percent,
        "minimum_coverage_percent",
        allow_zero=True
    )

    if not isinstance(security_items, list):
        raise ValidationError("INVALID_SECURITY_ITEMS")

    total_eligible_value = ZERO
    items = []

    for item in security_items:
        name = item.get("name", "Unnamed security")

        market_value = to_decimal(
            item.get("market_value_ugx"),
            "market_value_ugx"
        )

        haircut_percent = to_decimal(
            item.get("haircut_percent", 0),
            "haircut_percent",
            allow_zero=True
        )

        if haircut_percent > Decimal("100"):
            raise ValidationError("INVALID_HAIRCUT_PERCENT")

        eligible_value = (
            market_value
            * (Decimal("100") - haircut_percent)
            / Decimal("100")
        )

        eligible_value = round_ugx(eligible_value)

        total_eligible_value += eligible_value

        items.append({
            "name": name,
            "market_value_ugx": int(round_ugx(market_value)),
            "haircut_percent": float(haircut_percent),
            "eligible_value_ugx": int(eligible_value)
        })

    coverage_percent = (
        total_eligible_value / loan_amount
    ) * Decimal("100")

    return {
        "status": "success",
        "calculation": "security_coverage",
        "loan_amount_ugx": int(round_ugx(loan_amount)),
        "eligible_security_value_ugx": int(
            round_ugx(total_eligible_value)
        ),
        "coverage_percent": float(coverage_percent),
        "minimum_coverage_percent": float(minimum_coverage),
        "passes_minimum": coverage_percent >= minimum_coverage,
        "security_items": items,
        "formula": (
            "eligible security value / loan amount * 100"
        )
    }


def calculate_guarantor_coverage(
    loan_amount_ugx,
    guarantors,
    minimum_coverage_percent=100
):
    """
    Calculate guarantor coverage.

    Each guarantor must contain:
    name, approved_capacity_ugx

    Approved capacity should already consider the SACCO's
    guarantor rules, savings, existing obligations,
    and permitted guarantee amount.
    """

    loan_amount = to_decimal(
        loan_amount_ugx,
        "loan_amount_ugx"
    )

    minimum_coverage = to_decimal(
        minimum_coverage_percent,
        "minimum_coverage_percent",
        allow_zero=True
    )

    if not isinstance(guarantors, list):
        raise ValidationError("INVALID_GUARANTORS")

    total_capacity = ZERO
    guarantor_list = []

    for guarantor in guarantors:
        name = guarantor.get("name", "Unnamed guarantor")

        capacity = to_decimal(
            guarantor.get("approved_capacity_ugx"),
            "approved_capacity_ugx"
        )

        total_capacity += capacity

        guarantor_list.append({
            "name": name,
            "approved_capacity_ugx": int(
                round_ugx(capacity)
            )
        })

    coverage_percent = (
        total_capacity / loan_amount
    ) * Decimal("100")

    return {
        "status": "success",
        "calculation": "guarantor_coverage",
        "loan_amount_ugx": int(round_ugx(loan_amount)),
        "total_guarantor_capacity_ugx": int(
            round_ugx(total_capacity)
        ),
        "coverage_percent": float(coverage_percent),
        "minimum_coverage_percent": float(minimum_coverage),
        "passes_minimum": coverage_percent >= minimum_coverage,
        "guarantors": guarantor_list,
        "formula": (
            "total approved guarantor capacity / loan amount * 100"
        )
    }


def run_calculation(request):
    """
    Run a calculation using the public tool-catalogue contract.

    Request format:
    {
      "calculation_type": "debt_service_ratio",
      "inputs": {
        "net_monthly_income": 1500000,
        "existing_monthly_obligations": 200000,
        "proposed_monthly_installment": 466667
      }
    }
    """

    def failure(error):
        return {
            "calculation_successful": False,
            "error": error
        }

    try:
        if not isinstance(request, dict):
            return failure("missing_or_invalid_field: request")

        calculation_type = request.get("calculation_type")
        inputs = request.get("inputs")

        allowed_types = {
            "repayment_schedule",
            "debt_service_ratio",
            "savings_loan_limit",
            "security_coverage"
        }

        if calculation_type not in allowed_types:
            return failure("unsupported_calculation_type")

        if not isinstance(inputs, dict):
            return failure("missing_or_invalid_field: inputs")

        def required(name, allow_zero=False):
            value = inputs.get(name)
            if value is None or value == "":
                raise ValidationError(
                    f"missing_or_invalid_field: {name}"
                )
            try:
                number = Decimal(str(value))
            except Exception as error:
                raise ValidationError(
                    f"missing_or_invalid_field: {name}"
                ) from error
            if number < ZERO or (number == ZERO and not allow_zero):
                raise ValidationError(
                    f"invalid_input_value: {name}"
                )
            return value

        if calculation_type == "repayment_schedule":
            principal = required("principal")
            annual_rate = required(
                "annual_interest_rate",
                allow_zero=True
            )
            term_months = required("term_months")
            schedule = calculate_repayment_schedule(
                loan_amount_ugx=principal,
                annual_interest_rate_percent=annual_rate,
                repayment_period_months=term_months,
                first_repayment_date=inputs.get(
                    "first_repayment_date",
                    "1970-01-01"
                ),
                fees_ugx=inputs.get("fees", 0)
            )
            result = {
                "monthly_payment": schedule["schedule"][0][
                    "installment_amount_ugx"
                ],
                "total_interest": schedule["total_interest_ugx"],
                "total_repayment": schedule[
                    "total_amount_payable_ugx"
                ]
            }
            warning = (
                "term_exceeds_or_below_policy_limit"
                if not 6 <= schedule["repayment_period_months"] <= 24
                else None
            )

        elif calculation_type == "debt_service_ratio":
            result_data = calculate_dsr(
                monthly_income_ugx=required("net_monthly_income"),
                existing_monthly_debt_ugx=required(
                    "existing_monthly_obligations",
                    allow_zero=True
                ),
                new_monthly_payment_ugx=required(
                    "proposed_monthly_installment",
                    allow_zero=True
                )
            )
            result = {
                "dsr_percentage": result_data["dsr_percent"],
                "within_policy_limit": result_data["passes_limit"]
            }
            warning = None

        elif calculation_type == "savings_loan_limit":
            result_data = calculate_savings_based_limit(
                eligible_savings_ugx=required("savings_balance"),
                savings_multiple=required("multiplier_rate")
            )
            result = {
                "max_eligible_loan_amount": result_data[
                    "available_loan_ceiling_ugx"
                ]
            }
            warning = None

        else:
            loan_principal = required("loan_principal")
            pledged_security = required(
                "total_pledged_security",
                allow_zero=True
            )
            principal = Decimal(str(loan_principal))
            security = Decimal(str(pledged_security))
            coverage = (security / principal) * Decimal("100")
            result = {
                "coverage_percentage": float(coverage),
                "meets_minimum_coverage": coverage >= Decimal("100")
            }
            warning = None

        response = {
            "calculation_type": calculation_type,
            "result": result,
            "is_illustrative": True,
            "calculation_successful": True
        }
        if warning:
            response["policy_range_warning"] = warning
        return response

    except ValidationError as error:
        return failure(str(error))
    except Exception:
        return failure("calculation_error")


def json_response(start_response, status, response_body):
    """
    Return a JSON API response.
    """

    body = json.dumps(response_body).encode("utf-8")

    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body)))
    ]

    start_response(status, headers)

    return [body]


def application(environ, start_response):
    """
    Simple dependency-free API.

    Endpoint:
    POST /calculate
    """

    path = environ.get("PATH_INFO")
    method = environ.get("REQUEST_METHOD")

    if path != "/calculate":
        return json_response(
            start_response,
            "404 Not Found",
            {
                "status": "error",
                "code": "NOT_FOUND"
            }
        )

    if method != "POST":
        return json_response(
            start_response,
            "405 Method Not Allowed",
            {
                "status": "error",
                "code": "METHOD_NOT_ALLOWED"
            }
        )

    try:
        content_length = int(
            environ.get("CONTENT_LENGTH") or 0
        )

        raw_body = environ["wsgi.input"].read(
            content_length
        )

        request = json.loads(
            raw_body.decode("utf-8")
        )

        result = run_calculation(request)

        return json_response(
            start_response,
            "200 OK",
            result
        )

    except ValidationError as error:
        return json_response(
            start_response,
            "400 Bad Request",
            {
                "status": "error",
                "code": str(error)
            }
        )

    except json.JSONDecodeError:
        return json_response(
            start_response,
            "400 Bad Request",
            {
                "status": "error",
                "code": "INVALID_JSON"
            }
        )

    except Exception:
        return json_response(
            start_response,
            "503 Service Unavailable",
            {
                "status": "error",
                "code": "CALCULATION_SERVICE_UNAVAILABLE"
            }
        )


if __name__ == "__main__":
    print(
        "SACCO calculation API running at: "
        "http://127.0.0.1:8000/calculate"
    )

    server = make_server(
        "127.0.0.1",
        8000,
        application
    )

    server.serve_forever()