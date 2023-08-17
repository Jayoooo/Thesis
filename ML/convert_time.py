def us2ns(sec):
    """
    from dataset to p4

    args:
        sec: float

    return: 
        ns[truncate last 16 bit]
    """

    s_int = int(sec*10**9)

    ns_bin = bin(s_int)

    try:
        t = ns_bin[:-16]
        return int(t, 2)
    except:
        return 0
        

if __name__ == "__main__":

    # a = us2ns(0.000131)
    # print(a)


    count = 0
    max_n = 100
    for i in range(1, max_n):

        a = us2ns(i/10**6)
        b = i // 65
        if a != b:
            count += 1

    print(count/max_n)
