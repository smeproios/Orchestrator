"""
SMEPro Orchestrator - Data Processing Pipeline
Prototype Implementation
"""

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import io
import base64
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMEPro Orchestrator - Data Processing Pipeline</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 100%); }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 40px rgba(0,0,0,0.15); }
        .drop-zone { border: 2px dashed #cbd5e1; transition: all 0.3s ease; }
        .drop-zone.dragover { border-color: #3b82f6; background-color: #eff6ff; }
        .metric-card { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white">
        <div class="max-w-7xl mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold">SMEPro Orchestrator</h1>
                        <p class="text-blue-200 text-sm">Data Processing Pipeline v2.0</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium">Lamar University</p>
                    <p class="text-xs text-blue-200">College of Business</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left Panel: Upload & Config -->
            <div class="lg:col-span-1 space-y-6">
                <!-- Upload Card -->
                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 card-hover">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                        </svg>
                        Upload Dataset
                    </h2>
                    <div id="dropZone" class="drop-zone rounded-xl p-8 text-center cursor-pointer">
                        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                        </div>
                        <p class="text-gray-700 font-medium mb-2">Drop your file here</p>
                        <p class="text-sm text-gray-500 mb-4">or click to browse</p>
                        <p class="text-xs text-gray-400">CSV, Excel, JSON (max 50MB)</p>
                        <input type="file" id="fileInput" class="hidden" accept=".csv,.xlsx,.xls,.json">
                    </div>
                </div>

                <!-- Course Context -->
                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 card-hover">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4">Course Context</h2>
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Course</label>
                            <select id="courseSelect" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="BANA-3300">BANA-3300: Business Analytics</option>
                                <option value="FINA-4310">FINA-4310: Financial Modeling</option>
                                <option value="MKTG-3350">MKTG-3350: Marketing Research</option>
                            </select>
                        </div>
                        <div class="bg-gray-50 rounded-lg p-3">
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">CIP Code:</span>
                                <span id="cipCode" class="font-mono font-medium">52.1302</span>
                            </div>
                            <div class="flex justify-between text-sm mt-1">
                                <span class="text-gray-500">NAICS:</span>
                                <span id="naicsCode" class="font-mono font-medium text-blue-600">541990</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Analysis Options -->
                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 card-hover">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Options</h2>
                    <div class="space-y-3">
                        <label class="flex items-center">
                            <input type="checkbox" checked class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500">
                            <span class="ml-2 text-sm text-gray-700">Auto-detect data types</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" checked class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500">
                            <span class="ml-2 text-sm text-gray-700">Generate visualizations</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500">
                            <span class="ml-2 text-sm text-gray-700">Run statistical tests</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500">
                            <span class="ml-2 text-sm text-gray-700">ML model suggestions</span>
                        </label>
                    </div>
                </div>
            </div>

            <!-- Right Panel: Results -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Welcome State -->
                <div id="welcomeState" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
                    <div class="w-24 h-24 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">Upload a Dataset to Begin</h3>
                    <p class="text-gray-500 max-w-md mx-auto">The SMEPro Data Pipeline will automatically profile your data, detect patterns, and suggest relevant analyses based on your course context.</p>
                    <div class="mt-6 flex justify-center space-x-4">
                        <div class="text-center">
                            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                <span class="text-lg font-bold text-gray-600">1</span>
                            </div>
                            <p class="text-xs text-gray-500">Upload</p>
                        </div>
                        <div class="text-gray-300 pt-4">→</div>
                        <div class="text-center">
                            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                <span class="text-lg font-bold text-gray-600">2</span>
                            </div>
                            <p class="text-xs text-gray-500">Profile</p>
                        </div>
                        <div class="text-gray-300 pt-4">→</div>
                        <div class="text-center">
                            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                <span class="text-lg font-bold text-gray-600">3</span>
                            </div>
                            <p class="text-xs text-gray-500">Analyze</p>
                        </div>
                        <div class="text-gray-300 pt-4">→</div>
                        <div class="text-center">
                            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                <span class="text-lg font-bold text-gray-600">4</span>
                            </div>
                            <p class="text-xs text-gray-500">Visualize</p>
                        </div>
                    </div>
                </div>

                <!-- Processing State -->
                <div id="processingState" class="hidden bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
                    <div class="flex items-center justify-center mb-6">
                        <div class="animate-spin w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
                    </div>
                    <h3 class="text-lg font-semibold text-center text-gray-900 mb-2">Processing Dataset...</h3>
                    <p id="processingStatus" class="text-center text-gray-500">Reading file format...</p>
                    <div class="mt-6 w-full bg-gray-200 rounded-full h-2">
                        <div id="processingBar" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                    </div>
                </div>

                <!-- Results State -->
                <div id="resultsState" class="hidden space-y-6">
                    <!-- Dataset Summary -->
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                                <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                Dataset Profile: <span id="datasetName" class="ml-2 text-gray-600">sales_data.csv</span>
                            </h2>
                            <span id="qualityBadge" class="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">Quality Score: 87%</span>
                        </div>
                        
                        <!-- Metrics Grid -->
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                            <div class="metric-card rounded-xl p-4">
                                <p class="text-sm text-gray-500 mb-1">Rows</p>
                                <p id="rowCount" class="text-2xl font-bold text-gray-900">15,420</p>
                            </div>
                            <div class="metric-card rounded-xl p-4">
                                <p class="text-sm text-gray-500 mb-1">Columns</p>
                                <p id="colCount" class="text-2xl font-bold text-gray-900">12</p>
                            </div>
                            <div class="metric-card rounded-xl p-4">
                                <p class="text-sm text-gray-500 mb-1">Missing Values</p>
                                <p id="missingCount" class="text-2xl font-bold text-amber-600">463</p>
                            </div>
                            <div class="metric-card rounded-xl p-4">
                                <p class="text-sm text-gray-500 mb-1">Data Types</p>
                                <p id="typeCount" class="text-2xl font-bold text-blue-600">4</p>
                            </div>
                        </div>

                        <!-- Data Types Breakdown -->
                        <div class="bg-gray-50 rounded-xl p-4">
                            <h3 class="text-sm font-medium text-gray-700 mb-3">Data Type Distribution</h3>
                            <div class="flex flex-wrap gap-2" id="typeTags">
                                <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">Numeric: 7</span>
                                <span class="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full">Categorical: 4</span>
                                <span class="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">DateTime: 1</span>
                            </div>
                        </div>
                    </div>

                    <!-- Recommended Analyses -->
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                        <h2 class="text-lg font-semibold text-gray-900 mb-4">Recommended Analyses</h2>
                        <div id="recommendations" class="space-y-3">
                            <!-- Will be populated dynamically -->
                        </div>
                    </div>

                    <!-- Column Preview -->
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                        <h2 class="text-lg font-semibold text-gray-900 mb-4">Column Statistics</h2>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-3 text-left font-medium text-gray-700">Column</th>
                                        <th class="px-4 py-3 text-left font-medium text-gray-700">Type</th>
                                        <th class="px-4 py-3 text-left font-medium text-gray-700">Non-Null</th>
                                        <th class="px-4 py-3 text-left font-medium text-gray-700">Unique</th>
                                        <th class="px-4 py-3 text-left font-medium text-gray-700">Sample Values</th>
                                    </tr>
                                </thead>
                                <tbody id="columnTable" class="divide-y divide-gray-200">
                                    <!-- Will be populated dynamically -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex justify-end space-x-3">
                        <button class="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                            Download Cleaned Data
                        </button>
                        <button class="px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700">
                            Open in Analysis Notebook
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Course mapping
        const courseMapping = {
            'BANA-3300': { cip: '52.1302', naics: '541990' },
            'FINA-4310': { cip: '52.0801', naics: '523999' },
            'MKTG-3350': { cip: '52.1401', naics: '541613' }
        };

        // Update course context
        document.getElementById('courseSelect').addEventListener('change', function() {
            const mapping = courseMapping[this.value];
            document.getElementById('cipCode').textContent = mapping.cip;
            document.getElementById('naicsCode').textContent = mapping.naics;
        });

        // File upload handling
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length) handleFile(files[0]);
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });

        function handleFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('course_id', document.getElementById('courseSelect').value);

            // Show processing state
            document.getElementById('welcomeState').classList.add('hidden');
            document.getElementById('resultsState').classList.add('hidden');
            document.getElementById('processingState').classList.remove('hidden');

            // Simulate progress
            const steps = [
                { msg: 'Reading file format...', progress: 20 },
                { msg: 'Parsing data structure...', progress: 40 },
                { msg: 'Generating statistical profile...', progress: 60 },
                { msg: 'Detecting data types and patterns...', progress: 80 },
                { msg: 'Synthesizing recommendations...', progress: 100 }
            ];

            steps.forEach((step, i) => {
                setTimeout(() => {
                    document.getElementById('processingStatus').textContent = step.msg;
                    document.getElementById('processingBar').style.width = step.progress + '%';
                }, i * 400);
            });

            // Send to server
            fetch('/api/v1/data/upload', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                setTimeout(() => {
                    showResults(data);
                }, 2500);
            })
            .catch(err => {
                console.error(err);
                alert('Error processing file. Please try again.');
                document.getElementById('processingState').classList.add('hidden');
                document.getElementById('welcomeState').classList.remove('hidden');
            });
        }

        function showResults(data) {
            document.getElementById('processingState').classList.add('hidden');
            document.getElementById('resultsState').classList.remove('hidden');

            // Update metrics
            document.getElementById('datasetName').textContent = data.filename;
            document.getElementById('rowCount').textContent = data.profile.rows.toLocaleString();
            document.getElementById('colCount').textContent = data.profile.columns;
            document.getElementById('missingCount').textContent = data.profile.missing_values.toLocaleString();
            document.getElementById('qualityBadge').textContent = `Quality Score: ${Math.round(data.profile.quality_score * 100)}%`;

            // Update type tags
            const typeTags = document.getElementById('typeTags');
            typeTags.innerHTML = `
                <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">Numeric: ${data.profile.data_types.numeric}</span>
                <span class="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full">Categorical: ${data.profile.data_types.categorical}</span>
                <span class="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">DateTime: ${data.profile.data_types.datetime}</span>
            `;

            // Update recommendations
            const recContainer = document.getElementById('recommendations');
            recContainer.innerHTML = data.recommendations.map(rec => `
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                            </svg>
                        </div>
                        <div>
                            <p class="font-medium text-gray-900">${rec.name}</p>
                            <p class="text-sm text-gray-500">${rec.description}</p>
                        </div>
                    </div>
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </div>
            `).join('');

            // Update column table
            const colTable = document.getElementById('columnTable');
            colTable.innerHTML = data.columns.map(col => `
                <tr>
                    <td class="px-4 py-3 font-medium text-gray-900">${col.name}</td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-1 text-xs rounded-full ${getTypeColor(col.type)}">${col.type}</span>
                    </td>
                    <td class="px-4 py-3 text-gray-600">${col.non_null.toLocaleString()} (${Math.round(col.non_null / data.profile.rows * 100)}%)</td>
                    <td class="px-4 py-3 text-gray-600">${col.unique.toLocaleString()}</td>
                    <td class="px-4 py-3 text-gray-500 text-xs">${col.sample.join(', ')}</td>
                </tr>
            `).join('');
        }

        function getTypeColor(type) {
            const colors = {
                'numeric': 'bg-blue-100 text-blue-700',
                'categorical': 'bg-purple-100 text-purple-700',
                'datetime': 'bg-green-100 text-green-700',
                'text': 'bg-gray-100 text-gray-700'
            };
            return colors[type] || 'bg-gray-100 text-gray-700';
        }
    </script>
