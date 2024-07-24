logs = {}

center = [
    439021.250000,
    7839164.000000, 
    0
]



N = 35

def spiralGen(N):
    a = [None] * N
    for i in range(N): 
        a[i] = [None] * N

    x = 0
    y = 0
    dx = 1
    dy = 0

    for i in range(N * N):
        a[y][x] = N * N - i - 1
        test = x + dx if dx else y + dy
        if test < 0 or test == N or a[y + dy][x + dx] != None:
            dx, dy = -dy, dx
        x += dx
        y += dy

    s = list(range(N**2))

    for i in range(N):
        for j in range(N):
            s[a[i][j]] = i - 17, j - 17

    return s[::-1]

spiral = spiralGen(35)

logs = {}

with open('pv.log', 'r') as rf:
    for line in rf:
        iy, ix, x, y, z = line.split()
        logs[int(ix) - 17, int(iy) - 157] = {
            'x': float(x), 
            'y': float(y),
            'z': float(z),
            'ix': int(ix)- 17,
            'iy': int(iy)- 157
        }

coords = []

for index in spiral:
    r = logs[index]
    coords.append([
        r['ix'], r['iy'], r['x'], r['y'], r['z'] - 10
    ])

print(coords)


