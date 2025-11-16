"""
Flask Web Application for Divide and Conquer Algorithms
Question 4: User Interface Implementation
Run: python app.py
Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_file
import math
import time
import json
import os
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory
os.makedirs('uploads', exist_ok=True)

# ============================================================================
# ALGORITHM IMPLEMENTATIONS
# ============================================================================

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def brute_force_closest(points):
    min_dist = float('inf')
    n = len(points)
    pair = None
    steps = []
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = distance(points[i], points[j])
            steps.append({
                'type': 'compare',
                'points': [points[i], points[j]],
                'distance': dist
            })
            if dist < min_dist:
                min_dist = dist
                pair = (points[i], points[j])
    
    return pair, min_dist, steps

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

def closest_pair_recursive(px, py, steps):
    n = len(px)
    
    if n <= 3:
        pair, dist, brute_steps = brute_force_closest(px)
        steps.extend(brute_steps)
        return pair, dist
    
    mid = n // 2
    midpoint = px[mid]
    
    steps.append({
        'type': 'divide',
        'midpoint': midpoint,
        'left_size': mid,
        'right_size': n - mid
    })
    
    pyl = [p for p in py if p[0] <= midpoint[0]]
    pyr = [p for p in py if p[0] > midpoint[0]]
    
    pair_left, dl = closest_pair_recursive(px[:mid], pyl, steps)
    pair_right, dr = closest_pair_recursive(px[mid:], pyr, steps)
    
    if dl < dr:
        d = dl
        min_pair = pair_left
    else:
        d = dr
        min_pair = pair_right
    
    strip = [p for p in py if abs(p[0] - midpoint[0]) < d]
    steps.append({
        'type': 'strip',
        'strip_size': len(strip),
        'width': 2*d
    })
    
    strip_pair, strip_dist = strip_closest(strip, d)
    
    if strip_pair and strip_dist < d:
        return strip_pair, strip_dist
    else:
        return min_pair, d

def closest_pair_of_points_detailed(points):
    if len(points) < 2:
        return None, float('inf'), []
    
    steps = []
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    steps.append({
        'type': 'start',
        'num_points': len(points)
    })
    
    pair, dist = closest_pair_recursive(px, py, steps)
    
    steps.append({
        'type': 'result',
        'pair': pair,
        'distance': dist
    })
    
    return pair, dist, steps

def karatsuba_detailed(x, y, depth=0):
    steps = []
    
    if x < 10 or y < 10:
        result = x * y
        steps.append({
            'type': 'base_case',
            'x': x,
            'y': y,
            'result': result,
            'depth': depth
        })
        return result, steps
    
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)
    
    steps.append({
        'type': 'split',
        'x': x,
        'y': y,
        'split_pos': m,
        'depth': depth
    })
    
    z0, steps0 = karatsuba_detailed(low1, low2, depth + 1)
    z1, steps1 = karatsuba_detailed((low1 + high1), (low2 + high2), depth + 1)
    z2, steps2 = karatsuba_detailed(high1, high2, depth + 1)
    
    steps.extend(steps0)
    steps.extend(steps1)
    steps.extend(steps2)
    
    result = (z2 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z0
    
    steps.append({
        'type': 'combine',
        'result': result,
        'depth': depth
    })
    
    return result, steps

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

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/closest-pair', methods=['POST'])
def api_closest_pair():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and parse file
        content = file.read().decode('utf-8')
        points = parse_points_file(content)
        
        # Execute algorithm
        start_time = time.time()
        pair, dist, steps = closest_pair_of_points_detailed(points)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000
        
        return jsonify({
            'success': True,
            'num_points': len(points),
            'points': points,
            'closest_pair': pair,
            'distance': dist,
            'execution_time_ms': execution_time,
            'steps': steps[:100]  # Limit steps for performance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/karatsuba', methods=['POST'])
def api_karatsuba():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and parse file
        content = file.read().decode('utf-8')
        x, y = parse_integers_file(content)
        
        # Execute algorithm
        start_time = time.time()
        result, steps = karatsuba_detailed(x, y)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000
        
        # Verify
        expected = x * y
        is_correct = (result == expected)
        
        return jsonify({
            'success': True,
            'x': str(x),
            'y': str(y),
            'x_digits': len(str(x)),
            'y_digits': len(str(y)),
            'result': str(result),
            'result_digits': len(str(result)),
            'verified': is_correct,
            'execution_time_ms': execution_time,
            'steps': steps[:100]  # Limit steps for performance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HTML TEMPLATE (saved as templates/index.html)
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Divide & Conquer Algorithms Visualizer</title>
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
            max-width: 1400px;
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
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 40px;
            align-items: start;
        }
        
        .algorithm-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            transition: transform 0.3s ease;
            min-height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .algorithm-section:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .icon {
            font-size: 1.5em;
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
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
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
        
        .results {
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            display: none;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .results.show {
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
        
        .result-item {
            padding: 10px;
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
            overflow-wrap: break-word;
            max-width: 100%;
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
        
        .error {
            background: #fee;
            border-left-color: #f44;
            color: #c33;
        }
        
        .success {
            background: #efe;
            border-left-color: #4f4;
            color: #363;
        }
        
        canvas {
            width: 100%;
            height: 400px;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin-top: 20px;
            background: white;
        }
        
        .file-name {
            margin-top: 10px;
            color: #667eea;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Divide & Conquer Algorithms</h1>
            <p class="subtitle">Interactive Visualization & Analysis Tool</p>
        </header>
        
        <div class="main-content">
            <!-- Closest Pair Section -->
            <div class="algorithm-section">
                <h2><span class="icon">📍</span> Closest Pair of Points</h2>
                <p>Find the two closest points in a 2D plane using divide and conquer approach.</p>
                
                <div class="file-input-wrapper">
                    <input type="file" id="closestPairFile" class="file-input" accept=".txt">
                    <label for="closestPairFile" class="file-label">
                        📁 Click to select file or drag and drop
                    </label>
                    <div id="closestPairFileName" class="file-name"></div>
                </div>
                
                <button class="btn" id="closestPairBtn" disabled>Run Algorithm</button>
                
                <div class="loading" id="closestPairLoading">
                    <div class="spinner"></div>
                    <p>Processing...</p>
                </div>
                
                <div class="results" id="closestPairResults"></div>
                <canvas id="closestPairCanvas"></canvas>
            </div>
            
            <!-- Karatsuba Section -->
            <div class="algorithm-section">
                <h2><span class="icon">✖️</span> Karatsuba Multiplication</h2>
                <p>Multiply large integers efficiently using Karatsuba's divide and conquer algorithm.</p>
                
                <div class="file-input-wrapper">
                    <input type="file" id="karatsubaFile" class="file-input" accept=".txt">
                    <label for="karatsubaFile" class="file-label">
                        📁 Click to select file or drag and drop
                    </label>
                    <div id="karatsubaFileName" class="file-name"></div>
                </div>
                
                <button class="btn" id="karatsubaBtn" disabled>Run Algorithm</button>
                
                <div class="loading" id="karatsubaLoading">
                    <div class="spinner"></div>
                    <p>Processing...</p>
                </div>
                
                <div class="results" id="karatsubaResults"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Closest Pair File Handling
        const closestPairFile = document.getElementById('closestPairFile');
        const closestPairBtn = document.getElementById('closestPairBtn');
        const closestPairFileName = document.getElementById('closestPairFileName');
        
        closestPairFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                closestPairFileName.textContent = `Selected: ${e.target.files[0].name}`;
                closestPairBtn.disabled = false;
            }
        });
        
        closestPairBtn.addEventListener('click', async () => {
            const file = closestPairFile.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('closestPairLoading').classList.add('show');
            document.getElementById('closestPairResults').classList.remove('show');
            closestPairBtn.disabled = true;
            
            try {
                const response = await fetch('/api/closest-pair', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayClosestPairResults(data);
                    drawPoints(data.points, data.closest_pair);
                } else {
                    displayError('closestPairResults', data.error);
                }
            } catch (error) {
                displayError('closestPairResults', error.message);
            } finally {
                document.getElementById('closestPairLoading').classList.remove('show');
                closestPairBtn.disabled = false;
            }
        });
        
        // Karatsuba File Handling
        const karatsubaFile = document.getElementById('karatsubaFile');
        const karatsubaBtn = document.getElementById('karatsubaBtn');
        const karatsubaFileName = document.getElementById('karatsubaFileName');
        
        karatsubaFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                karatsubaFileName.textContent = `Selected: ${e.target.files[0].name}`;
                karatsubaBtn.disabled = false;
            }
        });
        
        karatsubaBtn.addEventListener('click', async () => {
            const file = karatsubaFile.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('karatsubaLoading').classList.add('show');
            document.getElementById('karatsubaResults').classList.remove('show');
            karatsubaBtn.disabled = true;
            
            try {
                const response = await fetch('/api/karatsuba', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayKaratsubaResults(data);
                } else {
                    displayError('karatsubaResults', data.error);
                }
            } catch (error) {
                displayError('karatsubaResults', error.message);
            } finally {
                document.getElementById('karatsubaLoading').classList.remove('show');
                karatsubaBtn.disabled = false;
            }
        });
        
        function displayClosestPairResults(data) {
            const results = document.getElementById('closestPairResults');
            results.innerHTML = `
                <div class="result-item success">
                    <div class="result-label">✓ Algorithm Completed Successfully</div>
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
            results.classList.add('show');
        }
        
        function displayKaratsubaResults(data) {
            const results = document.getElementById('karatsubaResults');
            
            // Truncate very long numbers for display
            const truncateNumber = (num, maxLength = 60) => {
                if (num.length <= maxLength) return num;
                const half = Math.floor(maxLength / 2);
                return `${num.substring(0, half)}...${num.substring(num.length - half)}`;
            };
            
            results.innerHTML = `
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
            results.classList.add('show');
        }
        
        function displayError(elementId, message) {
            const results = document.getElementById(elementId);
            results.innerHTML = `
                <div class="result-item error">
                    <div class="result-label">✗ Error</div>
                    <div class="result-value">${message}</div>
                </div>
            `;
            results.classList.add('show');
        }
        
        function drawPoints(points, closestPair) {
            const canvas = document.getElementById('closestPairCanvas');
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            canvas.width = canvas.offsetWidth;
            canvas.height = 400;
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Find bounds
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
            
            // Draw closest pair
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
    </script>
</body>
</html>'''

# ============================================================================
# CREATE TEMPLATES DIRECTORY AND HTML FILE
# ============================================================================

def setup_templates():
    """Create templates directory and HTML file"""
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE)
    print("✓ Templates created successfully")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("FLASK WEB APPLICATION FOR DIVIDE & CONQUER ALGORITHMS")
    print("="*80)
    
    setup_templates()
    
    print("\n🚀 Starting Flask server...")
    print("📱 Access the application at: http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)