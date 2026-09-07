def swap():
    a = int(input("Enter value for a: "))
    b = int(input("Enter value for b: "))

    print("Before swapping a:", a)
    print("Before swapping b:", b)

    a, b = b, a

    print("After swapping a becomes:", a)
    print("After swapping b becomes:", b)


swap()
