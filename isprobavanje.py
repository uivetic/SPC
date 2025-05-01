names = ['a', 'b', 'c']
points = ['1']

pairs = list(zip(names, points))
batch = [('a','b','1'), ('a', 'b', '2'), ('a', 'b', '3')]

points = [p[-1] for p in batch]
print(pairs)