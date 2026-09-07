def swap():
    
    a = int(input("Enter value for a: "))
    b = int(input("Enter value for b: "))

    print("Before swapping a:", a)
    print("Before swapping b:", b)

    
    a, b = b, a

    
    return a, b


a,b = swap()

print("After swapping a becomes:", a)
print("After swapping b becomes:", b)