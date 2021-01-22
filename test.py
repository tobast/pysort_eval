""" Quick and dirty evaluation of Python's sorting in various scenarios """

import random
import datetime
import numpy as np
import matplotlib.pyplot as plt
import argparse

# ========== SORTERS


def _sort_name(fun):
    return fun.__name__[len("sorter_") :]


def sorter_sort(lst):
    lst.sort()
    return lst


def sorter_sorted(lst):
    return sorted(lst)


SORTERS = [sorter_sort, sorter_sorted]


# ========== GENERATORS


def _gen_name(fun):
    return fun.__name__[len("gen_") :]


def gen_fullrand(card):
    """ Just a random array """
    out = []
    for _ in range(card):
        out.append(random.randint(0, 100_000))
    return out


def gen_quasi_sorted(card):
    """ 95%-sorted array """
    base_card = int(card * 0.95)
    rem_card = card - base_card
    out = sorted(gen_fullrand(base_card))

    for _ in range(rem_card):
        val = random.randint(0, 100_000)
        pos = random.randint(0, len(out))
        out.insert(pos, val)

    return out


def gen_tomerge(card):
    """ Concatenation of two sorted arrays """
    left_card = card // 2
    right_card = card - left_card

    return sorted(gen_fullrand(left_card)) + sorted(gen_fullrand(right_card))


def gen_revsorted(card):
    """ Array sorted in reverse order """
    return sorted(gen_fullrand(card), reverse=True)


GENERATORS = [gen_fullrand, gen_quasi_sorted, gen_tomerge, gen_revsorted]

# ========== END GENERATORS


def sort_series(card: int, nb_iter: int, generator, sorter):
    results = []
    for _ in range(nb_iter // 10):
        sorter(generator(card))  # Warmup
    for _ in range(nb_iter):
        lst = generator(card)
        start = datetime.datetime.now()
        sorter(lst)
        end = datetime.datetime.now()
        delta = end - start
        results.append(delta.total_seconds())

    return results


def analyze(results):
    avg = np.average(results)
    med = np.median(results)
    std = np.std(results)

    return {
        "avg": avg,
        "med": med,
        "std": std,
    }


def run_combine(card: int, nb_iter: int):
    results = {}
    for sorter in SORTERS:
        for generator in GENERATORS:
            res = sort_series(card, nb_iter, generator, sorter)
            resdict = {
                "res": res,
            }
            resdict.update(analyze(res))
            results[(sorter, generator)] = resdict
    return results


def plot_boxes(results):
    datamatrix = []
    labels = []
    for (sorter, generator), result in results.items():
        labels.append("S={}, G={}".format(_sort_name(sorter), _gen_name(generator)))
        datamatrix.append(result["res"])
    plt.boxplot(datamatrix, notch=True, labels=labels)
    plt.xticks(rotation=10)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cardinal",
        type=int,
        help="Cardinal of a list to be sorted",
        nargs="?",
        default=2000,
    )
    parser.add_argument(
        "iterations",
        type=int,
        help="Number of times the experiment is repeated",
        nargs="?",
        default=1000,
    )
    args = parser.parse_args()
    print("Running with card={}, iterations={}".format(args.cardinal, args.iterations))
    plot_boxes(run_combine(args.cardinal, args.iterations))
