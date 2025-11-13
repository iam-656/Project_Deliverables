import math
import random
import os

# ============================================================================
# PROBLEM 1: CLOSEST PAIR OF POINTS (Divide and Conquer)
# ============================================================================

def distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def brute_force_closest(points):
    """Brute force method for small number of points"""
    min_dist = float('inf')
    n = len(points)
    pair = None
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = distance(points[i], points[j])
            if dist < min_dist:
                min_dist = dist
                pair = (points[i], points[j])
    
    return pair, min_dist

def strip_closest(strip, d):
    """Find closest pair in strip of width 2d"""
    min_dist = d
    strip.sort(key=lambda point: point[1])  # Sort by y-coordinate
    pair = None
    
    for i in range(len(strip)):
        j = i + 1
        while j < len(strip) and (strip[j][1] - strip[i][1]) < min_dist:
            dist = distance(strip[i], strip[j])
            if dist < min_dist:
                min_dist = dist
                pair = (strip[i], strip[j])
            j += 1
    
    return pair, min_dist

def closest_pair_recursive(px, py):
    """
    Recursive divide and conquer for closest pair
    px: points sorted by x-coordinate
    py: points sorted by y-coordinate
    """
    n = len(px)
    
    # Base case: use brute force for small inputs
    if n <= 3:
        return brute_force_closest(px)
    
    # Divide: find middle point
    mid = n // 2
    midpoint = px[mid]
    
    # Divide points into left and right halves
    pyl = [p for p in py if p[0] <= midpoint[0]]
    pyr = [p for p in py if p[0] > midpoint[0]]
    
    # Conquer: recursively find closest pairs in both halves
    pair_left, dl = closest_pair_recursive(px[:mid], pyl)
    pair_right, dr = closest_pair_recursive(px[mid:], pyr)
    
    # Find the smaller distance
    if dl < dr:
        d = dl
        min_pair = pair_left
    else:
        d = dr
        min_pair = pair_right
    
    # Build strip of points closer than d to dividing line
    strip = [p for p in py if abs(p[0] - midpoint[0]) < d]
    
    # Find closest pair in strip
    strip_pair, strip_dist = strip_closest(strip, d)
    
    # Return the minimum
    if strip_pair and strip_dist < d:
        return strip_pair, strip_dist
    else:
        return min_pair, d

def closest_pair_of_points(points):
    """
    Main function to find closest pair of points
    Time Complexity: O(n log n)
    """
    if len(points) < 2:
        return None, float('inf')
    
    # Sort points by x and y coordinates
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    return closest_pair_recursive(px, py)

# ============================================================================
# PROBLEM 2: INTEGER MULTIPLICATION (Karatsuba Algorithm)
# ============================================================================

def karatsuba(x, y):
    """
    Karatsuba algorithm for fast multiplication
    Time Complexity: O(n^log2(3)) ≈ O(n^1.585)
    """
    # Base case for recursion
    if x < 10 or y < 10:
        return x * y
    
    # Calculate the size of the numbers
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    
    # Split the numbers
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)
    
    # Three recursive calls (divide and conquer)
    z0 = karatsuba(low1, low2)
    z1 = karatsuba((low1 + high1), (low2 + high2))
    z2 = karatsuba(high1, high2)
    
    # Combine the results
    return (z2 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z0

def integer_multiplication(x, y):
    """Wrapper function for Karatsuba multiplication"""
    return karatsuba(x, y)

# ============================================================================
# TEST DATA GENERATION
# ============================================================================

def generate_points_dataset(num_points, min_coord=-1000, max_coord=1000):
    """Generate random points for closest pair problem"""
    points = []
    for _ in range(num_points):
        x = random.uniform(min_coord, max_coord)
        y = random.uniform(min_coord, max_coord)
        points.append((x, y))
    return points

def generate_integer_dataset(num_digits_range):
    """Generate random integers for multiplication"""
    num_digits = random.randint(num_digits_range[0], num_digits_range[1])
    x = random.randint(10**(num_digits-1), 10**num_digits - 1)
    y = random.randint(10**(num_digits-1), 10**num_digits - 1)
    return x, y

def save_datasets():
    """Generate and save 10 datasets for each problem"""
    
    # Create directory for datasets
    os.makedirs('datasets', exist_ok=True)
    
    print("Generating datasets...")
    
    # Generate 10 datasets for Closest Pair of Points
    # 5 with size > 100, 5 with varying sizes
    point_sizes = [150, 200, 300, 500, 1000, 120, 180, 250, 400, 800]
    
    for i, size in enumerate(point_sizes, 1):
        points = generate_points_dataset(size)
        filename = f'datasets/closest_pair_input_{i}.txt'
        with open(filename, 'w') as f:
            f.write(f"{len(points)}\n")
            for point in points:
                f.write(f"{point[0]:.6f} {point[1]:.6f}\n")
        print(f"Created: {filename} (Size: {size} points)")
    
    # Generate 10 datasets for Integer Multiplication
    # 5 with large integers (> 100 digits), 5 with varying sizes
    digit_ranges = [(120, 150), (150, 200), (200, 250), (300, 350), (400, 450),
                    (110, 130), (140, 160), (180, 220), (250, 300), (350, 400)]
    
    for i, digit_range in enumerate(digit_ranges, 1):
        x, y = generate_integer_dataset(digit_range)
        filename = f'datasets/integer_mult_input_{i}.txt'
        with open(filename, 'w') as f:
            f.write(f"{x}\n{y}\n")
        print(f"Created: {filename} (Digits: {len(str(x))}, {len(str(y))})")
    
    print("\nAll datasets generated successfully!")

# ============================================================================
# TESTING THE ALGORITHMS
# ============================================================================

def test_closest_pair():
    """Test closest pair algorithm with sample data"""
    print("\n" + "="*70)
    print("TESTING CLOSEST PAIR OF POINTS")
    print("="*70)
    
    # Small test case
    points = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
    print(f"\nTest points: {points}")
    
    pair, dist = closest_pair_of_points(points)
    print(f"Closest pair: {pair}")
    print(f"Distance: {dist:.6f}")
    
    # Verify with brute force
    bf_pair, bf_dist = brute_force_closest(points)
    print(f"\nBrute force verification:")
    print(f"Closest pair: {bf_pair}")
    print(f"Distance: {bf_dist:.6f}")
    print(f"Match: {abs(dist - bf_dist) < 1e-9}")

def test_integer_multiplication():
    """Test Karatsuba multiplication with sample data"""
    print("\n" + "="*70)
    print("TESTING INTEGER MULTIPLICATION (KARATSUBA)")
    print("="*70)
    
    test_cases = [
        (1234, 5678),
        (12345678, 87654321),
        (123456789012345, 987654321098765)
    ]
    
    for x, y in test_cases:
        result = karatsuba(x, y)
        expected = x * y
        print(f"\n{x} × {y}")
        print(f"Karatsuba result: {result}")
        print(f"Expected result:  {expected}")
        print(f"Match: {result == expected}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("DIVIDE AND CONQUER ALGORITHMS IMPLEMENTATION")
    print("="*70)
    
    # Test the algorithms
    test_closest_pair()
    test_integer_multiplication()
    
    # Generate datasets
    print("\n" + "="*70)
    print("GENERATING DATASETS")
    print("="*70)
    save_datasets()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("✓ Closest Pair of Points: O(n log n) divide and conquer")
    print("✓ Karatsuba Multiplication: O(n^1.585) divide and conquer")
    print("✓ 10 test files for Closest Pair (sizes > 100)")
    print("✓ 10 test files for Integer Multiplication (digits > 100)")
    print("\nAll files saved in 'datasets/' directory")