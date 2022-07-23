#!/usr/bin/env python3

from collections import namedtuple, defaultdict
from decimal import Decimal
from math import inf

from beancount.core import data
from beancount.core.number import ZERO, D
from beancount.core import getters

__plugins__ = ('china_income_tax',)

ChinaIncomeTaxError = namedtuple('ChinaIncomeTaxError', 'source message entry')

# tax form
TAX_ROW = namedtuple('TAX_ROW', ['level', 'rate', 'deduction'])
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
DEFAULT_PRECISE = '0.01'
TAX_DEDUCTION = 'tax-deduction'

def china_income_tax(entries, options_map, config):
    """calculate income tax from beancount transactions"""

    errors = []
    taxable_accounts = set()
    taxable_transactions = []

    # configs
    config = get_config(config)
    category = config['category']
    tax_account = config['account']
    monthly_deduction = config.get('monthly-deduction', DEFAULT_MONTHLY_DEDUCTION)
    precise = D(config.get('precise', DEFAULT_PRECISE))

    # process beancount threads
    for e in entries:
        if e.meta.get('category', None) == category:
            if isinstance(e, data.Open):
                taxable_accounts.add(e.account)

            if isinstance(e, data.Transaction):
                taxable_transactions.append(e)

    # yearly accumulated tax calculation
    acc_income = defaultdict(lambda: ZERO)
    acc_tax = defaultdict(lambda: ZERO)

    # transactions are guaranteed sorted
    for t in taxable_transactions:
        year = t.date.year
        month = t.date.month

        deduction = monthly_deduction + t.meta.get(TAX_DEDUCTION, ZERO)
        income = ZERO
        tax = ZERO
        for p in t.postings:
            if p.account in taxable_accounts:
                income += p.units.number

            if p.account.startswith(tax_account):
                tax += p.units.number

        acc_current = acc_income[year] + (deduction - income)
        tax_calculated = calc_tax(acc_current) - acc_tax[year]
        acc_income[year] = acc_current
        acc_tax[year] += tax

        if (tax_calculated.quantize(precise) != tax.quantize(precise)):
            errors.append(
                ChinaIncomeTaxError(
                    t.meta,
                    f'income tax does not match, calculated: {tax_calculated:.2f}, actual: {tax:.2f}',
                    t))

    return entries, errors


def get_config(config):
    """get key value pair from beancount plugin options"""
    d = {}
    if config:
        for opt in config.split(','):
            k, v = opt.split('=')
            d[k] = v

    return d


def calc_tax(amount):
    """calculat tax according to the table"""
    if amount <= 0:
        return ZERO

    for t in TAX_TABLE:
        if amount < t.level:
            return amount * t.rate - t.deduction

    raise InvalidArgumentException(
        f'calc_tax: invalid tax rate for {amount}. should not reach here')
