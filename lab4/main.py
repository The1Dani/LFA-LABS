from interp import findString

if __name__ == "__main__":
    # Variant 2
    programs = [
        "M?N^2(O|P)^3Q^*R^+",
        "(X|Y|Z)^38^+(9|O)^2",
        "(H|i)(J|K)L^*N?",
    ]

    for prog in programs:
        result = findString(prog, 5)

        print(result)
