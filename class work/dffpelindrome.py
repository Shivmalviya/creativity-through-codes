#mathematical reversal technique
num = 9669669

rev=0 #reverse
temp = 9669669

while temp> 0: #temporary__ loop run when number is over
    digit = temp % 10 #degit=1
    rev = rev* 10 + digit #rev=0:0*10=0+1 rev=1
    temp //= 10 

if num == rev:
    print("The number is Palindrome")
else:
    print("The number is Not Palindrome")