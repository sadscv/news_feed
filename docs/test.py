with open('data.txt') as f:
    data = f.readlines()
    for s in data:
        list = s.split('html')
        print(list[0] + 'html')
        print('#'*30)
        print(list[1].split('_')[0])
        'tmptest'