test_number = 9669669
print ("The original number is : " + str(test_number))
res = str(test_number) == str(test_number)[::-1]
print ("Is the number palindrome ? : " + str(res))