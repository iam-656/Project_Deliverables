"""
Integrated Flask Web Application - All-in-One Solution
Combines: Dataset Generation + Algorithm Application + Visualization
Run: python integrated_app.py
Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_file
import math
import time
import json
import os
import random
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATASET_FOLDER'] = 'datasets'

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('datasets', exist_ok=True)

# ============================================================================
# ALGORITHM IMPLEMENTATIONS
# ============================================================================

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def brute_force_closest(points):
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
    if len(points) < 2:
        return None, float('inf')
    
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    return closest_pair_recursive(px, py)

def karatsuba(x, y):
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

# ============================================================================
# DATASET GENERATION
# ============================================================================

def generate_points_dataset(num_points, min_coord=-1000, max_coord=1000):
    points = []
    for _ in range(num_points):
        x = random.uniform(min_coord, max_coord)
        y = random.uniform(min_coord, max_coord)
        points.append((x, y))
    return points

def generate_integer_dataset(num_digits_range):
    num_digits = random.randint(num_digits_range[0], num_digits_range[1])
    x = random.randint(10**(num_digits-1), 10**num_digits - 1)
    y = random.randint(10**(num_digits-1), 10**num_digits - 1)
    return x, y

# ============================================================================
# FILE PARSING
# ============================================================================

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

def read_points_file(filepath):
    with open(filepath, 'r') as f:
        n = int(f.readline().strip())
        points = []
        for line in f:
            x, y = map(float, line.strip().split())
            points.append((x, y))
    return points

def read_integers_file(filepath):
    with open(filepath, 'r') as f:
        x = int(f.readline().strip())
        y = int(f.readline().strip())
    return x, y

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('integrated.html')

@app.route('/api/generate-datasets', methods=['POST'])
def generate_datasets():
    try:
        generated_files = []
        
        # Generate 10 closest pair datasets
        point_sizes = [150, 200, 300, 500, 1000, 120, 180, 250, 400, 800]
        
        for i, size in enumerate(point_sizes, 1):
            points = generate_points_dataset(size)
            filename = f'closest_pair_input_{i}.txt'
            filepath = os.path.join(app.config['DATASET_FOLDER'], filename)
            
            with open(filepath, 'w') as f:
                f.write(f"{len(points)}\n")
                for point in points:
                    f.write(f"{point[0]:.6f} {point[1]:.6f}\n")
            
            file_stat = os.stat(filepath)
            generated_files.append({
                'name': filename,
                'type': 'closest_pair',
                'size': file_stat.st_size,
                'points': size,
                'timestamp': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Generate 10 karatsuba datasets
        digit_ranges = [(120, 150), (150, 200), (200, 250), (300, 350), (400, 450),
                        (110, 130), (140, 160), (180, 220), (250, 300), (350, 400)]
        
        for i, digit_range in enumerate(digit_ranges, 1):
            x, y = generate_integer_dataset(digit_range)
            filename = f'integer_mult_input_{i}.txt'
            filepath = os.path.join(app.config['DATASET_FOLDER'], filename)
            
            with open(filepath, 'w') as f:
                f.write(f"{x}\n{y}\n")
            
            file_stat = os.stat(filepath)
            generated_files.append({
                'name': filename,
                'type': 'karatsuba',
                'size': file_stat.st_size,
                'digits': f"{len(str(x))}, {len(str(y))}",
                'timestamp': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'total_files': len(generated_files),
            'files': generated_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apply-algorithms', methods=['POST'])
def apply_algorithms():
    try:
        results = []
        dataset_dir = app.config['DATASET_FOLDER']
        
        # Process closest pair files
        closest_files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('closest_pair_input_')])
        
        for filename in closest_files:
            filepath = os.path.join(dataset_dir, filename)
            points = read_points_file(filepath)
            
            start_time = time.time()
            pair, min_dist = closest_pair_of_points(points)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            
            results.append({
                'filename': filename,
                'type': 'closest_pair',
                'num_points': len(points),
                'distance': min_dist,
                'execution_time_ms': execution_time,
                'status': 'success'
            })
        
        # Process karatsuba files
        karatsuba_files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('integer_mult_input_')])
        
        for filename in karatsuba_files:
            filepath = os.path.join(dataset_dir, filename)
            x, y = read_integers_file(filepath)
            
            start_time = time.time()
            result = karatsuba(x, y)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            expected = x * y
            verified = (result == expected)
            
            results.append({
                'filename': filename,
                'type': 'karatsuba',
                'x_digits': len(str(x)),
                'y_digits': len(str(y)),
                'result_digits': len(str(result)),
                'verified': verified,
                'execution_time_ms': execution_time,
                'status': 'success' if verified else 'failed'
            })
        
        # Calculate statistics
        closest_results = [r for r in results if r['type'] == 'closest_pair']
        karatsuba_results = [r for r in results if r['type'] == 'karatsuba']
        
        stats = {
            'closest_pair': {
                'total': len(closest_results),
                'avg_time': sum(r['execution_time_ms'] for r in closest_results) / len(closest_results) if closest_results else 0,
                'min_time': min(r['execution_time_ms'] for r in closest_results) if closest_results else 0,
                'max_time': max(r['execution_time_ms'] for r in closest_results) if closest_results else 0
            },
            'karatsuba': {
                'total': len(karatsuba_results),
                'avg_time': sum(r['execution_time_ms'] for r in karatsuba_results) / len(karatsuba_results) if karatsuba_results else 0,
                'min_time': min(r['execution_time_ms'] for r in karatsuba_results) if karatsuba_results else 0,
                'max_time': max(r['execution_time_ms'] for r in karatsuba_results) if karatsuba_results else 0,
                'all_verified': all(r['verified'] for r in karatsuba_results)
            }
        }
        
        # Save results to files
        with open(os.path.join(dataset_dir, 'closest_pair_results.txt'), 'w') as f:
            f.write("CLOSEST PAIR OF POINTS - RESULTS\n")
            f.write("="*80 + "\n\n")
            for r in closest_results:
                f.write(f"Dataset: {r['filename']}\n")
                f.write(f"Number of points: {r['num_points']}\n")
                f.write(f"Distance: {r['distance']:.6f}\n")
                f.write(f"Execution time: {r['execution_time_ms']:.4f} ms\n")
                f.write("-"*80 + "\n\n")
        
        with open(os.path.join(dataset_dir, 'integer_mult_results.txt'), 'w') as f:
            f.write("KARATSUBA INTEGER MULTIPLICATION - RESULTS\n")
            f.write("="*80 + "\n\n")
            for r in karatsuba_results:
                f.write(f"Dataset: {r['filename']}\n")
                f.write(f"First integer digits: {r['x_digits']}\n")
                f.write(f"Second integer digits: {r['y_digits']}\n")
                f.write(f"Result digits: {r['result_digits']}\n")
                f.write(f"Verification: {'PASSED' if r['verified'] else 'FAILED'}\n")
                f.write(f"Execution time: {r['execution_time_ms']:.4f} ms\n")
                f.write("-"*80 + "\n\n")
        
        return jsonify({
            'success': True,
            'results': results,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-files', methods=['GET'])
def list_files():
    try:
        dataset_dir = app.config['DATASET_FOLDER']
        files = []
        
        if os.path.exists(dataset_dir):
            for filename in os.listdir(dataset_dir):
                if filename.endswith('.txt') and (filename.startswith('closest_pair_input_') or filename.startswith('integer_mult_input_')):
                    filepath = os.path.join(dataset_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    file_type = 'closest_pair' if filename.startswith('closest_pair') else 'karatsuba'
                    
                    files.append({
                        'name': filename,
                        'type': file_type,
                        'size': file_stat.st_size,
                        'timestamp': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        files.sort(key=lambda x: x['name'])
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualize-file', methods=['POST'])
def visualize_file():
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['DATASET_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        if filename.startswith('closest_pair'):
            points = read_points_file(filepath)
            
            start_time = time.time()
            pair, dist = closest_pair_of_points(points)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            
            return jsonify({
                'success': True,
                'type': 'closest_pair',
                'num_points': len(points),
                'points': points,
                'closest_pair': pair,
                'distance': dist,
                'execution_time_ms': execution_time
            })
            
        elif filename.startswith('integer_mult'):
            x, y = read_integers_file(filepath)
            
            start_time = time.time()
            result = karatsuba(x, y)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            expected = x * y
            verified = (result == expected)
            
            return jsonify({
                'success': True,
                'type': 'karatsuba',
                'x': str(x),
                'y': str(y),
                'x_digits': len(str(x)),
                'y_digits': len(str(y)),
                'result': str(result),
                'result_digits': len(str(result)),
                'verified': verified,
                'execution_time_ms': execution_time
            })
        
        else:
            return jsonify({'error': 'Unknown file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-and-visualize', methods=['POST'])
def upload_and_visualize():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        content = file.read().decode('utf-8')
        
        # Try to detect file type and process
        try:
            # Try as closest pair
            points = parse_points_file(content)
            
            start_time = time.time()
            pair, dist = closest_pair_of_points(points)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            
            return jsonify({
                'success': True,
                'type': 'closest_pair',
                'num_points': len(points),
                'points': points,
                'closest_pair': pair,
                'distance': dist,
                'execution_time_ms': execution_time
            })
        except:
            # Try as karatsuba
            try:
                x, y = parse_integers_file(content)
                
                start_time = time.time()
                result = karatsuba(x, y)
                end_time = time.time()
                
                execution_time = (end_time - start_time) * 1000
                expected = x * y
                verified = (result == expected)
                
                return jsonify({
                    'success': True,
                    'type': 'karatsuba',
                    'x': str(x),
                    'y': str(y),
                    'x_digits': len(str(x)),
                    'y_digits': len(str(y)),
                    'result': str(result),
                    'result_digits': len(str(result)),
                    'verified': verified,
                    'execution_time_ms': execution_time
                })
            except:
                return jsonify({'error': 'Could not parse file as closest pair or karatsuba format'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Divide & Conquer Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        
        .section-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
        }
        
        h2 {
            color: #667eea;
            font-size: 1.8em;
        }
        
        .section-description {
            color: #666;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .file-list {
            max-height: 400px;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .file-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .file-item:hover {
            background: #f0f0ff;
        }
        
        .file-item.selected {
            background: #e6f0ff;
            border-left: 4px solid #667eea;
        }
        
        .file-info {
            flex-grow: 1;
        }
        
        .file-name {
            font-weight: bold;
            color: #333;
        }
        
        .file-meta {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .file-badge {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .badge-closest {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-karatsuba {
            background: #cce5ff;
            color: #004085;
        }
        
        .progress-container {
            display: none;
            margin-top: 20px;
        }
        
        .progress-container.show {
            display: block;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .progress-text {
            text-align: center;
            margin-top: 10px;
            color: #667eea;
            font-weight: bold;
        }
        
        .results-summary {
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
        }
        
        .results-summary.show {
            display: block;
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .results-display {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
        }
        
        .results-display.show {
            display: block;
            animation: slideIn 0.5s ease;
        }
        
        .result-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }
        
        .result-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .result-value {
            color: #333;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        
        .success {
            background: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        
        .error {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        
        canvas {
            width: 100%;
            max-width: 100%;
            height: 400px;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin-top: 20px;
            background: white;
        }
        
        .file-input-wrapper {
            position: relative;
            margin: 20px 0;
        }
        
        .file-input {
            display: none;
        }
        
        .file-label {
            display: block;
            padding: 15px;
            background: white;
            border: 2px dashed #667eea;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-label:hover {
            background: #f0f0ff;
            border-color: #764ba2;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            
            .stat-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Divide & Conquer Platform</h1>
            <p class="subtitle">Generate → Apply → Visualize - All in One Place</p>
        </header>
        
        <div class="main-content">
            <!-- SECTION 1: Generate Datasets -->
            <div class="section">
                <div class="section-header">
                    <div class="section-number">1</div>
                    <div>
                        <h2>Generate Datasets</h2>
                    </div>
                </div>
                <p class="section-description">
                    Generate 20 random datasets (10 for Closest Pair, 10 for Karatsuba Multiplication) with varying complexities.
                </p>
                
                <button class="btn" id="generateBtn" onclick="generateDatasets()">
                    📁 Generate All Datasets
                </button>
                
                <div class="loading" id="generateLoading">
                    <div class="spinner"></div>
                    <p>Generating datasets...</p>
                </div>
                
                <div class="file-list" id="generatedFilesList" style="display: none;"></div>
            </div>
            
            <!-- SECTION 2: Apply Algorithms -->
            <div class="section">
                <div class="section-header">
                    <div class="section-number">2</div>
                    <div>
                        <h2>Apply Algorithms</h2>
                    </div>
                </div>
                <p class="section-description">
                    Process all generated datasets and apply the appropriate divide-and-conquer algorithms.
                </p>
                
                <button class="btn" id="applyBtn" onclick="applyAlgorithms()" disabled>
                    ⚙️ Apply Algorithms to All Datasets
                </button>
                
                <div class="progress-container" id="applyProgress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill">0%</div>
                    </div>
                    <div class="progress-text" id="progressText">Processing datasets...</div>
                </div>
                
                <div class="results-summary" id="resultsSummary">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📊 Processing Results</h3>
                    <div class="stat-grid" id="statsGrid"></div>
                </div>
            </div>
            
            <!-- SECTION 3: Visualize Results -->
            <div class="section">
                <div class="section-header">
                    <div class="section-number">3</div>
                    <div>
                        <h2>Visualize Results</h2>
                    </div>
                </div>
                <p class="section-description">
                    Select a dataset file to visualize the algorithm results, or upload your own custom file.
                </p>
                
                <div class="button-group">
                    <button class="btn" id="refreshFilesBtn" onclick="refreshFileList()">
                        🔄 Refresh File List
                    </button>
                    <label for="customFileInput" class="btn btn-secondary" style="margin: 0;">
                        📤 Upload Custom File
                    </label>
                    <input type="file" id="customFileInput" class="file-input" accept=".txt" onchange="handleCustomFile(this)">
                </div>
                
                <div class="file-list" id="visualizeFilesList"></div>
                
                <div class="results-display" id="visualizeResults">
                    <h3 style="color: #667eea; margin-bottom: 15px;">Visualization Results</h3>
                    <div id="visualizeContent"></div>
                    <canvas id="visualizeCanvas"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedFile = null;
        
        // =====================================================
        // SECTION 1: Generate Datasets
        // =====================================================
        
        async function generateDatasets() {
            const btn = document.getElementById('generateBtn');
            const loading = document.getElementById('generateLoading');
            const filesList = document.getElementById('generatedFilesList');
            
            btn.disabled = true;
            loading.classList.add('show');
            filesList.style.display = 'none';
            
            try {
                const response = await fetch('/api/generate-datasets', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayGeneratedFiles(data.files);
                    document.getElementById('applyBtn').disabled = false;
                    alert(`✓ Successfully generated ${data.total_files} datasets!`);
                } else {
                    alert('✗ Error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('✗ Error: ' + error.message);
            } finally {
                loading.classList.remove('show');
                btn.disabled = false;
            }
        }
        
        function displayGeneratedFiles(files) {
            const filesList = document.getElementById('generatedFilesList');
            filesList.innerHTML = '<h4 style="padding: 15px; color: #667eea;">Generated Files:</h4>';
            
            files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-meta">
                            ${file.type === 'closest_pair' ? 'Points: ' + file.points : 'Digits: ' + file.digits} | 
                            Size: ${(file.size / 1024).toFixed(2)} KB | 
                            Created: ${file.timestamp}
                        </div>
                    </div>
                    <span class="file-badge ${file.type === 'closest_pair' ? 'badge-closest' : 'badge-karatsuba'}">
                        ${file.type === 'closest_pair' ? 'Closest Pair' : 'Karatsuba'}
                    </span>
                `;
                filesList.appendChild(fileItem);
            });
            
            filesList.style.display = 'block';
        }
        
        // =====================================================
        // SECTION 2: Apply Algorithms
        // =====================================================
        
        async function applyAlgorithms() {
            const btn = document.getElementById('applyBtn');
            const progress = document.getElementById('applyProgress');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const summary = document.getElementById('resultsSummary');
            
            btn.disabled = true;
            progress.classList.add('show');
            summary.classList.remove('show');
            
            // Simulate progress
            let currentProgress = 0;
            const progressInterval = setInterval(() => {
                if (currentProgress < 90) {
                    currentProgress += 5;
                    progressFill.style.width = currentProgress + '%';
                    progressFill.textContent = currentProgress + '%';
                }
            }, 200);
            
            try {
                const response = await fetch('/api/apply-algorithms', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                progressFill.textContent = '100%';
                
                if (data.success) {
                    setTimeout(() => {
                        progress.classList.remove('show');
                        displayResultsSummary(data.statistics, data.results);
                    }, 500);
                } else {
                    alert('✗ Error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                clearInterval(progressInterval);
                alert('✗ Error: ' + error.message);
            } finally {
                btn.disabled = false;
            }
        }
        
        function displayResultsSummary(stats, results) {
            const summary = document.getElementById('resultsSummary');
            const statsGrid = document.getElementById('statsGrid');
            
            const successCount = results.filter(r => r.status === 'success').length;
            const failedCount = results.filter(r => r.status === 'failed').length;
            
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Total Processed</div>
                    <div class="stat-value">${results.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Successful</div>
                    <div class="stat-value" style="color: #28a745;">${successCount}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Closest Pair Avg Time</div>
                    <div class="stat-value">${stats.closest_pair.avg_time.toFixed(2)} ms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Karatsuba Avg Time</div>
                    <div class="stat-value">${stats.karatsuba.avg_time.toFixed(2)} ms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">All Verified</div>
                    <div class="stat-value" style="color: ${stats.karatsuba.all_verified ? '#28a745' : '#dc3545'};">
                        ${stats.karatsuba.all_verified ? '✓ Yes' : '✗ No'}
                    </div>
                </div>
            `;
            
            summary.classList.add('show');
            refreshFileList();
        }
        
        // =====================================================
        // SECTION 3: Visualize Results
        // =====================================================
        
        async function refreshFileList() {
            const filesList = document.getElementById('visualizeFilesList');
            filesList.innerHTML = '<div style="padding: 15px; text-align: center;">Loading files...</div>';
            
            try {
                const response = await fetch('/api/list-files');
                const data = await response.json();
                
                if (data.success && data.files.length > 0) {
                    displayVisualizableFiles(data.files);
                } else {
                    filesList.innerHTML = '<div style="padding: 15px; text-align: center; color: #999;">No datasets available. Please generate datasets first.</div>';
                }
            } catch (error) {
                filesList.innerHTML = '<div style="padding: 15px; text-align: center; color: #dc3545;">Error loading files: ' + error.message + '</div>';
            }
        }
        
        function displayVisualizableFiles(files) {
            const filesList = document.getElementById('visualizeFilesList');
            filesList.innerHTML = '<h4 style="padding: 15px; color: #667eea;">Available Datasets (Click to Visualize):</h4>';
            
            files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.onclick = () => selectAndVisualizeFile(file.name, fileItem);
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-meta">
                            Type: ${file.type === 'closest_pair' ? 'Closest Pair' : 'Karatsuba'} | 
                            Size: ${(file.size / 1024).toFixed(2)} KB | 
                            Modified: ${file.timestamp}
                        </div>
                    </div>
                    <span class="file-badge ${file.type === 'closest_pair' ? 'badge-closest' : 'badge-karatsuba'}">
                        ${file.type === 'closest_pair' ? 'Closest Pair' : 'Karatsuba'}
                    </span>
                `;
                filesList.appendChild(fileItem);
            });
        }
        
        async function selectAndVisualizeFile(filename, fileItem) {
            // Update selection UI
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
            });
            fileItem.classList.add('selected');
            
            selectedFile = filename;
            
            // Show loading
            const resultsDisplay = document.getElementById('visualizeResults');
            const visualizeContent = document.getElementById('visualizeContent');
            visualizeContent.innerHTML = '<div class="loading show"><div class="spinner"></div><p>Processing...</p></div>';
            resultsDisplay.classList.add('show');
            
            try {
                const response = await fetch('/api/visualize-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ filename: filename })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayVisualizationResults(data);
                } else {
                    visualizeContent.innerHTML = `<div class="result-item error"><div class="result-label">✗ Error</div><div class="result-value">${data.error}</div></div>`;
                }
            } catch (error) {
                visualizeContent.innerHTML = `<div class="result-item error"><div class="result-label">✗ Error</div><div class="result-value">${error.message}</div></div>`;
            }
        }
        
        function displayVisualizationResults(data) {
            const visualizeContent = document.getElementById('visualizeContent');
            
            if (data.type === 'closest_pair') {
                visualizeContent.innerHTML = `
                    <div class="result-item success">
                        <div class="result-label">✓ Closest Pair Algorithm Completed</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Number of Points:</div>
                        <div class="result-value">${data.num_points}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Closest Pair:</div>
                        <div class="result-value">
                            Point 1: (${data.closest_pair[0][0].toFixed(4)}, ${data.closest_pair[0][1].toFixed(4)})<br>
                            Point 2: (${data.closest_pair[1][0].toFixed(4)}, ${data.closest_pair[1][1].toFixed(4)})
                        </div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Minimum Distance:</div>
                        <div class="result-value">${data.distance.toFixed(6)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Execution Time:</div>
                        <div class="result-value">${data.execution_time_ms.toFixed(4)} ms</div>
                    </div>
                `;
                drawPoints(data.points, data.closest_pair);
            } else if (data.type === 'karatsuba') {
                const truncateNumber = (num, maxLength = 60) => {
                    if (num.length <= maxLength) return num;
                    const half = Math.floor(maxLength / 2);
                    return `${num.substring(0, half)}...${num.substring(num.length - half)}`;
                };
                
                visualizeContent.innerHTML = `
                    <div class="result-item ${data.verified ? 'success' : 'error'}">
                        <div class="result-label">${data.verified ? '✓' : '✗'} ${data.verified ? 'Verification Passed' : 'Verification Failed'}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">First Integer:</div>
                        <div class="result-value">${data.x_digits} digits<br>${truncateNumber(data.x)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Second Integer:</div>
                        <div class="result-value">${data.y_digits} digits<br>${truncateNumber(data.y)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Result:</div>
                        <div class="result-value">
                            ${data.result_digits} digits<br>
                            ${truncateNumber(data.result, 80)}
                        </div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Execution Time:</div>
                        <div class="result-value">${data.execution_time_ms.toFixed(4)} ms</div>
                    </div>
                `;
                
                // Hide canvas for karatsuba
                document.getElementById('visualizeCanvas').style.display = 'none';
            }
        }
        
        function drawPoints(points, closestPair) {
            const canvas = document.getElementById('visualizeCanvas');
            canvas.style.display = 'block';
            const ctx = canvas.getContext('2d');
            
            canvas.width = canvas.offsetWidth;
            canvas.height = 400;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const xs = points.map(p => p[0]);
            const ys = points.map(p => p[1]);
            const minX = Math.min(...xs);
            const maxX = Math.max(...xs);
            const minY = Math.min(...ys);
            const maxY = Math.max(...ys);
            
            const padding = 40;
            const scaleX = (canvas.width - 2 * padding) / (maxX - minX);
            const scaleY = (canvas.height - 2 * padding) / (maxY - minY);
            
            function toCanvasX(x) {
                return padding + (x - minX) * scaleX;
            }
            
            function toCanvasY(y) {
                return canvas.height - padding - (y - minY) * scaleY;
            }
            
            // Draw all points
            ctx.fillStyle = '#667eea';
            points.forEach(point => {
                ctx.beginPath();
                ctx.arc(toCanvasX(point[0]), toCanvasY(point[1]), 3, 0, 2 * Math.PI);
                ctx.fill();
            });
            
            // Draw closest pair line
            ctx.strokeStyle = '#f44';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(toCanvasX(closestPair[0][0]), toCanvasY(closestPair[0][1]));
            ctx.lineTo(toCanvasX(closestPair[1][0]), toCanvasY(closestPair[1][1]));
            ctx.stroke();
            
            // Highlight closest pair points
            ctx.fillStyle = '#f44';
            ctx.beginPath();
            ctx.arc(toCanvasX(closestPair[0][0]), toCanvasY(closestPair[0][1]), 6, 0, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(toCanvasX(closestPair[1][0]), toCanvasY(closestPair[1][1]), 6, 0, 2 * Math.PI);
            ctx.fill();
        }
        
        async function handleCustomFile(input) {
            if (!input.files || input.files.length === 0) return;
            
            const file = input.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            const resultsDisplay = document.getElementById('visualizeResults');
            const visualizeContent = document.getElementById('visualizeContent');
            visualizeContent.innerHTML = '<div class="loading show"><div class="spinner"></div><p>Processing uploaded file...</p></div>';
            resultsDisplay.classList.add('show');
            
            try {
                const response = await fetch('/api/upload-and-visualize', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayVisualizationResults(data);
                } else {
                    visualizeContent.innerHTML = `<div class="result-item error"><div class="result-label">✗ Error</div><div class="result-value">${data.error}</div></div>`;
                }
            } catch (error) {
                visualizeContent.innerHTML = `<div class="result-item error"><div class="result-label">✗ Error</div><div class="result-value">${error.message}</div></div>`;
            }
            
            // Reset input
            input.value = '';
        }
        
        // Initialize on page load
        window.onload = function() {
            refreshFileList();
        };
    </script>
</body>
</html>'''

def setup_templates():
    """Create templates directory and HTML file"""
    os.makedirs('templates', exist_ok=True)
    with open('templates/integrated.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE)
    print("✓ Templates created successfully")

if __name__ == '__main__':
    print("="*80)
    print("INTEGRATED DIVIDE & CONQUER PLATFORM")
    print("="*80)
    print("\nFeatures:")
    print("  1. Generate Datasets - Create 20 random test files")
    print("  2. Apply Algorithms - Process all datasets automatically")
    print("  3. Visualize Results - Interactive file selection and visualization")
    print("="*80)
    
    setup_templates()
    
    print("\n🚀 Starting Flask server...")
    print("📱 Access the application at: http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)