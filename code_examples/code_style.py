def add_1(a: int, b: int):
    return a + b


def add_2(a: int, b: int):
    """
    :param a: first operand
    :param b: second operand
    :return: a plus b
    """
    return a + b


def add_3(a: int, b: int):
    for i in range(0, b):
        a = a + 1
    return a


def add_4(a: int, b: int):

    for i in range(0, b):

        a = a + 1

    return a


def main():
    print(add_3(1, 2))


if __name__ == "__main__":
    main()