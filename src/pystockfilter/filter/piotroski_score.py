# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
from pystockfilter.filter.base_filter import BaseFilter


class PiotroskiScore(BaseFilter):
    """
    Piotroski Score Implementation
    https://en.wikipedia.org/wiki/Piotroski_F-Score
    """

    NAME = "PiotroskiScore"

    def __init__(self, arguments, logger: logging.Logger):
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = None
        super(PiotroskiScore, self).__init__(arguments, logger)

    def __calculate_net_income(self):
        return self.stock.get_data_attr("income", "netIncome")

    def __calculate_roa(self):
        net_income = self.stock.get_data_attr("income", "netIncome")
        total_assets = self.stock.get_data_attr("balance", "totalAssets")
        net_income_prev = self.stock.get_data_attr("income", "netIncome",
                                                   quarter_diff=4)
        total_assets_prev = self.stock.get_data_attr("balance", "totalAssets",
                                                     quarter_diff=4)
        return net_income / total_assets, net_income_prev / total_assets_prev

    def __calculate_operating_cashflow(self):
        return self.stock.get_data_attr("cash", "cashFromOper")

    def __calculate_debtassetratio(self):
        ltd = self.stock.get_data_attr("balance", "longTermDebt")
        total_assets = self.stock.get_data_attr("balance", "totalAssets")
        ltd_prev = self.stock.get_data_attr("balance",
                                            "longTermDebt",
                                            quarter_diff=4)
        total_assets_prev = self.stock.get_data_attr("balance", "totalAssets",
                                                                quarter_diff=4)
        return (ltd / total_assets,
                ltd_prev / total_assets_prev)

    def __calculate_current_ratio(self):
        assets = self.stock.get_data_attr("balance", "totalCurrentAssets")
        lia = self.stock.get_data_attr("balance", "totalCurrentLiabili")
        assets_prev = self.stock.get_data_attr("balance", "totalCurrentAssets",
                                               quarter_diff=4)
        lia_prev = self.stock.get_data_attr("balance", "totalCurrentLiabili",
                                            quarter_diff=4)
        return assets / lia, assets_prev / lia_prev

    def __calculate_gross_margin(self):
        total_revenue = self.stock.get_data_attr("income", "totalRevenue")
        goods = self.stock.get_data_attr("income", "costOfRevenue")
        total_revenue_prev = self.stock.get_data_attr("income", "totalRevenue",
                                                      quarter_diff=4)
        goods_prev = self.stock.get_data_attr("income", "costOfRevenue",
                                              quarter_diff=4)
        gross_margin = (total_revenue - goods) / total_revenue
        gross_margin_prev = (total_revenue_prev - goods_prev) / \
            total_revenue_prev
        return gross_margin, gross_margin_prev

    def __calculate_asset_turnover(self):
        total_revenue = self.stock.get_data_attr("income", "totalRevenue")
        total_assets = self.stock.get_data_attr("balance", "totalAssets")
        total_revenue_prev = self.stock.get_data_attr("income", "totalRevenue",
                                                      quarter_diff=4)
        total_assets_prev = self.stock.get_data_attr("balance", "totalAssets",
                                                     quarter_diff=4)
        return (total_revenue / total_assets,
                total_revenue_prev / total_assets_prev)

    def __calculate_total_shares(self):
        shares = self.stock.get_data_attr("balance", "totalSharesOutst")
        shares_prev = self.stock.get_data_attr("balance", "totalSharesOutst",
                                               quarter_diff=4)
        return shares, shares_prev

    def __calculate_profitability(self):
        piotroski = 0
        # Profitability
        # return on assets = net income / total assets
        ocf = self.__calculate_operating_cashflow()
        roa = self.__calculate_roa()
        # Positive return on assets in the current year
        if roa[0] > 0:
            self.args['pio_return_on_assets'] = 1
            piotroski += 1
        else:
            self.args['pio_return_on_assets'] = 0
            self.logger.debug("Negative return on assets")
        # Positive operating cash flow in the current year
        if ocf > 0:
            self.args['pio_operating_cash_flow'] = 1
            piotroski += 1
        else:
            self.args['pio_operating_cash_flow'] = 0
            self.logger.debug("Negative operating cash flow")
        # Cash flow from operations are greater than Net Income
        if ocf > self.__calculate_net_income():
            self.args['pio_operating_cash_flow_gt_net_income'] = 1
            piotroski += 1
        else:
            self.args['pio_operating_cash_flow_gt_net_income'] = 0
            self.logger.debug(
                "Cash flow from operations are smaller than Net Income"
            )
        # Higher return on assets (ROA) in the current period
        # compared to the ROA in the
        # previous year
        if roa[0] > roa[1]:
            self.args['pio_roa_gt_roa_last_year'] = 1
            piotroski += 1
        else:
            self.args['pio_roa_gt_roa_last_year'] = 0
            self.logger.debug(
                "Lower ROA in the current period compared to the ROA in the "
                "previous year"
            )
        return piotroski

    def __calculate_liquidity(self):
        piotroski = 0
        # Liquidity
        # long term debt / total assets
        debt_asset_ratio = self.__calculate_debtassetratio()
        # Current Ratio = Current Assets / Current Liabilities
        current_ratio = self.__calculate_current_ratio()
        sheets = self.__calculate_total_shares()
        # Lower ratio of long term debt to in the current period compared
        # value in the previous year
        if debt_asset_ratio[1] > debt_asset_ratio[0]:
            self.args['pio_lower_ratio_long_term_debt'] = 1
            piotroski += 1
        else:
            self.args['pio_lower_ratio_long_term_debt'] = 0
            self.logger.debug(
                "Higher ratio of long term debt to in the current period"
                " compared value in the previous year"
            )
        # Higher current ratio this year compared to the previous year
        if current_ratio[0] > current_ratio[1]:
            self.args['pio_higher_current_ratio'] = 1
            piotroski += 1
        else:
            self.args['pio_higher_current_ratio'] = 0
            self.logger.debug(
                "Lower current ratio this year compared to the previous year"
            )
        # No new shares were issued in the last year
        if sheets[0] >= sheets[1]:
            self.args['pio_no_new_sheets_issued'] = 1
            piotroski += 1
        else:
            self.args['pio_no_new_sheets_issued'] = 0
            self.logger.debug("New shares were issued in the last year")
        return piotroski

    def __calculate_operating_efficiency(self):
        piotroski = 0
        # gross margin % = (revenue - cost of goods sold) / revenue
        gross_margin = self.__calculate_gross_margin()
        # Asset Turnover = Revenues / Total Assets
        asset_turnover = self.__calculate_asset_turnover()

        # Operating Efficiency
        # A higher gross margin compared to the previous year
        if gross_margin[0] > gross_margin[1]:
            self.args['pio_higher_gross_margin'] = 1
            piotroski += 1
        else:
            self.args['pio_higher_gross_margin'] = 0
            self.logger.debug(
                "A lower gross margin compared to the previous year"
            )

        # A higher asset turnover ratio compared to the previous year
        if asset_turnover[0] > asset_turnover[1]:
            self.args['pio_higher_asset_turnover_ratio'] = 1
            piotroski += 1
        else:
            self.args['pio_higher_asset_turnover_ratio'] = 0
            self.logger.debug(
                "A lower asset turnover ratio compared to the previous year"
            )
        return piotroski

    def analyse(self):
        self.calc = self.__calculate_profitability() + \
                    self.__calculate_liquidity() + \
                    self.__calculate_operating_efficiency()

        return super(PiotroskiScore, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return True
