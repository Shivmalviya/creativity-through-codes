def  factorial(n):
    if n==0 or n==1:
        
        return 1
    else:
        return n*factorial (n-1)
num = int(input("enter the number:"))
if num <0:
    print("Error: Factorial is not defined for negative nombers")
else:
    result =factorial (num)
    print(f"the factorial on {num} is {result}") 