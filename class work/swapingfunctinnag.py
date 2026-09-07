def swap(x, y):
    print("Before swapping a:", x)
    print("Before swapping b:", y)
    
    # Swap values
    x, y = y, x
    print("After swaping a becomes:",x)
    print("After swaping b becomes:",y)


# Take input from user
a = int(input("Enter value for a: "))
b = int(input("Enter value for b: "))
swap (a,b)
