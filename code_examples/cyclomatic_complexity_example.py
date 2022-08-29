def return_integer(a: int, b: int) -> int:
    number = 0
    if a > number:
        return number
    number = 2 * a
    if (a == number) and (b < number):
        return number
    while number > 500:
        number = number + 1
    return -1
