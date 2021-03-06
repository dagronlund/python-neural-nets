__author__ = 'David'
import sys
import math

# Useful constants
epsilon = sys.float_info.epsilon

def safe_float_range(start, stop, steps):
    step = (stop - start) / steps
    for i in range(0, int(steps)):
        yield (start + i * step), step


def float_range(start, stop, step, inclusive_list=False, include_end=False):
    i = start
    if not inclusive_list:
        stop -= step
    while i <= stop:
        yield i
        i += step
    if include_end:
        yield stop


def romberg_integral(f, a, b, method, accurate_digits=10, debug=False, adaptive=False):
    results = []
    if debug: print("Romberg Debug\n\t", end=" ")
    for iteration in range(0, math.ceil(accurate_digits / 2)):  # Each iteration gives about two more digits
        sub_results = []
        results.append(sub_results)
        for sub_iteration in range(0, iteration + 1):  # Each sub-iteration length is the iteration + 1
            if sub_iteration == 0:  # First sub-iteration value is the integration
                steps = math.pow(2, iteration)  # The first iteration is one step, second two steps, fours steps...
                if adaptive:
                    epsilon = math.pow(10.0, -(iteration + 1.0))  # Rough estimate at accurate digits required
                    if debug: print("Ep: ", epsilon, end=" ", flush=True)
                    sub_results.append(adaptive_definite_integral(f, a, b, epsilon, method))
                else:
                    sub_results.append(definite_integral(f, a, b, steps, method))

                if debug: print(sub_results[-1], end=" ", flush=True)
            else:
                sub_results.append((math.pow(4, sub_iteration) * results[iteration][sub_iteration - 1] -
                    results[iteration - 1][sub_iteration - 1]) /
                    (math.pow(4, sub_iteration) - 1))  # The critical romberg code
                if debug: print(sub_results[-1], end=" ", flush=True)
        if debug: print('\n\t', end=" ")
    if debug: print()
    return results[-1][-1]  # In python -1 returns the last item, who knew?


def adaptive_definite_integral(f, a, b, epsilon, method):
    area = 0.0
    mid = (a + b) / 2  # Possibly find random mid-point?
    guess = method(f, a, b - a)
    guess_a = method(f, a, mid - a)
    guess_b = method(f, mid, b - mid)
    if math.fabs(guess_a + guess_b - guess) > epsilon:
        return adaptive_definite_integral(f, a, mid, epsilon, method) + \
            adaptive_definite_integral(f, mid, b, epsilon, method)
    else:
        return guess_a + guess_b


def definite_integral(f, a, b, steps, method):
    area = 0.0
    for x, step in safe_float_range(a, b, steps):
        area += method(f, x, step)
    return area


def derivative(f, x):
    return (f(x + epsilon * 2) - f(x)) / (epsilon * 2)


def rect_estimate(f, x, step):
    return f(x + step / 2) * step

trap_counter = 0

def trap_estimate(f, x, step):
    global trap_counter
    trap_counter += 1
    return (f(x) + f(x + step)) * step / 2


def quad_estimate(f, x, step):
    return (step / 6) * (f(x) + 4 * f(x + step / 2) + f(x + step))


def polynomial(x):
    return 1200 * x ** 5 - 3060 * x ** 4 + 2730 * x ** 3 - 990 * x ** 2 + 120 * x


def trig(x):
    return math.sin(x)


def run_trap_test(f, a, b):
    global trap_counter
    trap_counter = 0
    print("Trapezoidal: ", definite_integral(f, a, b, 10, trap_estimate), trap_counter)
    trap_counter = 0
    print("Adaptive: ", adaptive_definite_integral(f, a, b, .01, trap_estimate), trap_counter)
    trap_counter = 0
    print("Romberg: ", romberg_integral(f, a, b, trap_estimate), trap_counter)
    trap_counter = 0
    print("Adaptive Romberg: ", romberg_integral(f, a, b, trap_estimate, adaptive=True), trap_counter)
    print()

