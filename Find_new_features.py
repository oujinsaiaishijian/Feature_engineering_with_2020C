#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''

__author__ = 'Jensen'

from pandas import DataFrame
from collections import Counter
import numpy as np
import pandas as pd

# 尝试挖掘时间中的信息


def cal_times(Data: DataFrame) -> tuple:
    '''
    传入每个企业开票日期的那一列，返回三个数值：
    len(years): 如果企业有2017,2018两年的数据,则返回2
    months_for_each_year.mean(): 记录平均每年工作多少个月
    days_for_each_month.mean(): 记录平均每月开出多少张发票

    如E1企业，其三个数值分别就为：(4, 8.0, 107.53125)
    '''

    Data_time = Data['开票日期'].values
    # 将数据转换为pd可以处理的时间格式
    act_time = pd.to_datetime(Data_time)

    # 先用列表储存信息，每个元素是个三元列表，分别对应每张支票的年，月，日
    Date_data = []
    for each in act_time:
        year, month, day = each.year, each.month, each.day
        this_bill_time = [year, month, day]
        Date_data.append(this_bill_time)

    # 转换为array的形式方便后续处理
    Date_data = np.array(Date_data)

    # 确定企业在本表中有多少年份,如果企业有2017,2018两年的数据，则years == array([2017, 2018])
    years = np.unique(np.array(Date_data[:, 0]))
    # 储存该年度下有多少个月份在工作，如果2017年只有7月和八月在工作，2018年只有9月在工作，则mean_month == [2, 1]
    months_for_each_year = []
    # 储存在具体月份下有多少订单
    days_for_each_month = []

    # 求出平均每年工作的月份数量，和每月开出多少张发票
    for year in years:
        this_year = Date_data[Date_data[:, 0] == year]
        months = np.unique(this_year[:, 1])
        months_for_each_year.append(len(months))
        for month in months:
            this_month = this_year[this_year[:, 1] == month]
            days_for_each_month.append(len(this_month))

    months_for_each_year = np.array(months_for_each_year)
    days_for_each_month = np.array(days_for_each_month)

    # 依次返回年份个数,平均每年工作多少月，平均每月开出多少发票
    return len(years), months_for_each_year.mean(), days_for_each_month.mean()

# 尝试挖掘发票和进项金额的信息


def cal_bills(years: int, Data: DataFrame):
    '''
    传入企业的信息，返回四个数值
    negative_tax_rate: 负数发票税额是无法收回的损失。该项是负数发票的税额总和与正常发票税额的总和的比值，
    本来想通过对数化处理使得各项的差异放缓，但是发现这种处理不适合放在这种比值上，会造成很多的数据倾向于负无穷
    negative_num_rate: 统计年均负数发票的比率
    cancel_num_rate: 统计年均作废发票的比率
    Normal_price_and_tax: 统计正常的年均价税合计，这个主要是为了后面要计算毛利率用的
    如E1企业，其三个数值分别就为：(-2.5068990811115666, 17.75, 48.0, 1802967970.7425)
    '''
    bill_data = Data.loc[:, ['税额', '价税合计', '发票状态']]
    # 统计发票状态
    bill_status = Counter(Data['发票状态'])

    # 在有效发票中区别开正常发票和负数发票
    negative = bill_data.loc[np.logical_and(
        bill_data['税额'] < 0, bill_data['发票状态'] == '有效发票')]
    positive = bill_data.loc[np.logical_and(
        bill_data['税额'] > 0, bill_data['发票状态'] == '有效发票')]

    # 得到税额为负的总和税额为正的总和的比值
    negative_tax_rate = - negative['税额'].sum() / positive['税额'].sum()
    # 得出平均每年有多少负数发票和作废发票
    negative_num_rate = len(bill_data.loc[bill_data['税额'] < 0]) / years
    cancel_num_rate = bill_status['作废发票'] / years
    # 得出正常的年均价税合计,此为加工的成本价
    Normal_price_and_tax = positive['价税合计'].sum() / years

    # 依次返回负税率,年均负数发票个数,年均作废发票个数,正常的年均价税合计
    return negative_tax_rate, negative_num_rate, cancel_num_rate, Normal_price_and_tax

# 尝试挖掘企业与稳定性相关的信息
# 尝试尚未成功。
