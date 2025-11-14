def parse_points_file(file_content):
    lines = file_content.strip().split('\n')
    n = int(lines[0])
    points = []
    for i in range(1, min(n + 1, len(lines))):
        parts = lines[i].strip().split()
        if len(parts) >= 2:
            x, y = float(parts[0]), float(parts[1])
            points.append((x, y))
    return points


def parse_integers_file(file_content):
    lines = file_content.strip().split('\n')
    x = int(lines[0].strip())
    y = int(lines[1].strip())
    return x, y
