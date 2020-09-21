#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
这个文件储存了我当时处理特征的函数，用这些特征对每个企业的信息进行处理就能得到Data中的建模期间的特征
由于并不具备多少价值，所以当时顺手就删去了处理的代码,具体的使用方式看新的代码就可以了
'''

__author__ = 'Jensen'


from pandas import DataFrame,Series
from math import exp


def Cal_Gross_profit_margin(data_cost:Series,data_revenue:Series) -> float:
    '''
    求每个企业的毛利率，毛利率是利润占成本的百分比

    强调这个东西没有考虑到有些企业提供了更多年份的发票信息
    '''
    income = data_revenue.sum()
    cost = data_cost.sum()
    Gross_profit = (income - cost) / cost
    
    return Gross_profit


def Cal_Good_check(data_revenue_and_state:DataFrame, alpha=2) -> float:
    '''
    根据销项发票的负数发票和作废发票的信息来计算良性发票所占的比值,考虑到负数发票比作废发票带来的损失更大，
    因此对负数发票基于更大的权重.

    在决策树的可视化中发现这个特征似乎并不是很有用，也许要修改这个特征的处理方式
    
    强调这个东西没有考虑到有些企业提供了更多年份的发票信息
    '''
    # 返回行数,All代表了该公司的所有发票的总和数
    All = data_revenue_and_state.shape[0]
    # 得到作废发票的个数
    Cancel = len(data_revenue_and_state.loc[data_revenue_and_state['发票状态'] == '作废发票'])
    # 得到损失的金额总数,乘上-1为了取绝对值
    Loss_df = data_revenue_and_state.loc[data_revenue_and_state['价税合计']<0]
    Loss = Loss_df['价税合计'].sum() * -1
    Mean = data_revenue_and_state['价税合计'].mean()
    # 设定良品率是所有的好的减去一个比例系数乘上所有的损失金额与平均每单发票所赚取的流水的比值，再减去作废发票的个数。
    Good = All - alpha * (Loss / Mean) - Cancel
    result = Good / All
    return result


def Cal_Degree_of_stability(data_up,data_down) -> float:
    '''
    根据上下游企业的分布情况计算该企业的稳定程度,我们认为，不应该盲目的追求上下游企业的绝对数量，而是要看其在
    供应链中的占比。若一个企业的上游稳定且下游稳定，则该企业很有可能是稳定的。

    对于稳定度特征的计算，这个函数实现的不是我的想法,我后面会尝试其他的衡量上下游稳定程度的方式

    强调这个东西没有考虑到有些企业提供了更多年份的发票信息
    '''
    Up_stability = 0 # 初始化上游稳定性为0
    Down_stability = 0 # 初始化下游稳定性为0

    try:
        # 得到上游企业出现的比例
        Up_frequency = dict(data_up.value_counts())
        Up_all = 0
        for value in Up_frequency.values():
            Up_all += value
        for key in Up_frequency.keys():
            Up_frequency[key] = Up_frequency[key] / Up_all
        # 对于上游企业来说，采购比重低于0.15的不认为具有稳定性，将采购比重高于0.15的个数，作为上游稳定性的评估指标。
        for key in Up_frequency.keys():
            if Up_frequency[key] > 0.15:
                Up_stability += 1
    except:
        Up_stability = 1

    try:
        # 得到下游企业出现的比例
        Down_frequency = dict(data_down.value_counts())
        Down_all = 0
        for value in Down_frequency.values():
            Down_all += value
        for key in Down_frequency.keys():
            Down_frequency[key] = Down_frequency[key] / Down_all
        # 对于下游企业来说，出售重低于0.15的不认为具有稳定性，将采购比重高于0.15的个数，作为下游稳定性的评估指标。
        for key in Down_frequency.keys():
            if Down_frequency[key] > 0.15:
                Down_stability += 1
    except:
        Down_stability = 1

    '''
    下面的score和stability是队员讨论和引用论文的结果，看不懂没关系，毕竟不见得有价值
    '''
    score = ((-1*Up_stability**2+6*Up_stability+1) - Down_stability)

    # 对于企业稳定性的评估
    stability = 1 / (1 + exp(-score/10))

    return stability


