#two pointer method
def is_palindrome_pointer(data):
    s = str(data)
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:#check same or not charecters
            return False
        left += 1 #pointers come center
        right -= 1
    return True 

print(is_palindrome_pointer("9669669"))