# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta

from pystockfilter.filter.base_filter import BaseFilter
from pystockfilter.filter.stock_is_hot import StockIsHot as Sih


class LevermannScore(BaseFilter):
    """
    Implementation of Levermann Score
    """

    NAME = "LevermannScore"

    def __init__(self, arguments: dict, logger: logging.Logger):
        super(LevermannScore, self).__init__(arguments, logger)
        self.buy = arguments['args']['threshold_buy']
        self.sell = arguments['args']['threshold_sell']
        self.lookback = arguments['args']['lookback']

    @staticmethod
    def calculate_trendsrating(datas):
        """
        Calculates the analysts rating ala Levermann
        :param datas: analysts data
        :return: the rating score
        """
        nominator = 0
        denominator = 0
        for data in datas:
            nominator += data['Recommendation']*data['NumberOfAnalysts']
            denominator += data['NumberOfAnalysts']
        return nominator / denominator

    def __calculate_shareholders_equity(self):
        total_assets = self.stock.get_data_attr("balance", "totalAssets")
        current_liabilities = self.stock.get_data_attr("balance",
                                                       "totalCurrentLiabili")
        if total_assets and current_liabilities:
            shareholders_equity = total_assets - current_liabilities
            return shareholders_equity
        return 0

    def __calculate_roe(self):
        net_income = self.stock.get_data_attr("income", "netIncome")
        shareholders_equity = self.__calculate_shareholders_equity()
        roe = 0
        if shareholders_equity != 0:
            roe = net_income / shareholders_equity
        return roe

    def __calculate_ebit_margin(self):
        net_income_before_taxes = self.stock.get_data_attr("income",
                                                           "netBeforeTaxes")
        ac_dep = self.stock.get_data_attr("balance", "accumulatedDepreciation")
        total_revenue = self.stock.get_data_attr("income", "totalRevenue")
        ebit_margin = 0
        if total_revenue > 0:
            ebit_margin = (net_income_before_taxes - ac_dep) / total_revenue
        return ebit_margin

    def __calculate_shareholders_equity_ratio(self):
        total_assets = self.stock.get_data_attr("balance", "totalAssets")
        ser = 0
        if total_assets > 0:
            ser = self.__calculate_shareholders_equity() / total_assets
        return ser

    def __calculate_eps_avg(self, years=5):
        eps_counter = 0
        eps_n = 0
        for idx in range(0, years):
            eps_annual = self.stock.get_data_attr("income",
                                                  "dilutedEpsExtraOrd",
                                                  annual=True,
                                                  quarter_diff=idx * 4)
            if eps_annual != -1:
                eps_n += eps_annual
                eps_counter += 1
        if eps_counter == 0:
            return -1
        eps_n /= eps_counter
        return eps_n

    def __calculate_price_earnings_ratios(self):
        eps_estimate = self.stock.get_data_attr("recommendation", "eps")
        close_prices = self.bars[:, 0]
        last_close = close_prices[-1]
        eps_avg = self.__calculate_eps_avg()
        if eps_estimate > 0 and eps_avg > 0:
            per = last_close / eps_estimate
            per_5 = last_close / eps_avg
            return [per, per_5]
        return None

    def __calculate_impact_of_quartly_figures(self):
        # index values
        last_quart = self.stock.get_data("income")
        if last_quart:
            last_quart = last_quart[0]['reportDate']
        else:
            return -1
        # get index by report date
        last_quart = last_quart.split('T00')[0]
        # report date provided by fundamentals looks not accurate
        last_quart = datetime.strptime(last_quart, '%Y-%m-%d')
        idx_index_last_quart = np.where(self.index_bars[:, 5] <
                                        np.datetime64(last_quart))[0][-1]
        idx_stock_last_quart = np.where(self.bars[:, 5] <
                                        np.datetime64(last_quart))[0][-1]
        vals_stock_last_quart = self.bars[[idx_stock_last_quart,
                                           idx_stock_last_quart - 1]]
        vals_index_last_quart = self.index_bars[[idx_index_last_quart,
                                                 idx_index_last_quart - 1]]
        perf_quart_index_prc = 100 * (vals_index_last_quart[1][0] -
                                      vals_index_last_quart[0][0]) /\
            vals_index_last_quart[1][0]
        perf_quart_stock_prc = 100 * (vals_stock_last_quart[1][0] -
                                      vals_stock_last_quart[0][0]) / \
            vals_stock_last_quart[1][0]
        perf_quart = perf_quart_stock_prc - perf_quart_index_prc
        return perf_quart

    def __calculate_rating_differences_in_percent(self):
        rating = self.calculate_trendsrating(
            self.stock.get_data("recommendation")
            ['trends'][0]['distributionList']
        )
        rating_4w = self.calculate_trendsrating(
            self.stock.get_data("recommendation")
            ['trends'][2]['distributionList'])
        rating_dif_prc = 100 * (rating_4w - rating) / rating
        return rating_dif_prc

    def __calculate_performance(self):
        close_prices = self.bars[:, 0]
        close_6m = close_prices[int(close_prices.size / 2)]
        last_close = close_prices[-1]
        first_close = self.bars[:, 0][0]
        last_close_6m_diff = last_close / close_6m - 1
        last_close_12m_diff = last_close / first_close - 1
        return [last_close_6m_diff, last_close_12m_diff]

    def __compare_index_with_stock_performance(self):
        date_stock = self.bars[:, 5]
        date_index = self.index_bars[:, 5]
        date_stock = date_stock[date_stock != np.array(None)]
        date_index = date_index[date_index != np.array(None)]
        index_dict = {}
        # create stock and index close price list with equal date
        for idx, value in enumerate(date_index):
            for idy, valuey in enumerate(date_stock):
                if value.date() == valuey.date():
                    index_dict[idx] = idy
                    break
        # create new arrays and copy values by same date index
        close_prices_stock = np.copy(self.bars[:, 0][[*index_dict.values()], ])
        close_price_index = np.copy(self.index_bars[:, 0][[*index_dict], ])

        stock_perf = Sih.get_performance(close_prices_stock, 30)[::-1]
        index_perf = Sih.get_performance(close_price_index, 30)[::-1]

        perf_measure = 0
        if not hasattr(stock_perf, 'size') or not hasattr(index_perf, 'size') \
           or stock_perf.size == 0 or index_perf.size == 0:
            return perf_measure

        if stock_perf.size != index_perf.size:
            raise RuntimeError('Index and stock bar size is not equal.')

        for idx, perf in enumerate(index_perf):
            index_val = perf.flat[0]
            stock_val = stock_perf.flat[idx]
            if index_val > stock_val:
                perf_measure += 1
            else:
                perf_measure -= 1
        return perf_measure

    def __calculate_eps_difference(self):
        eps_estimate = self.stock.get_data_attr("recommendation", "eps")
        eps_last = 0
        for idx in range(0, 5):
            eps_annual = self.stock.get_data_attr("income",
                                                  "dilutedEpsExtraOrd",
                                                  annual=True,
                                                  quarter_diff=idx * 4)
            if eps_annual != -1:
                eps_last = eps_annual
        eps_last_diff_prc = 100 * (eps_estimate - eps_last) / eps_estimate
        return eps_last_diff_prc

    def __calculate_quality(self):
        levermann = 0
        roe = self.__calculate_roe()
        ebit_margin = self.__calculate_ebit_margin()
        ser = self.__calculate_shareholders_equity_ratio()
        # 1. RoE
        if roe > 0.2:
            self.args['lev_roe'] = 1
            levermann += 1
        elif roe < 0.1:
            self.args['lev_roe'] = -1
            levermann -= 1
        # 2. Ebit
        if ebit_margin > 0.12:
            self.args['lev_ebit_margin'] = 1
            levermann += 1
        elif ebit_margin < 0.06:
            self.args['lev_ebit_margin'] = -1
            levermann -= 1
        # 3. equity ratio
        if ser > 0.25:
            self.args['lev_sharehold_equity_ratio'] = 1
            levermann += 1
        elif ser < 0.15:
            self.args['lev_sharehold_equity_ratio'] = -1
            levermann -= 1
        return levermann

    def __calculate_rating(self):
        self.args['lev_eps_5_years'] = -1
        levermann = 0
        price_earnings_ratios = self.__calculate_price_earnings_ratios()
        if price_earnings_ratios is None:
            return -1
        # 4. Price-Earnings-Ratio and 5 Price-Earnings-Ratio 5 years ago
        for ratio in price_earnings_ratios:
            if ratio > 0 or ratio < 12:
                levermann += 1
            elif ratio > 12 or ratio < 0:
                levermann -= 1
        self.args['lev_eps_5_years'] = levermann
        # todo add 5. eps
        return levermann

    def __calculate_mood(self):
        levermann = 0
        rating = self.calculate_trendsrating(
            self.stock.get_data("recommendation")
            ['trends'][0]['distributionList']
        )

        # 6. Analysis  >= 2.5 +1 <=1.5 -1
        if rating >= 2.5:
            self.args['lev_mood'] = 1
            levermann += 1
        elif rating <= 1.5:
            self.args['lev_mood'] = -1
            levermann -= 1

        impact_quartly = self.__calculate_impact_of_quartly_figures()
        # 7. impact of quart figures > 1 % +1 < -1 %
        # = stock price reaction - index quotation reaction
        if impact_quartly > 1.0:
            self.args['lev_impact_quart'] = 1
            levermann += 1
        elif impact_quartly < -1.0:
            self.args['lev_impact_quart'] = -1
            levermann -= 1
        return levermann

    def __calculate_momentum(self):
        levermann = 0
        rating_dif_prc = self.__calculate_rating_differences_in_percent()
        performance_list_stock = self.__calculate_performance()
        # 8. EPS -  not possible with our data therefore
        # we take the overall rating
        if rating_dif_prc > 10.0:
            self.args['lev_rating_dif_prc'] = 1
            levermann += 1
        elif rating_dif_prc < 10.0:
            self.args['lev_rating_dif_prc'] = -1
            levermann -= 1
        # 9. performance 6 months and 10. 12 months
        for per_it in performance_list_stock:
            if per_it > 0.05:
                self.args['lev_stock_performance'] = 1
                levermann += 1
            elif per_it < -0.05:
                self.args['lev_stock_performance'] = -1
                levermann -= 1
        # 11. raising momentum
        if performance_list_stock[0] > 0.05 and \
                (0.05 > performance_list_stock[1] > -0.05 or
                 performance_list_stock[1] < -0.05):
            self.args['lev_raising_momentum'] = 1
            levermann += 1
        elif performance_list_stock[0] < -0.05 and \
                (0.05 > performance_list_stock[1] > -0.05 or
                 performance_list_stock[1] > 0.05):
            self.args['lev_raising_momentum'] = -1
            levermann -= 1
        return levermann

    def __calculate_technique(self):
        levermann = 0
        perf_measure = self.__compare_index_with_stock_performance()
        # 12. 3 month interval compare with index
        if perf_measure == 3:
            levermann += 1
            self.args['lev_cmp_index'] = 1
        elif perf_measure == -3:
            levermann -= 1
            self.args['lev_cmp_index'] = -1
        return levermann

    def __calculate_growing(self):
        levermann = 0
        eps_last_diff_prc = self.__calculate_eps_difference()
        # 13. compare guessed eps of this year withe next year
        if eps_last_diff_prc > 5.0:
            self.args['lev_eps_diff'] = 1
            levermann += 1
        elif eps_last_diff_prc < -5.0:
            self.args['lev_eps_diff'] = -1
            levermann -= 1
        return levermann

    def analyse(self):
        self.calc = self.__calculate_quality() \
                    + self.__calculate_rating() \
                    + self.__calculate_mood() \
                    + self.__calculate_momentum() \
                    + self.__calculate_technique() \
                    + self.__calculate_growing()
        return super(LevermannScore, self).analyse()

    def get_calculation(self):
        return self.calc

    def look_back_date(self):
        return self.now_date + relativedelta(months=-self.lookback)
