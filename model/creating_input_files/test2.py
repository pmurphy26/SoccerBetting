arr = [3, 1, 5, 4, 2]
maxLen = 0
        
for i in range(len(arr)-1):
    for j in range(i+1, len(arr)):
        len_removed = j - i
        #print(ta1, ta2)
        temp_arr = arr[:i] + arr[j:]
        new_max = True
        for c in range(len(temp_arr)):
            if c + 1 not in temp_arr:
                new_max = False
                
        if new_max and len_removed > maxLen:
            maxLen = len_removed

print(maxLen)