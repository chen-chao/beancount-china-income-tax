本插件用于 [beancount](https://github.com/beancount/beancount) 计算每
月所应缴纳的中华人民共和国个人所得税. 如计算金额与实际缴纳额度不同,
`bean-check` 或 `beancount-fava` 会显示 error.

## 税表和扣除项目

插件所使用税表来自
[中华人民共和国个人所得税法](http://www.chinatax.gov.cn/chinatax/n810219/n810744/n3752930/n3752974/c3970366/content.html)
所附
[附件1：个人所得税税率表（综合所得适用）.pdf](http://www.chinatax.gov.cn/chinatax/n363/c5161493/5161493/files/%E9%99%84%E4%BB%B61%EF%BC%9A%E4%B8%AA%E4%BA%BA%E6%89%80%E5%BE%97%E7%A8%8E%E7%A8%8E%E7%8E%87%E8%A1%A8%EF%BC%88%E7%BB%BC%E5%90%88%E6%89%80%E5%BE%97%E9%80%82%E7%94%A8%EF%BC%89.pdf)

| 级数 | 年应纳税所得额               | 税率（%） | 速算扣除数 |
|------|------------------------------|-----------|------------|
| 1    | 不超过36000元的              | 3         | 0          |
| 2    | 超过36000元至144000元的部分  | 10        | 2520       |
| 3    | 超过144000元至300000元的部分 | 20        | 16920      |
| 4    | 超过300000元至420000元的部分 | 25        | 31920      |
| 5    | 超过420000元至660000元的部分 | 30        | 52920      |
| 6    | 超过660000元至960000元的部分 | 35        | 85920      |
| 7    | 超过960000元的部分           | 45        | 181920     |


根据
[2006第07期-基本养老保险, 基本医疗保险费, 失业保险费, 住房公积金免征个人所得税](http://www.chinatax.gov.cn/n810341/n810765/n812183/n812846/c1197169/content.html)
及
[个人所得税专项附加扣除暂行办法](http://www.chinatax.gov.cn/chinatax/n810219/n810744/n3752930/n3752974/c3963375/content.html),
纳税人可享有相应扣除项目, 可在本插件中指定扣除账户或扣除额度.


## 使用方法

beancount 插件的工作流程和使用方法可参考 [Beancount Scripting & Plugins](https://beancount.github.io/docs/beancount_scripting_plugins.html).
最简单的方法是 `pip install beancount-china-income-tax`, 然后在 beanount 里指定

```
plugin "beancount-china-income-tax.china_income_tax" "category=china-income-tax,account=Expenses:IncomeTax"
```

在参与所得税计算的 beancount 账户和 transaction 下指定
`category:china-income-tax`, 如:

```
1970-01-01 open Income:Salary
  category: "china-income-tax"
1970-01-01 open Income:Allowance
  category: "china-income-tax"
1970-01-01 open Expenses:Pension
  category: "china-income-tax"
```

可在 transaction thread 下用 tax-deduction 修正税款计算, 如下面的示例
中 `tax-deduction: -3300`. 负数为扣除, 正数为增加 (如有未记录的额外收益时).

```
2022-01-31 * "salary"
  category: "china-income-tax"
  tax-deduction: -3300
  Income:Allowance                          -500 CNY
  Income:Salary                           -40000 CNY
  Expenses:Pension                          1000 CNY
  Expenses:IncomeTax:2022                 410.41 CNY
  Assets:BankCard
```

本插件会根据相应账户收支及指定的扣除来计算应纳税额. 如果
`Expenses:IncomeTax:2022` 的税款与插件计算不符, `beancount-fava` 会显示

```
income tax does not match, calculated: 1005.00, actual: 410.41
```


### 设置选项

| option            | 分类                      | 用途                                      | 是否必需? | 示例                       |
|-------------------|---------------------------|-------------------------------------------|-----------|----------------------------|
| category          | plugin/transaction option | 指定参与本插件计算的账户和 transaction    | 是        | category=china-income-tax  |
| account           | plugin option             | 税款账户前缀                              | 是        | account=Expenses:IncomeTax |
| monthly-deduction | plugin option             | 每月的修正额度, 默认为 -5000, 正数为增加  | 否        | monthly-deduction=-5000    |
| precise           | plugin option             | 税款账户比较精度, 默认为 0.01             | 否        | precise=0.01               |
| tax-deduction     | transaction option        | 指定 transaction 的税款计算修正, 默认为 0 | 否        | tax-deduction: -1100       |
