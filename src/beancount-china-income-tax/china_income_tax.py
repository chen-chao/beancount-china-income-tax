#!/usr/bin/env python3

from collections import namedtuple, defaultdict
from decimal import Decimal
from math import inf

from beancount.core import data
from beancount.core.number import ZERO, D
from beancount.core import getters

__plugins__ = ("china_income_tax",)

ChinaIncomeTaxError = namedtuple("ChinaIncomeTaxError", "source message entry")

# tax form
TAX_ROW = namedtuple("TAX_ROW", ["level", "rate", "deduction"])
TAX_TABLE = [
    TAX_ROW(D(36000), D(0.03), ZERO),
    TAX_ROW(D(144000), D(0.10), D(2520)),
    TAX_ROW(D(300000), D(0.20), D(16920)),
    TAX_ROW(D(420000), D(0.25), D(31920)),
    TAX_ROW(D(660000), D(0.30), D(52920)),
    TAX_ROW(D(960000), D(0.35), D(85920)),
    TAX_ROW(D(inf), D(0.45), D(181920)),
]

# constants
DEFAULT_MONTHLY_DEDUCTION = D(-5000)
DEFAULT_PRECISION = "0.01"
TAX_DEDUCTION = "tax-deduction"


def china_income_tax(entries, options_map, config):
    """calculate income tax from beancount transactions"""

    errors = []
    taxable_accounts = set()
    taxable_transactions = []

    # configs
    config = get_config(config)
    category = config["category"]
    tax_account = config["account"]
    monthly_deduction = config.get(
        "monthly-deduction", DEFAULT_MONTHLY_DEDUCTION
    )
    precision = D(config.get("precision", DEFAULT_PRECISION))

    # process beancount threads
    for e in entries:
        if e.meta.get("category", None) == category:
            if isinstance(e, data.Open):
                taxable_accounts.add(e.account)

            if isinstance(e, data.Transaction):
                taxable_transactions.append(e)

    # yearly accumulated tax calculation
    cum_income = defaultdict(lambda: ZERO)
    cum_tax_paid = defaultdict(lambda: ZERO)

    # transactions are guaranteed sorted
    for t in taxable_transactions:
        year = t.date.year

        deduction = monthly_deduction + D(t.meta.get(TAX_DEDUCTION, 0))
        income = ZERO
        tax = ZERO
        taxed_accounts = []
        for p in t.postings:
            if p.account in taxable_accounts:
                income += p.units.number
                taxed_accounts.append(p.account)

            if p.account.startswith(tax_account):
                tax += p.units.number

        cur_taxable_income = deduction - income
        cum_taxable_income = cum_income[year] + cur_taxable_income
        cum_tax_payable = calc_tax(cum_taxable_income)
        tax_expected = cum_tax_payable - cum_tax_paid[year]

        cum_income[year] = cum_taxable_income
        cum_tax_paid[year] += tax

        if tax_expected.quantize(precision) != tax.quantize(precision):
            tax_level = get_tax_level(cum_taxable_income)
            errors.append(
                ChinaIncomeTaxError(
                    t.meta,
                    (
                        f"Income tax does not match. Diagnostics:\n"
                        f"Cumulative taxable income: {cum_taxable_income:.2f}, \n"
                        f"Current income: {income:.2f} ({', '.join(taxed_accounts)}), \n"
                        f"Current taxable income: {cur_taxable_income:.2f} (deduction: {deduction: .2f}), \n"
                        f"Tax rate: {tax_level.rate}\n"
                        f"Tax quick deduction: {tax_level.deduction}\n"
                        f"Cumulative tax payable: {cum_tax_payable:.2f}, "
                        f"Cumulative tax paid: {cum_tax_paid[year]:.2f}, "
                        f"Tax (Expected): {tax_expected:.2f}, \n"
                        f"Tax (Actual): {tax: .2f}"
                    ),
                    t,
                )
            )

    return entries, errors


def get_config(config):
    """get key value pair from beancount plugin options"""
    d = {}
    if config:
        for opt in config.split(","):
            k, v = opt.split("=")
            d[k] = v

    return d

def get_tax_level(amount) -> TAX_ROW:
    """get tax level according to the amount"""
    assert amount >= 0, "amount should be non-negative"

    for t in TAX_TABLE:
        if amount < t.level:
            return t

def calc_tax(amount) -> Decimal:
    """calculat tax according to the table"""
    tax_level = get_tax_level(amount)
    return amount * tax_level.rate - tax_level.deduction
