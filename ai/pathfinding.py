

import heapq


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(city, start, goal):

    if start == goal:
        return []

    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return _reconstruct(came_from, current)

        for neighbour in _neighbours(city, current):
            tentative_g = g_score[current] + 1
            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                priority = tentative_g + manhattan(neighbour, goal)
                heapq.heappush(open_set, (priority, neighbour))
                came_from[neighbour] = current

    return []


def _neighbours(city, pos):
    x, y = pos
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    result = []
    for nx, ny in candidates:
        if city.in_bounds(nx, ny):
            cell = city.get_cell(nx, ny)
            if cell.is_empty():
                result.append((nx, ny))
    return result


def _reconstruct(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path[1:]
