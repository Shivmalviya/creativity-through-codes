def swap(x, y):
    print("Before swapping a:", x)
    print("Before swapping b:", y)
    
    # Swap values
    x, y = y, x
    
    return x, y

# Take input from user
a = int(input("Enter value for a: "))
b = int(input("Enter value for b: "))

# Call swap function
a, b = swap(a, b)

print("After swapping a becomes:", a)
print("After swapping b becomes:", b)