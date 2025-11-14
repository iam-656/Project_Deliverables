import math
import time
import os
from pathlib import Path

# ALGORITHM IMPLEMENTATIONS (from Question 2)

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
    strip.sort(key=lambda point: point[1])
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
    """Recursive divide and conquer for closest pair"""
    n = len(px)
    
    if n <= 3:
        return brute_force_closest(px)
    
    mid = n // 2
    midpoint = px[mid]
    
    pyl = [p for p in py if p[0] <= midpoint[0]]
    pyr = [p for p in py if p[0] > midpoint[0]]
    
    pair_left, dl = closest_pair_recursive(px[:mid], pyl)
    pair_right, dr = closest_pair_recursive(px[mid:], pyr)
    
    if dl < dr:
        d = dl
        min_pair = pair_left
    else:
        d = dr
        min_pair = pair_right
    
    strip = [p for p in py if abs(p[0] - midpoint[0]) < d]
    strip_pair, strip_dist = strip_closest(strip, d)
    
    if strip_pair and strip_dist < d:
        return strip_pair, strip_dist
    else:
        return min_pair, d

def closest_pair_of_points(points):
    """Main function to find closest pair of points"""
    if len(points) < 2:
        return None, float('inf')
    
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    return closest_pair_recursive(px, py)

def karatsuba(x, y):
    """Karatsuba algorithm for fast multiplication"""
    if x < 10 or y < 10:
        return x * y
    
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)
    
    z0 = karatsuba(low1, low2)
    z1 = karatsuba((low1 + high1), (low2 + high2))
    z2 = karatsuba(high1, high2)
    
    return (z2 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z0

# FILE READING FUNCTIONS

def read_points_file(filename):
    """Read points from file"""
    with open(filename, 'r') as f:
        n = int(f.readline().strip())
        points = []
        for line in f:
            x, y = map(float, line.strip().split())
            points.append((x, y))
    return points

def read_integers_file(filename):
    """Read two integers from file"""
    with open(filename, 'r') as f:
        x = int(f.readline().strip())
        y = int(f.readline().strip())
    return x, y

# APPLY ALGORITHMS TO DATASETS

def apply_closest_pair_algorithm():
    """Apply closest pair algorithm to all datasets"""
    print("\n" + "="*80)
    print("APPLYING CLOSEST PAIR OF POINTS ALGORITHM")
    print("="*80)
    
    results = []
    dataset_dir = 'datasets'
    
    # Find all closest pair input files
    files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('closest_pair_input_')])
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(dataset_dir, filename)
        print(f"\n[Dataset {i}] Processing: {filename}")
        print("-" * 80)
        
        try:
            # Read points
            points = read_points_file(filepath)
            print(f"Number of points: {len(points)}")
            
            # Measure execution time
            start_time = time.time()
            pair, min_dist = closest_pair_of_points(points)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Display results
            print(f"\n✓ Closest pair found:")
            print(f"  Point 1: ({pair[0][0]:.6f}, {pair[0][1]:.6f})")
            print(f"  Point 2: ({pair[1][0]:.6f}, {pair[1][1]:.6f})")
            print(f"  Distance: {min_dist:.6f}")
            print(f"  Execution time: {execution_time:.4f} ms")
            
            # Store results
            results.append({
                'dataset': filename,
                'num_points': len(points),
                'pair': pair,
                'distance': min_dist,
                'time_ms': execution_time
            })
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
    
    # Save results to file
    output_file = os.path.join(dataset_dir, 'closest_pair_results.txt')
    with open(output_file, 'w') as f:
        f.write("CLOSEST PAIR OF POINTS - RESULTS\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"Dataset: {result['dataset']}\n")
            f.write(f"Number of points: {result['num_points']}\n")
            f.write(f"Closest pair:\n")
            f.write(f"  Point 1: ({result['pair'][0][0]:.6f}, {result['pair'][0][1]:.6f})\n")
            f.write(f"  Point 2: ({result['pair'][1][0]:.6f}, {result['pair'][1][1]:.6f})\n")
            f.write(f"Distance: {result['distance']:.6f}\n")
            f.write(f"Execution time: {result['time_ms']:.4f} ms\n")
            f.write("-"*80 + "\n\n")
    
    print(f"\n✓ Results saved to: {output_file}")
    return results

def apply_karatsuba_algorithm():
    """Apply Karatsuba multiplication to all datasets"""
    print("\n" + "="*80)
    print("APPLYING KARATSUBA INTEGER MULTIPLICATION ALGORITHM")
    print("="*80)
    
    results = []
    dataset_dir = 'datasets'
    
    # Find all integer multiplication input files
    files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('integer_mult_input_')])
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(dataset_dir, filename)
        print(f"\n[Dataset {i}] Processing: {filename}")
        print("-" * 80)
        
        try:
            # Read integers
            x, y = read_integers_file(filepath)
            print(f"First integer digits:  {len(str(x))}")
            print(f"Second integer digits: {len(str(y))}")
            
            # Measure execution time
            start_time = time.time()
            result = karatsuba(x, y)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Verify with standard multiplication
            expected = x * y
            is_correct = (result == expected)
            
            # Display results
            print(f"\n✓ Multiplication completed:")
            print(f"  Result digits: {len(str(result))}")
            print(f"  First 50 digits: {str(result)[:50]}...")
            print(f"  Last 50 digits:  ...{str(result)[-50:]}")
            print(f"  Verification: {'PASSED' if is_correct else 'FAILED'}")
            print(f"  Execution time: {execution_time:.4f} ms")
            
            # Store results
            results.append({
                'dataset': filename,
                'x_digits': len(str(x)),
                'y_digits': len(str(y)),
                'result_digits': len(str(result)),
                'result': result,
                'verified': is_correct,
                'time_ms': execution_time
            })
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
    
    # Save results to file
    output_file = os.path.join(dataset_dir, 'integer_mult_results.txt')
    with open(output_file, 'w') as f:
        f.write("KARATSUBA INTEGER MULTIPLICATION - RESULTS\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"Dataset: {result['dataset']}\n")
            f.write(f"First integer digits: {result['x_digits']}\n")
            f.write(f"Second integer digits: {result['y_digits']}\n")
            f.write(f"Result digits: {result['result_digits']}\n")
            f.write(f"First 100 digits of result: {str(result['result'])[:100]}...\n")
            f.write(f"Last 100 digits of result: ...{str(result['result'])[-100:]}\n")
            f.write(f"Verification: {'PASSED' if result['verified'] else 'FAILED'}\n")
            f.write(f"Execution time: {result['time_ms']:.4f} ms\n")
            f.write("-"*80 + "\n\n")
    
    print(f"\n✓ Results saved to: {output_file}")
    return results

# PERFORMANCE ANALYSIS

def analyze_performance(closest_pair_results, karatsuba_results):
    """Analyze and display performance statistics"""
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    print("\n--- CLOSEST PAIR OF POINTS ---")
    print(f"Total datasets processed: {len(closest_pair_results)}")
    
    if closest_pair_results:
        avg_time = sum(r['time_ms'] for r in closest_pair_results) / len(closest_pair_results)
        min_time = min(r['time_ms'] for r in closest_pair_results)
        max_time = max(r['time_ms'] for r in closest_pair_results)
        min_size = min(r['num_points'] for r in closest_pair_results)
        max_size = max(r['num_points'] for r in closest_pair_results)
        
        print(f"Point set sizes: {min_size} to {max_size}")
        print(f"Average execution time: {avg_time:.4f} ms")
        print(f"Min execution time: {min_time:.4f} ms")
        print(f"Max execution time: {max_time:.4f} ms")
    
    print("\n--- KARATSUBA MULTIPLICATION ---")
    print(f"Total datasets processed: {len(karatsuba_results)}")
    
    if karatsuba_results:
        avg_time = sum(r['time_ms'] for r in karatsuba_results) / len(karatsuba_results)
        min_time = min(r['time_ms'] for r in karatsuba_results)
        max_time = max(r['time_ms'] for r in karatsuba_results)
        min_digits = min(r['x_digits'] for r in karatsuba_results)
        max_digits = max(r['x_digits'] for r in karatsuba_results)
        all_verified = all(r['verified'] for r in karatsuba_results)
        
        print(f"Integer sizes: {min_digits} to {max_digits} digits")
        print(f"Average execution time: {avg_time:.4f} ms")
        print(f"Min execution time: {min_time:.4f} ms")
        print(f"Max execution time: {max_time:.4f} ms")
        print(f"All verifications: {'PASSED ✓' if all_verified else 'FAILED ✗'}")

# MAIN EXECUTION

if __name__ == "__main__":
    print("="*80)
    print("QUESTION 3: APPLYING DIVIDE AND CONQUER ALGORITHMS TO DATASETS")
    print("="*80)
    
    # Check if datasets directory exists
    if not os.path.exists('datasets'):
        print("\n✗ Error: 'datasets' directory not found!")
        print("Please run Question 2 code first to generate datasets.")
    else:
        # Apply algorithms
        closest_results = apply_closest_pair_algorithm()
        karatsuba_results = apply_karatsuba_algorithm()
        
        # Analyze performance
        analyze_performance(closest_results, karatsuba_results)
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print("✓ All algorithms applied successfully")
        print("✓ Results saved to:")
        print("  - datasets/closest_pair_results.txt")
        print("  - datasets/integer_mult_results.txt")
        print("\nReady for Question 4: Building the user interface")