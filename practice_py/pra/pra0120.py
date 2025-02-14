arr = [1, 2, 3, 33, 3, 3, 3, 5, 7, 7, 7, 8, 9, 56, 45, 34, 34
    , 5, 5, 5, 6, 7, 67, 67, 13, 32, 24, 24, 3, 3]
seen = set()
uarr = []
for num in arr:
    if num not in seen:
        uarr.append(num)
        seen.add(num)
print(uarr)

seen1 = set()
for num in arr:
        seen.add(num)
print(seen)