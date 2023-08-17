import math
from util import get_mask


def dec2bin(num: int, n) -> str:
    return "".join(format(num, f'0{n}b'))


def bin2dec(num):
    return int(num, 2)


def compute_dnf(a, b, n) -> []:
    if a == b:
        return [a]
    if int(a, 2) == 0 and int(b, 2) == 2**n - 1:
        return ["*" * n]
    if a[0] == b[0]:
        T = compute_dnf(a[1:n], b[1:n], n - 1)
        assert T is not None, print(a, b, n)
        return [a[0] + t for t in T]

    if int(a, 2) == 0:  # The prefix case
        c = dec2bin(int(b, 2) + 1, n)

        # find the index that c[i] == 1
        o = [i + 1 for i, o_i in enumerate(c) if o_i == "1"]

        output = []
        for o_i in o:
            output.append(c[0:o_i - 1] + "0" + "*" * (n - o_i))
        return output

    if int(b, 2) == 2**n - 1:  # The suffix case
        d = dec2bin(int(a, 2) - 1, n)

        # find the index that d[i] == 0
        z = [i + 1 for i, z_i in enumerate(d) if z_i == "0"]

        output = []
        for z_i in z:
            output.append(d[0:z_i - 1] + "1" + "*" * (n - z_i))
        return output

    if a[0:2] == "01" and b[0:2] == "10":  # Case 1
        T1 = compute_dnf(a[2:n], "1" * (n - 2), n - 2)
        T2 = compute_dnf("0" * (n - 2), b[2:n], n - 2)

        O1 = ["01" + t for t in T1]
        O2 = ["10" + t for t in T2]

        return O1 + O2

    elif a[0:2] == "00" and b[0:2] == "10":  # Case 2
        T = compute_dnf(a[0] + a[2:n], b[0] + b[2:n], n - 1)

        O = [t[0] + "0" + t[1:n - 1] for t in T]

        return O + ["01" + "*" * (n - 2)]

    elif a[0:2] == "01" and b[0:2] == "11":  # Case 3
        T = compute_dnf(a[0] + a[2:n], b[0] + b[2:n], n - 1)

        O = [t[0] + "1" + t[1:n - 1] for t in T]

        return O + ["10" + "*" * (n - 2)]

    elif a[0:2] == "00" and b[0:2] == "11":  # Case 4
        j = 0
        for k in range(n):
            if a[k] == "0" and b[k] == "1":
                j = k + 1
                continue
            else:
                break

        T_ = []
        for i in range(0, j - 1):
            T_.append("*" * i + "01" + "*" * (j - 2 - i))

        T_.append("1" + "*" * (j - 2) + "0")

        T__ = compute_dnf(a[j - 1:n], b[j - 1:n], n - j + 1)

        if bin2dec(b[j:n]) < bin2dec(a[j:n]) - 1:  # Case 4.1
            O_ = [t + "*" * (n - j) for t in T_]
            O__ = ["*" * (j - 1) + t for t in T__]
            return O_ + O__

        else:  # Case 4.2
            O_ = [t + "*" * (n - j) for t in T_[:-1]]
            O__ = ["*" * (j - 1) + t for t in T__ if t[0] != "1"]
            O__ += ["1" + "*" * (j - 1) + t[1:n - j + 1]
                    for t in T__ if t[0] == "1"]
            return O_ + O__


def range_encoding(low, high, n=32):
    # Assume input is binary string if it is string, and they are filled with 0 in the front side

    if n == None:
        if isinstance(low, str):
            n = len(low)
        else:
            n = int(math.log2(low)) + 1

    if not isinstance(low, str):
        low = dec2bin(low, n)

    if not isinstance(high, str):
        high = dec2bin(high, n)

    rules = compute_dnf(low, high, n)

    p4_ternary = []
    for r in rules:
        p4_ternary.append(get_mask(r))

    return p4_ternary


if __name__ == "__main__":
    import sys
    #t = range_encoding(int(sys.argv[1]), int(
    #    sys.argv[2]), 32 if len(sys.argv) < 4 else int(sys.argv[3]))
    #print(t)
    #t1 = range_encoding("111110", "11111101")
    #print(t1)
    t2 = compute_dnf("0001", "1110", 4)
    print(t2)
