#!/usr/bin/env python3
"""
Enhanced FastAPI Backend Server for Mindmap Generation with Editable UI
Integrates with the enhanced mindmap generator script
"""

import asyncio
import os
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Import the enhanced mindmap generator
from mindmap_generator import MindmapGenerator
from pydantic import BaseModel, Field


class MindmapRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000, description="The mindmap prompt")


class EditRequest(BaseModel):
    xml_content: str = Field(..., description="The XML content to validate and save")


class MindmapResponse(BaseModel):
    xml_content: str
    processing_time: float
    metadata: Dict[str, Any]
    success: bool


class EditResponse(BaseModel):
    success: bool
    message: str
    validated_xml: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_key_configured: bool


# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI Mindmap Generator API",
    description="Generate detailed, editable mindmaps from natural language using AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# Global mindmap generator instance
mindmap_generator = None


def initialize_generator():
    """Initialize the mindmap generator with API key"""
    global mindmap_generator

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Warning: ANTHROPIC_API_KEY environment variable not set!")
        return False

    try:
        mindmap_generator = MindmapGenerator(api_key)
        print("✅ Enhanced mindmap generator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize mindmap generator: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Enhanced Mindmap Generator API...")
    success = initialize_generator()
    if success:
        print("🎉 Server ready! Open http://localhost:8000 to use the enhanced interface")
    else:
        print("⚠️ Server started but mindmap generation may not work without API key")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the enhanced frontend HTML interface with editing capabilities"""
    try:
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Mindmap Generator & Editor</title>
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
            display: flex;
            flex-direction: column;
        }

        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header h1 {
            color: white;
            font-size: 2em;
            margin-bottom: 10px;
        }

        .header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1em;
        }

        .main-container {
            display: flex;
            flex: 1;
            gap: 20px;
            padding: 20px;
            min-height: 0;
        }

        .left-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            width: 400px;
            display: flex;
            flex-direction: column;
        }

        .right-panel {
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 20px;
            min-height: 0;
        }

        .mindmap-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }

        .editor-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            height: 300px;
            display: flex;
            flex-direction: column;
        }

        .tabs {
            display: flex;
            border-bottom: 2px solid #e1e8ed;
            margin-bottom: 20px;
        }

        .tab {
            background: none;
            border: none;
            padding: 12px 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .tab-content {
            display: none;
            flex: 1;
        }

        .tab-content.active {
            display: flex;
            flex-direction: column;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s ease;
            font-family: monospace;
        }

        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .xml-editor {
            flex: 1;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            min-height: 200px;
            background: #f8f9fa;
        }

        .generate-btn, .action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 15px;
        }

        .action-btn {
            padding: 10px 20px;
            font-size: 14px;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .secondary-btn {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        }

        .danger-btn {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }

        .generate-btn:hover, .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .generate-btn:disabled, .action-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 500;
        }

        .status.loading {
            background: #e3f2fd;
            color: #1976d2;
            border: 1px solid #bbdefb;
        }

        .status.success {
            background: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }

        .status.error {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #ffcdd2;
        }

        .mindmap-container {
            flex: 1;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            background: #fafafa;
            min-height: 400px;
        }

        .mindmap-svg {
            width: 100%;
            height: 100%;
            min-height: 400px;
        }

        .node {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .node:hover {
            filter: brightness(1.1);
            transform: scale(1.05);
        }

        .node.expanded {
            filter: brightness(1.2);
        }

        .node text {
            pointer-events: none;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 500;
        }

        .node-details {
            display: none;
            position: absolute;
            background: white;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 300px;
            z-index: 1000;
        }

        .node-details.show {
            display: block;
        }

        .node-details h4 {
            margin-bottom: 10px;
            color: #333;
        }

        .node-details .section {
            margin-bottom: 10px;
        }

        .node-details .section-title {
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }

        .node-details ul {
            margin-left: 15px;
            font-size: 12px;
            color: #666;
        }

        .edge {
            stroke-width: 2;
            fill: none;
            marker-end: url(#arrowhead);
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            align-items: center;
            flex-wrap: wrap;
        }

        .control-btn {
            background: #f5f5f5;
            border: 1px solid #ddd;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s ease;
        }

        .control-btn:hover {
            background: #e9e9e9;
        }

        .zoom-info {
            margin-left: auto;
            font-size: 12px;
            color: #666;
        }

        .metadata-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 15px;
            font-size: 12px;
            color: #495057;
        }

        .metadata-info .meta-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }

        .collapsible {
            margin-bottom: 10px;
        }

        .collapsible-header {
            background: #f1f3f4;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            user-select: none;
        }

        .collapsible-content {
            display: none;
            padding: 10px;
            border-left: 3px solid #667eea;
            margin-left: 10px;
        }

        .collapsible.open .collapsible-content {
            display: block;
        }

        @media (max-width: 1200px) {
            .main-container {
                flex-direction: column;
                gap: 15px;
                padding: 15px;
            }

            .left-panel {
                width: 100%;
            }

            .right-panel {
                flex-direction: row;
            }
        }

        @media (max-width: 768px) {
            .right-panel {
                flex-direction: column;
            }

            .header h1 {
                font-size: 1.5em;
            }

            .controls {
                flex-direction: column;
                align-items: stretch;
            }

            .zoom-info {
                margin-left: 0;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Enhanced AI Mindmap Generator</h1>
        <p>Transform your ideas into detailed, editable visual mindmaps using AI</p>
    </div>

    <div class="main-container">
        <div class="left-panel">
            <div class="form-group">
                <label for="prompt">Describe your detailed mindmap:</label>
                <textarea
                    id="prompt"
                    placeholder="Enter your mindmap description here...&#10;&#10;Example: Create a detailed mindmap for designing a machine learning system to predict customer churn for a SaaS company. Include data collection strategies, feature engineering techniques, model selection criteria, deployment pipeline components, monitoring systems, and business impact measurement methods."
                ></textarea>
            </div>

            <button class="generate-btn" onclick="generateMindmap()">
                <span id="btn-text">🚀 Generate Detailed Mindmap</span>
            </button>

            <div id="status" style="display: none;"></div>

            <div class="form-group">
                <label>Sample Detailed Prompts:</label>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <button class="control-btn" onclick="loadDetailedSample(0)" style="text-align: left; padding: 8px;">
                        📊 ML Customer Churn System
                    </button>
                    <button class="control-btn" onclick="loadDetailedSample(1)" style="text-align: left; padding: 8px;">
                        🏗️ Microservices Architecture
                    </button>
                    <button class="control-btn" onclick="loadDetailedSample(2)" style="text-align: left; padding: 8px;">
                        🎓 Complete Data Science Learning Path
                    </button>
                </div>
            </div>

            <div id="metadata-display" class="metadata-info" style="display: none;">
                <div class="meta-item"><strong>Generated:</strong> <span id="meta-timestamp"></span></div>
                <div class="meta-item"><strong>Domain:</strong> <span id="meta-domain"></span></div>
                <div class="meta-item"><strong>Complexity:</strong> <span id="meta-complexity"></span></div>
                <div class="meta-item"><strong>Total Nodes:</strong> <span id="meta-nodes"></span></div>
                <div class="meta-item"><strong>Max Depth:</strong> <span id="meta-depth"></span></div>
            </div>
        </div>

        <div class="right-panel">
            <div class="mindmap-panel">
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('visual')">🎨 Visual View</button>
                    <button class="tab" onclick="switchTab('details')">📋 Node Details</button>
                </div>

                <div id="visual-tab" class="tab-content active">
                    <div class="controls">
                        <button class="control-btn" onclick="zoomIn()">🔍 Zoom In</button>
                        <button class="control-btn" onclick="zoomOut()">🔍 Zoom Out</button>
                        <button class="control-btn" onclick="resetZoom()">🎯 Reset</button>
                        <button class="control-btn" onclick="toggleNodeDetails()">ℹ️ Toggle Details</button>
                        <button class="control-btn" onclick="downloadSVG()">💾 Download SVG</button>
                        <div class="zoom-info" id="zoom-info">Zoom: 100%</div>
                    </div>

                    <div class="mindmap-container" id="mindmap-container">
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999; font-size: 18px;">
                            Generate a mindmap to see the enhanced visualization here
                        </div>
                    </div>
                </div>

                <div id="details-tab" class="tab-content">
                    <div id="node-details-list" style="overflow-y: auto; flex: 1;">
                        <p style="color: #999; text-align: center; margin-top: 50px;">
                            Generate a mindmap to see detailed node information here
                        </p>
                    </div>
                </div>

                <div class="node-details" id="node-tooltip">
                    <h4 id="tooltip-title">Node Title</h4>
                    <div class="section">
                        <div class="section-title">Description:</div>
                        <p id="tooltip-description"></p>
                    </div>
                    <div class="section">
                        <div class="section-title">Details:</div>
                        <ul id="tooltip-details"></ul>
                    </div>
                    <div class="section">
                        <div class="section-title">Processes:</div>
                        <ul id="tooltip-processes"></ul>
                    </div>
                    <div class="section">
                        <div class="section-title">Considerations:</div>
                        <ul id="tooltip-considerations"></ul>
                    </div>
                </div>
            </div>

            <div class="editor-panel">
                <div class="tabs">
                    <button class="tab active" onclick="switchEditorTab('xml')">📝 XML Editor</button>
                    <button class="tab" onclick="switchEditorTab('raw')">🔧 Raw View</button>
                </div>

                <div id="xml-editor-tab" class="tab-content active">
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <button class="action-btn secondary-btn" onclick="validateXML()">✅ Validate</button>
                        <button class="action-btn" onclick="applyChanges()">🔄 Apply Changes</button>
                        <button class="action-btn" onclick="resetXML()">↶ Reset</button>
                        <button class="action-btn" onclick="downloadXML()">💾 Download XML</button>
                    </div>
                    <textarea id="xml-editor" class="xml-editor" placeholder="Generated XML will appear here for editing..."></textarea>
                </div>

                <div id="raw-editor-tab" class="tab-content">
                    <div style="flex: 1; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; overflow: auto;">
                        <pre id="raw-xml-display" style="font-size: 11px; line-height: 1.3; color: #495057;"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentZoom = 1;
        let currentXmlData = null;
        let originalXmlData = null;
        let nodeDetailsVisible = false;
        let parsedMindmapData = null;

        const detailedSamplePrompts = [
            "Create a comprehensive mindmap for designing a machine learning system to predict customer churn for a SaaS company. Include detailed data collection strategies, feature engineering techniques, model selection criteria, cross-validation approaches, deployment pipeline components, A/B testing frameworks, monitoring systems, alert mechanisms, and business impact measurement methods with specific KPIs.",
            "Design a detailed mindmap for a scalable microservices architecture including service decomposition strategies, API gateway patterns, database per service patterns, event-driven communication, circuit breaker implementations, distributed tracing, service mesh configurations, container orchestration, security measures, monitoring solutions, and deployment strategies with CI/CD pipeline details.",
            "Create a comprehensive mindmap for learning data science from scratch, covering mathematical foundations (statistics, linear algebra, calculus), programming languages (Python, R, SQL), data manipulation libraries, visualization tools, machine learning algorithms (supervised, unsupervised, reinforcement), deep learning frameworks, model evaluation techniques, deployment strategies, career paths, and industry applications with specific project examples."
        ];

        function loadDetailedSample(index) {
            document.getElementById('prompt').value = detailedSamplePrompts[index];
        }

        function switchTab(tabName) {
            // Remove active class from all tabs and content
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // Add active class to selected tab and content
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }

        function switchEditorTab(tabName) {
            // Remove active class from editor tabs and content
            const editorPanel = document.querySelector('.editor-panel');
            editorPanel.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            editorPanel.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // Add active class to selected tab and content
            event.target.classList.add('active');
            document.getElementById(tabName + '-editor-tab').classList.add('active');

            if (tabName === 'raw' && currentXmlData) {
                document.getElementById('raw-xml-display').textContent = currentXmlData;
            }
        }

        async function generateMindmap() {
            const prompt = document.getElementById('prompt').value.trim();

            if (!prompt) {
                showStatus('Please enter a detailed mindmap description', 'error');
                return;
            }

            const btn = document.querySelector('.generate-btn');
            const btnText = document.getElementById('btn-text');

            btn.disabled = true;
            btnText.textContent = '⏳ Generating Detailed Mindmap...';
            showStatus('Generating your detailed mindmap... This may take 60-90 seconds for comprehensive analysis.', 'loading');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: prompt })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    currentXmlData = data.xml_content;
                    originalXmlData = data.xml_content;

                    renderEnhancedMindmap(data.xml_content);
                    updateXMLEditor(data.xml_content);
                    updateMetadata(data.metadata);

                    showStatus(`✅ Detailed mindmap generated in ${data.processing_time.toFixed(1)}s!`, 'success');
                } else {
                    throw new Error(data.error || 'Generation failed');
                }

            } catch (error) {
                console.error('Generation error:', error);
                showStatus(`❌ Failed to generate mindmap: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btnText.textContent = '🚀 Generate Detailed Mindmap';
            }
        }

        function renderEnhancedMindmap(xmlContent) {
            try {
                const parser = new DOMParser();
                const xmlDoc = parser.parseFromString(xmlContent, 'text/xml');

                const parseError = xmlDoc.querySelector('parsererror');
                if (parseError) {
                    throw new Error('Invalid XML format');
                }

                // Extract enhanced data from XML
                const nodes = Array.from(xmlDoc.querySelectorAll('node')).map(node => {
                    const position = node.querySelector('position');
                    const style = node.querySelector('style');
                    const content = node.querySelector('content');

                    return {
                        id: node.getAttribute('id'),
                        level: parseInt(node.getAttribute('level')) || 0,
                        category: node.getAttribute('category') || 'general',
                        expanded: node.getAttribute('expanded') === 'true',
                        title: content ? content.querySelector('title')?.textContent || 'Unnamed' : 'Unnamed',
                        description: content ? content.querySelector('description')?.textContent || '' : '',
                        x: position ? parseInt(position.getAttribute('x')) || 400 : 400,
                        y: position ? parseInt(position.getAttribute('y')) || 300 : 300,
                        width: position ? parseInt(position.getAttribute('width')) || 160 : 160,
                        height: position ? parseInt(position.getAttribute('height')) || 60 : 60,
                        color: style ? style.getAttribute('color') || '#3498db' : '#3498db',
                        shape: style ? style.getAttribute('shape') || 'rectangle' : 'rectangle',
                        details: Array.from(node.querySelectorAll('details item')).map(item => item.textContent),
                        processes: Array.from(node.querySelectorAll('processes step')).map(step => step.textContent),
                        considerations: Array.from(node.querySelectorAll('considerations point')).map(point => point.textContent)
                    };
                });

                const edges = Array.from(xmlDoc.querySelectorAll('edge')).map(edge => {
                    const style = edge.querySelector('style');
                    return {
                        id: edge.getAttribute('id'),
                        source: edge.getAttribute('source'),
                        target: edge.getAttribute('target'),
                        label: edge.querySelector('label')?.textContent || '',
                        description: edge.querySelector('description')?.textContent || '',
                        color: style ? style.getAttribute('color') || '#7f8c8d' : '#7f8c8d',
                        weight: style ? parseInt(style.getAttribute('weight')) || 2 : 2
                    };
                });

                parsedMindmapData = { nodes, edges };
                drawEnhancedMindmap(nodes, edges);
                updateNodeDetailsList(nodes);

            } catch (error) {
                console.error('XML parsing error:', error);
                showStatus('❌ Failed to parse detailed mindmap data', 'error');
            }
        }

        function drawEnhancedMindmap(nodes, edges) {
            const container = document.getElementById('mindmap-container');

            if (nodes.length === 0) {
                container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">No nodes to display</div>';
                return;
            }

            // Calculate SVG dimensions with padding
            const maxX = Math.max(...nodes.map(n => n.x + n.width/2)) + 100;
            const maxY = Math.max(...nodes.map(n => n.y + n.height/2)) + 100;
            const minX = Math.min(...nodes.map(n => n.x - n.width/2)) - 100;
            const minY = Math.min(...nodes.map(n => n.y - n.height/2)) - 100;

            const svgWidth = maxX - minX;
            const svgHeight = maxY - minY;

            const svg = `
                <svg class="mindmap-svg" viewBox="${minX} ${minY} ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#7f8c8d"/>
                        </marker>
                        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="3" dy="3" flood-color="#00000030"/>
                        </filter>
                        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>

                    ${edges.map(edge => {
                        const sourceNode = nodes.find(n => n.id === edge.source);
                        const targetNode = nodes.find(n => n.id === edge.target);
                        if (!sourceNode || !targetNode) return '';

                        return `
                            <line class="edge"
                                x1="${sourceNode.x}" y1="${sourceNode.y}"
                                x2="${targetNode.x}" y2="${targetNode.y}"
                                stroke="${edge.color}"
                                stroke-width="${edge.weight}"
                                marker-end="url(#arrowhead)"/>
                            <text x="${(sourceNode.x + targetNode.x) / 2}"
                                  y="${(sourceNode.y + targetNode.y) / 2 - 8}"
                                  text-anchor="middle"
                                  font-size="10"
                                  fill="#666">${edge.label}</text>
                        `;
                    }).join('')}

                    ${nodes.map(node => {
                        const shapeElement = node.shape === 'circle'
                            ? `<circle cx="${node.x}" cy="${node.y}" r="${Math.max(node.width, node.height)/2}" fill="${node.color}" filter="url(#shadow)"/>`
                            : node.shape === 'ellipse' || node.shape === 'rounded_rectangle'
                            ? `<ellipse cx="${node.x}" cy="${node.y}" rx="${node.width/2}" ry="${node.height/2}" fill="${node.color}" filter="url(#shadow)"/>`
                            : `<rect x="${node.x - node.width/2}" y="${node.y - node.height/2}" width="${node.width}" height="${node.height}" rx="8" fill="${node.color}" filter="url(#shadow)"/>`;

                        const expandedIndicator = node.details.length > 0 || node.processes.length > 0 || node.considerations.length > 0
                            ? `<circle cx="${node.x + node.width/2 - 10}" cy="${node.y - node.height/2 + 10}" r="6" fill="white" stroke="${node.color}" stroke-width="2"/>
                               <text x="${node.x + node.width/2 - 10}" y="${node.y - node.height/2 + 14}" text-anchor="middle" font-size="10" fill="${node.color}">+</text>`
                            : '';

                        return `
                            <g class="node ${node.expanded ? 'expanded' : ''}" data-node-id="${node.id}" onclick="handleNodeClick('${node.id}')" onmouseover="showNodeTooltip(event, '${node.id}')" onmouseout="hideNodeTooltip()">
                                ${shapeElement}
                                ${expandedIndicator}
                                <text x="${node.x}" y="${node.y - 5}"
                                      text-anchor="middle"
                                      font-size="${node.level === 0 ? '14' : '12'}"
                                      font-weight="${node.level === 0 ? 'bold' : 'normal'}"
                                      fill="white">${node.title}</text>
                                <text x="${node.x}" y="${node.y + 10}"
                                      text-anchor="middle"
                                      font-size="9"
                                      fill="rgba(255,255,255,0.8)">${node.category}</text>
                            </g>
                        `;
                    }).join('')}
                </svg>
            `;

            container.innerHTML = svg;
            resetZoom();
        }

        function updateNodeDetailsList(nodes) {
            const detailsList = document.getElementById('node-details-list');

            const detailsHtml = nodes.map(node => `
                <div class="collapsible" onclick="toggleCollapsible(this)">
                    <div class="collapsible-header">
                        <strong>${node.title}</strong> (${node.category})
                    </div>
                    <div class="collapsible-content">
                        <p><strong>Description:</strong> ${node.description}</p>

                        ${node.details.length > 0 ? `
                            <div><strong>Details:</strong>
                                <ul>${node.details.map(detail => `<li>${detail}</li>`).join('')}</ul>
                            </div>
                        ` : ''}

                        ${node.processes.length > 0 ? `
                            <div><strong>Processes:</strong>
                                <ul>${node.processes.map(process => `<li>${process}</li>`).join('')}</ul>
                            </div>
                        ` : ''}

                        ${node.considerations.length > 0 ? `
                            <div><strong>Considerations:</strong>
                                <ul>${node.considerations.map(consideration => `<li>${consideration}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');

            detailsList.innerHTML = detailsHtml;
        }

        function toggleCollapsible(element) {
            element.classList.toggle('open');
        }

        function handleNodeClick(nodeId) {
            console.log('Node clicked:', nodeId);
            // Could implement node editing here
        }

        function showNodeTooltip(event, nodeId) {
            if (!nodeDetailsVisible || !parsedMindmapData) return;

            const node = parsedMindmapData.nodes.find(n => n.id === nodeId);
            if (!node) return;

            const tooltip = document.getElementById('node-tooltip');

            document.getElementById('tooltip-title').textContent = node.title;
            document.getElementById('tooltip-description').textContent = node.description;

            const detailsList = document.getElementById('tooltip-details');
            detailsList.innerHTML = node.details.map(detail => `<li>${detail}</li>`).join('');

            const processesList = document.getElementById('tooltip-processes');
            processesList.innerHTML = node.processes.map(process => `<li>${process}</li>`).join('');

            const considerationsList = document.getElementById('tooltip-considerations');
            considerationsList.innerHTML = node.considerations.map(consideration => `<li>${consideration}</li>`).join('');

            tooltip.style.left = event.pageX + 10 + 'px';
            tooltip.style.top = event.pageY + 10 + 'px';
            tooltip.classList.add('show');
        }

        function hideNodeTooltip() {
            document.getElementById('node-tooltip').classList.remove('show');
        }

        function toggleNodeDetails() {
            nodeDetailsVisible = !nodeDetailsVisible;
            const btn = event.target;
            btn.textContent = nodeDetailsVisible ? 'ℹ️ Hide Details' : 'ℹ️ Toggle Details';
        }

        function updateXMLEditor(xmlContent) {
            document.getElementById('xml-editor').value = xmlContent;
            document.getElementById('raw-xml-display').textContent = xmlContent;
        }

        function updateMetadata(metadata) {
            const metadataDisplay = document.getElementById('metadata-display');

            // Extract metadata from XML if not provided
            if (!metadata.timestamp) {
                try {
                    const parser = new DOMParser();
                    const xmlDoc = parser.parseFromString(currentXmlData, 'text/xml');
                    const metadataNode = xmlDoc.querySelector('metadata');

                    if (metadataNode) {
                        metadata.timestamp = metadataNode.querySelector('created_at')?.textContent || 'Unknown';
                        metadata.domain = metadataNode.querySelector('domain')?.textContent || 'General';
                        metadata.complexity = metadataNode.querySelector('complexity')?.textContent || 'Intermediate';
                        metadata.total_nodes = metadataNode.querySelector('total_nodes')?.textContent || '0';
                        metadata.max_depth = metadataNode.querySelector('max_depth')?.textContent || '0';
                    }
                } catch (e) {
                    console.error('Error parsing metadata:', e);
                }
            }

            document.getElementById('meta-timestamp').textContent = metadata.timestamp || new Date().toISOString();
            document.getElementById('meta-domain').textContent = metadata.domain || 'General';
            document.getElementById('meta-complexity').textContent = metadata.complexity || 'Intermediate';
            document.getElementById('meta-nodes').textContent = metadata.total_nodes || '0';
            document.getElementById('meta-depth').textContent = metadata.max_depth || '0';

            metadataDisplay.style.display = 'block';
        }

        async function validateXML() {
            const xmlContent = document.getElementById('xml-editor').value.trim();

            if (!xmlContent) {
                showStatus('No XML content to validate', 'error');
                return;
            }

            try {
                showStatus('Validating XML...', 'loading');

                const response = await fetch('/api/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ xml_content: xmlContent })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus('✅ XML is valid!', 'success');
                    if (data.validated_xml && data.validated_xml !== xmlContent) {
                        document.getElementById('xml-editor').value = data.validated_xml;
                        showStatus('✅ XML validated and auto-corrected!', 'success');
                    }
                } else {
                    showStatus(`❌ XML validation failed: ${data.message}`, 'error');
                }

            } catch (error) {
                console.error('Validation error:', error);
                showStatus(`❌ Validation error: ${error.message}`, 'error');
            }
        }

        async function applyChanges() {
            const xmlContent = document.getElementById('xml-editor').value.trim();

            if (!xmlContent) {
                showStatus('No XML content to apply', 'error');
                return;
            }

            try {
                showStatus('Applying changes...', 'loading');
                currentXmlData = xmlContent;
                renderEnhancedMindmap(xmlContent);
                document.getElementById('raw-xml-display').textContent = xmlContent;
                showStatus('✅ Changes applied successfully!', 'success');
            } catch (error) {
                console.error('Error applying changes:', error);
                showStatus(`❌ Failed to apply changes: ${error.message}`, 'error');
            }
        }

        function resetXML() {
            if (originalXmlData) {
                document.getElementById('xml-editor').value = originalXmlData;
                currentXmlData = originalXmlData;
                renderEnhancedMindmap(originalXmlData);
                document.getElementById('raw-xml-display').textContent = originalXmlData;
                showStatus('✅ XML reset to original', 'success');
            } else {
                showStatus('No original XML to reset to', 'error');
            }
        }

        function downloadXML() {
            const xmlContent = document.getElementById('xml-editor').value.trim();

            if (!xmlContent) {
                showStatus('No XML content to download', 'error');
                return;
            }

            const blob = new Blob([xmlContent], { type: 'application/xml' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `mindmap_${new Date().toISOString().slice(0,10)}.xml`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            URL.revokeObjectURL(url);
            showStatus('✅ XML downloaded successfully!', 'success');
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';

            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 5000);
            }
        }

        function zoomIn() {
            currentZoom = Math.min(currentZoom * 1.2, 3);
            applyZoom();
        }

        function zoomOut() {
            currentZoom = Math.max(currentZoom / 1.2, 0.3);
            applyZoom();
        }

        function resetZoom() {
            currentZoom = 1;
            applyZoom();
        }

        function applyZoom() {
            const svg = document.querySelector('.mindmap-svg');
            if (svg) {
                svg.style.transform = `scale(${currentZoom})`;
                document.getElementById('zoom-info').textContent = `Zoom: ${Math.round(currentZoom * 100)}%`;
            }
        }

        function downloadSVG() {
            const svg = document.querySelector('.mindmap-svg');
            if (!svg) {
                showStatus('No mindmap to download', 'error');
                return;
            }

            const svgData = new XMLSerializer().serializeToString(svg);
            const blob = new Blob([svgData], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `mindmap_${new Date().toISOString().slice(0,10)}.svg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            URL.revokeObjectURL(url);
            showStatus('✅ Mindmap downloaded successfully!', 'success');
        }

        // Check server health on page load
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                if (!data.api_key_configured) {
                    showStatus('⚠️ API key not configured. Please set ANTHROPIC_API_KEY environment variable.', 'error');
                }
            })
            .catch(error => {
                showStatus('❌ Cannot connect to server', 'error');
            });
    </script>
</body>
</html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading enhanced interface</h1><p>{str(e)}</p>", status_code=500)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    api_key_configured = bool(os.getenv("ANTHROPIC_API_KEY"))

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_key_configured=api_key_configured
    )

@app.post("/api/generate", response_model=MindmapResponse)
async def generate_mindmap(request: MindmapRequest):
    """Generate detailed mindmap from prompt"""

    if not mindmap_generator:
        raise HTTPException(
            status_code=500,
            detail="Mindmap generator not initialized. Please check your ANTHROPIC_API_KEY."
        )

    start_time = time.time()

    try:
        print(f"🔄 Generating detailed mindmap for prompt: '{request.prompt[:50]}...'")

        # Generate mindmap using the enhanced script
        xml_content = await mindmap_generator.generate_mindmap(request.prompt)

        processing_time = time.time() - start_time

        print(f"✅ Detailed mindmap generated successfully in {processing_time:.2f} seconds")

        # Extract additional metadata from XML
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_content)
            metadata_elem = root.find('metadata')

            extracted_metadata = {
                "prompt_length": len(request.prompt),
                "xml_length": len(xml_content),
                "timestamp": datetime.now().isoformat(),
                "domain": metadata_elem.find('domain').text if metadata_elem is not None and metadata_elem.find('domain') is not None else "general",
                "complexity": metadata_elem.find('complexity').text if metadata_elem is not None and metadata_elem.find('complexity') is not None else "intermediate",
                "total_nodes": metadata_elem.find('total_nodes').text if metadata_elem is not None and metadata_elem.find('total_nodes') is not None else "0",
                "max_depth": metadata_elem.find('max_depth').text if metadata_elem is not None and metadata_elem.find('max_depth') is not None else "0"
            }
        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
            extracted_metadata = {
                "prompt_length": len(request.prompt),
                "xml_length": len(xml_content),
                "timestamp": datetime.now().isoformat()
            }

        return MindmapResponse(
            xml_content=xml_content,
            processing_time=processing_time,
            metadata=extracted_metadata,
            success=True
        )

    except Exception as e:
        processing_time = time.time() - start_time
        error_trace = traceback.format_exc()

        print(f"❌ Error generating detailed mindmap: {e}")
        print(f"📝 Full traceback:\n{error_trace}")

        raise HTTPException(
            status_code=500,
            detail=f"Detailed mindmap generation failed: {str(e)}"
        )

@app.post("/api/validate", response_model=EditResponse)
async def validate_xml(request: EditRequest):
    """Validate and optionally correct XML content"""

    try:
        from xml.etree import ElementTree as ET

        # Try to parse the XML
        try:
            ET.fromstring(request.xml_content)
            return EditResponse(
                success=True,
                message="XML is valid",
                validated_xml=request.xml_content
            )
        except ET.ParseError as e:
            # If basic parsing fails, try to auto-correct common issues
            corrected_xml = await auto_correct_xml(request.xml_content)

            if corrected_xml:
                try:
                    ET.fromstring(corrected_xml)
                    return EditResponse(
                        success=True,
                        message="XML was invalid but has been auto-corrected",
                        validated_xml=corrected_xml
                    )
                except ET.ParseError:
                    pass

            return EditResponse(
                success=False,
                message=f"XML validation failed: {str(e)}",
                validated_xml=None
            )

    except Exception as e:
        return EditResponse(
            success=False,
            message=f"Validation error: {str(e)}",
            validated_xml=None
        )

async def auto_correct_xml(xml_content: str) -> Optional[str]:
    """Attempt to auto-correct common XML issues"""
    if not mindmap_generator:
        return None

    try:
        correction_prompt = f"""
        Fix this XML content to make it valid and well-formed:

        {xml_content}

        Common issues to fix:
        - Unclosed tags
        - Mismatched tags
        - Invalid characters in attribute values
        - Missing quotes around attributes
        - Improper nesting

        Return ONLY the corrected XML, no explanations.
        """

        response = await mindmap_generator.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": correction_prompt}]
        )

        corrected_xml = response.content[0].text.strip()

        # Clean up if it has markdown formatting
        if corrected_xml.startswith('```xml'):
            corrected_xml = corrected_xml[6:]
        if corrected_xml.endswith('```'):
            corrected_xml = corrected_xml[:-3]

        return corrected_xml.strip()

    except Exception as e:
        print(f"Auto-correction failed: {e}")
        return None

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "Enhanced API is working!",
        "timestamp": datetime.now().isoformat(),
        "generator_ready": mindmap_generator is not None,
        "features": ["detailed_nodes", "xml_editing", "enhanced_ui"]
    }

if __name__ == "__main__":
    print("🚀 Starting Enhanced Mindmap Generator Server...")
    print("📋 Make sure to set your ANTHROPIC_API_KEY environment variable!")
    print("🌐 The enhanced web interface will be available at: http://localhost:8000")
    print("✨ New features: Detailed nodes, XML editing, interactive tooltips")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )