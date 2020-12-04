from math import floor
import math
next = 15
level = 0
xp = 0

for _ in range(0, next+1):
    xp = xp + 45 * level * (floor(level / 10) + 1)
    level += 1

print(xp)

level = 0
xp = 0
current_xp = 7300
while xp <= current_xp:
    xp = xp + 45 * level * (math.floor(level / 10) + 1);
    level += 1
print(level)