"""
Andrew Shackelford
ashackelford@college.harvard.edu

Peter Chang
chang04@college.harvard.edu

CS 208 - Spring 2019
Final Project: A Modular System for Local Differential Privacy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

# calculate randomized response probability for given epsilon
def rr_prob(epsilon):
    return np.exp(epsilon) / (1. + np.exp(epsilon))

# return basic composition theorem
def basic_composition(epsilon, n):
    return float(epsilon) / float(n)

# return our advanced composition theorem
def advanced_composition(epsilon, n):
    epsilon, n = float(epsilon), float(n)
    old_epsilon_i = 0.
    epsilon_i = epsilon / n
    eta = epsilon
    t = 0.001
    s = 1.

    # iterate until we reach our desired threshold of 0.001
    while True:
        a = binom.cdf(np.ceil(n / 2.) - 1, n, rr_prob(epsilon_i))
        b = 1. - rr_prob(epsilon)
        t = 0.001
        if np.abs(epsilon_i - old_epsilon_i) < t and np.sign(a - b) == 1:
            return epsilon_i
        if np.sign(a - b) != s:
            s = -s
            eta = eta / 2.
        old_epsilon_i = epsilon_i
        epsilon_i = epsilon_i + s * eta

# calculate results for different values of epsilon
def calculate_results():
    basic_results = {}
    advanced_results = {}
    for epsilon in [1, 2, 5, 10]:
        basic_x, basic_y = [], []
        advanced_x, advanced_y = [], []
        for n in range(1, 101):
            basic_x.append(n)
            basic_y.append(basic_composition(epsilon, n))
            advanced_x.append(n)
            advanced_y.append(advanced_composition(epsilon, n))

        basic_results[epsilon] = (basic_x, basic_y)
        advanced_results[epsilon] = (advanced_x, advanced_y)

    return basic_results, advanced_results

# graph results for different values of epsilon
def graph_results(basic_results, advanced_results):
    for idx, epsilon in enumerate(sorted(basic_results.keys())):
        plt.plot(basic_results[epsilon][0], basic_results[epsilon][1], label='basic')
        plt.plot(advanced_results[epsilon][0], advanced_results[epsilon][1], label='advanced')
        plt.legend(loc='upper right')
        plt.xlabel(r'$n$')
        plt.ylabel(r'$\epsilon_i$')
        plt.title(r'Composition for $\epsilon$ = ' + str(epsilon))
        plt.savefig('advanced_composition_'+ str(epsilon) + '.png', bbox_inches='tight')
        plt.clf()

def main():
    basic_results, advanced_results = calculate_results()
    graph_results(basic_results, advanced_results)

if __name__ == "__main__":
    main()