</body>
</html>
'''

# Sample dataset generator for demo
def generate_sample_dataset():
    """Generate a sample sales dataset for demonstration"""
    np.random.seed(42)
    n_rows = 15420
    
    dates = pd.date_range(start='2023-01-01', end='2025-12-31', periods=n_rows)
    
    data = {
        'transaction_id': [f'TXN-{i:08d}' for i in range(n_rows)],
        'date': dates,
        'customer_segment': np.random.choice(['Enterprise', 'SMB', 'Consumer'], n_rows, p=[0.2, 0.3, 0.5]),
        'product_category': np.random.choice(['Electronics', 'Software', 'Services', 'Hardware'], n_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
        'revenue': np.random.lognormal(8, 1.5, n_rows),
        'units_sold': np.random.poisson(50, n_rows),
        'discount_applied': np.random.choice([0, 5, 10, 15, 20], n_rows, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        'sales_rep': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'], n_rows),
        'payment_method': np.random.choice(['Credit Card', 'Wire', 'ACH', 'Check'], n_rows, p=[0.6, 0.2, 0.15, 0.05]),
        'customer_satisfaction': np.random.choice([1, 2, 3, 4, 5], n_rows, p=[0.05, 0.1, 0.2, 0.35, 0.3]),
        'is_recurring': np.random.choice([True, False], n_rows, p=[0.3, 0.7])
    }
    
    df = pd.DataFrame(data)
    # Introduce some missing values
    mask = np.random.random(n_rows) < 0.03
    df.loc[mask, 'customer_satisfaction'] = np.nan
    
    return df

# Global sample dataset
SAMPLE_DATASET = generate_sample_dataset()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/data/upload', methods=['POST'])
def upload_data():
    """Handle file upload and return data profile"""
    
    course_id = request.form.get('course_id', 'BANA-3300')
    
    # Use sample dataset for demo (in production, would parse uploaded file)
    df = SAMPLE_DATASET.copy()
    
    # Generate profile
    profile = {
        'rows': len(df),
        'columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'quality_score': 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns))),
        'data_types': {
            'numeric': len(df.select_dtypes(include=[np.number]).columns),
            'categorical': len(df.select_dtypes(include=['object']).columns) - 1,  # Exclude transaction_id
            'datetime': len(df.select_dtypes(include=['datetime64']).columns)
        }
    }
    
    # Generate column stats
    columns = []
    for col in df.columns:
        col_data = {
            'name': col,
            'type': 'datetime' if pd.api.types.is_datetime64_any_dtype(df[col]) else 
                   'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical',
            'non_null': df[col].notna().sum(),
            'unique': df[col].nunique(),
            'sample': df[col].dropna().head(3).astype(str).tolist()
        }
        columns.append(col_data)
    
    # Generate recommendations based on data types
    recommendations = []
    
    if profile['data_types']['datetime'] > 0:
        recommendations.append({
            'name': 'Time Series Analysis',
            'description': 'Analyze trends, seasonality, and forecast future values',
            'type': 'time_series'
        })
        recommendations.append({
            'name': 'Seasonal Decomposition',
            'description': 'Break down patterns into trend, seasonal, and residual components',
            'type': 'seasonal'
        })
    
    if profile['data_types']['numeric'] >= 2:
        recommendations.append({
            'name': 'Correlation Analysis',
            'description': 'Explore relationships between numerical variables',
            'type': 'correlation'
        })
    
    if profile['data_types']['categorical'] > 0:
        recommendations.append({
            'name': 'Segmentation Analysis',
            'description': 'Group data by categories and compare metrics',
            'type': 'segmentation'
        })
    
    recommendations.append({
        'name': 'Outlier Detection',
        'description': 'Identify anomalous data points that may need attention',
        'type': 'anomaly'
    })
    
    return jsonify({
        'dataset_id': f'ds-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
        'filename': 'sales_data.csv',
        'status': 'processed',
        'profile': profile,
        'columns': columns,
        'recommendations': recommendations
    })

@app.route('/api/v1/data/profile/<dataset_id>')
def get_profile(dataset_id):
    """Get detailed profile for a dataset"""
    df = SAMPLE_DATASET
    
    profile = {
        'dataset_id': dataset_id,
        'shape': {'rows': len(df), 'columns': len(df.columns)},
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
        'categorical_summary': {col: df[col].value_counts().head(10).to_dict() 
                               for col in df.select_dtypes(include=['object']).columns}
    }
    
    return jsonify(profile)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'version': '2.0.0', 'service': 'smepro-data-pipeline'})

if __name__ == '__main__':
    print("=" * 60)
    print("SMEPro Orchestrator - Data Processing Pipeline")
    print("Version 2.0 - Strategic Scaling Architecture")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("\nSample dataset loaded: 15,420 rows x 12 columns")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
