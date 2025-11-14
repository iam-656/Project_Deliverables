# ===========================
# app.py
# ===========================
import os
from flask import Flask, render_template, request, jsonify
from math import sqrt
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ----------------------------------------------------
# Closest Pair Helper Functions
# ----------------------------------------------------
def distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def brute_force(points):
    min_dist = float("inf")
    pair = None
    steps = []
    n = len(points)

    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])
            steps.append(f"Distance between {points[i]} and {points[j]} = {d}")
            if d < min_dist:
                min_dist = d
                pair = (points[i], points[j])

    return min_dist, pair, steps

def strip_closest(strip, d):
    min_val = d
    steps = []
    pair = None

    strip.sort(key=lambda p: p[1])

    for i in range(len(strip)):
        j = i + 1
        while j < len(strip) and (strip[j][1] - strip[i][1] < min_val):
            dist = distance(strip[i], strip[j])
            steps.append(f"Strip check: {strip[i]} with {strip[j]} → {dist}")
            if dist < min_val:
                min_val = dist
                pair = (strip[i], strip[j])
            j += 1

    return min_val, pair, steps

def closest_pair(points):
    if len(points) <= 3:
        return brute_force(points)

    mid = len(points) // 2
    mid_point = points[mid]

    dl, pair_l, steps_l = closest_pair(points[:mid])
    dr, pair_r, steps_r = closest_pair(points[mid:])

    d = min(dl, dr)
    best_pair = pair_l if dl < dr else pair_r

    strip = [p for p in points if abs(p[0] - mid_point[0]) < d]

    ds, strip_pair, steps_s = strip_closest(strip, d)

    final_dist = ds if ds < d else d
    final_pair = strip_pair if ds < d else best_pair
    all_steps = steps_l + steps_r + steps_s

    return final_dist, final_pair, all_steps


# ----------------------------------------------------
# Karatsuba Multiplication
# ----------------------------------------------------
def karatsuba(x, y, steps):
    steps.append(f"karatsuba({x}, {y})")

    if x < 10 or y < 10:
        result = x * y
        steps.append(f"Base multiply: {x} * {y} = {result}")
        return result

    n = max(len(str(x)), len(str(y)))
    half = n // 2

    high1, low1 = divmod(x, 10 ** half)
    high2, low2 = divmod(y, 10 ** half)

    z0 = karatsuba(low1, low2, steps)
    z1 = karatsuba(low1 + high1, low2 + high2, steps)
    z2 = karatsuba(high1, high2, steps)

    result = (z2 * 10 ** (2 * half)) + ((z1 - z2 - z0) * 10 ** half) + z0
    steps.append(f"Combine → {result}")

    return result


# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/closest", methods=["POST"])
def closest_route():
    file = request.files["file"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    data = open(path).read().strip().split("\n")
    points = [tuple(map(float, line.split())) for line in data[1:]]

    start = datetime.now()
    dist, pair, steps = closest_pair(sorted(points))
    end = datetime.now()

    return jsonify({
        "distance": dist,
        "pair": pair,
        "steps": steps[:100],
        "time": (end - start).total_seconds()
    })


@app.route("/karatsuba", methods=["POST"])
def karatsuba_route():
    file = request.files["file"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    nums = open(path).read().strip().split("\n")
    a = int(nums[0])
    b = int(nums[1])

    steps = []
    start = datetime.now()
    result = karatsuba(a, b, steps)
    end = datetime.now()

    return jsonify({
        "a": a,
        "b": b,
        "result": result,
        "verified": result == a * b,
        "steps": steps[:100],
        "time": (end - start).total_seconds()
    })


if __name__ == "__main__":
    app.run(debug=True)
