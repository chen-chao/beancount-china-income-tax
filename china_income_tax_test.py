#!/usr/bin/env python3

import unittest

from beancount import loader
from beancount.core.number import ZERO, D
from beancount.parser import printer

from china_income_tax import calc_tax, ChinaIncomeTaxError

class ChinaIncomeTaxUnitTest(unittest.TestCase):
    def test_calc_tax(self):
        self.assertAlmostEqual(calc_tax(0), ZERO)
        self.assertAlmostEqual(calc_tax(144000), D(11880))
        self.assertAlmostEqual(calc_tax(412345), D(71166.25))
        self.assertAlmostEqual(calc_tax(2000000), D(718080))

    @loader.load_doc()
    def test_china_income_tax_success(self, entries, errors, options_map):
        '''
        plugin "china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"

        1970-01-01 open Income:Salary
          category: "china-income-tax"
        1970-01-01 open Income:Allowance
          category: "china-income-tax"
        1970-01-01 open Expenses:Pension
          category: "china-income-tax"
        1970-01-01 open Assets:BankCard
        1970-01-01 open Expenses:IncomeTax:2022

        2022-01-31 * "salary"
          category: "china-income-tax"
          tax-deduction: -1000
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   1005 CNY
          Assets:BankCard
        '''

        printer.print_errors(errors)
        self.assertEqual([], errors)

    @loader.load_doc(expect_errors=True)
    def test_china_income_tax_fail(self, entries, errors, options_map):
        '''
        plugin "china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"

        1970-01-01 open Income:Salary
          category: "china-income-tax"
        1970-01-01 open Income:Allowance
          category: "china-income-tax"
        1970-01-01 open Expenses:Pension
          category: "china-income-tax"
        1970-01-01 open Assets:BankCard
        1970-01-01 open Expenses:IncomeTax:2022

        2022-01-31 * "salary"
          category: "china-income-tax"
          tax-deduction: -3300
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                    400 CNY
          Assets:BankCard
        '''

        self.assertEqual([ChinaIncomeTaxError], list(map(type, errors)))

    @loader.load_doc()
    def test_china_income_tax_multiple_month(self, entries, errors, options_map):
        '''
        plugin "china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"

        1970-01-01 open Income:Salary
          category: "china-income-tax"
        1970-01-01 open Income:Allowance
          category: "china-income-tax"
        1970-01-01 open Expenses:Pension
          category: "china-income-tax"
        1970-01-01 open Assets:BankCard
        1970-01-01 open Expenses:IncomeTax:2022

        2022-01-31 * "salary"
          category: "china-income-tax"
          tax-deduction: -1000
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   1005 CNY
          Assets:BankCard

        2022-02-28 * "salary"
          category: "china-income-tax"
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   3275 CNY
          Assets:BankCard
        '''

        printer.print_errors(errors)
        self.assertEqual([], errors)

    @loader.load_doc()
    def test_china_income_tax_orderless(self, entries, errors, options_map):
        '''
        plugin "china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"

        1970-01-01 open Income:Salary
          category: "china-income-tax"
        1970-01-01 open Income:Allowance
          category: "china-income-tax"
        1970-01-01 open Expenses:Pension
          category: "china-income-tax"
        1970-01-01 open Assets:BankCard
        1970-01-01 open Expenses:IncomeTax:2022

        2022-02-28 * "salary"
          category: "china-income-tax"
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   3275 CNY
          Assets:BankCard

        2022-01-31 * "salary"
          category: "china-income-tax"
          tax-deduction: -1000
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   1005 CNY
          Assets:BankCard
        '''

        printer.print_errors(errors)
        self.assertEqual([], errors)

    @loader.load_doc()
    def test_china_income_tax_skip_month(self, entries, errors, options_map):
        '''
        plugin "china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"

        1970-01-01 open Income:Salary
          category: "china-income-tax"
        1970-01-01 open Income:Allowance
          category: "china-income-tax"
        1970-01-01 open Expenses:Pension
          category: "china-income-tax"
        1970-01-01 open Assets:BankCard
        1970-01-01 open Expenses:IncomeTax:2022

        2022-01-31 * "salary"
          category: "china-income-tax"
          tax-deduction: -1000
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   1005 CNY
          Assets:BankCard

        2022-03-31 * "salary"
          category: "china-income-tax"
          Income:Allowance                          -500 CNY
          Income:Salary                           -40000 CNY
          Expenses:Pension                          1000 CNY
          Expenses:IncomeTax:2022                   3275 CNY
          Assets:BankCard
        '''

        printer.print_errors(errors)
        self.assertEqual([], errors)

if __name__ == '__main__':
    unittest.main()
