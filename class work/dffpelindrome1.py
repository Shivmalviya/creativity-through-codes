
s =input("Enter a string:")
left =0
right=len(s)-1
x=0
while left<right:
        if s[left] !=s[right]:
            x +=1
            break
        left +=1
        right -=1
        if x==0:
            print("palindrome")
else:
    print("Not a palindrome")
        