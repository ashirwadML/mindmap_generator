#!/usr/bin/env python3
"""
Enhanced Mindmap Generation Script using Anthropic API
Takes a prompt and returns detailed XML mindmap representation with comprehensive node information
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

PARSE_MODEL = "claude-sonnet-4-20250514"
STRUCTURE_MODEL = "claude-3-5-haiku-20241022"
GENERATE_XML_MODEL = "claude-sonnet-4-20250514"
VALIDATE_XML_MODEL = "claude-3-5-haiku-20241022"

class MindmapGenerator:
    """Enhanced mindmap generator with detailed node information using Claude for each processing step"""

    def __init__(self, anthropic_api_key: str):
        self.client = AsyncAnthropic(api_key=anthropic_api_key)

    async def generate_mindmap(self, prompt: str) -> str:
        """Main method to generate detailed mindmap XML from prompt"""
        print(f"🧠 Starting enhanced mindmap generation for: '{prompt[:50]}...'")

        # Step 1: Parse prompt and extract detailed concepts
        print("1️⃣ Parsing concepts and relationships with detailed analysis...")
        parsed_data = await self._parse_concepts_detailed(prompt)

        # Step 2: Structure the knowledge graph with detailed nodes
        print("2️⃣ Building detailed knowledge structure...")
        structured_data = await self._structure_knowledge_detailed(parsed_data, prompt)

        # Step 3: Generate comprehensive XML
        print("3️⃣ Generating detailed XML mindmap...")
        xml_content = await self._generate_detailed_xml(structured_data, prompt)

        # Step 4: Validate and correct XML
        print("4️⃣ Validating XML structure...")
        final_xml = await self._validate_xml(xml_content)

        print("✅ Enhanced mindmap generation completed!")
        return final_xml

    async def _parse_concepts_detailed(self, prompt: str) -> Dict[str, Any]:
        """Extract detailed concepts with deep domain analysis and flowchart structure"""

        parsing_prompt = f"""
        You are an expert analyst creating a comprehensive mindmap for: "{prompt}"

        FIRST, analyze the domain and core workflow:
        1. Identify the domain (technology/business/education/science/healthcare/etc.)
        2. Determine the main process flow or system architecture
        3. Identify key decision points and branching logic
        4. Map out sequential steps and parallel processes

        Create a flowchart-style mindmap where each node contains rich information like a presentation slide.

        Return ONLY valid JSON - no extra text or explanations:

        {{
            "main_topic": "System/Process Name",
            "topic_description": "Comprehensive overview with context and scope",
            "mindmap_type": "flowchart",
            "domain": "machine_learning",
            "complexity_level": "intermediate",
            "workflow_type": "sequential",
            "concepts": [
                {{
                    "id": "root",
                    "title": "System Overview",
                    "description": "Complete system description with purpose and scope",
                    "level": 0,
                    "parent": null,
                    "category": "system",
                    "node_type": "start",
                    "what": "What this system does",
                    "why": "Business value and importance",
                    "how": "High-level approach and methodology",
                    "examples": ["Real example 1", "Use case 2"],
                    "metrics": ["Success metric 1", "KPI 2"],
                    "details": ["Technical requirement", "Key decision", "Success factor"],
                    "processes": ["Phase 1: Planning", "Phase 2: Implementation"],
                    "considerations": ["Major risk", "Best practice"],
                    "tools_technologies": ["Tool 1", "Technology 2"],
                    "stakeholders": ["Role 1", "Department 2"]
                }},
                {{
                    "id": "phase1",
                    "title": "Data Collection",
                    "description": "Comprehensive data gathering pipeline",
                    "level": 1,
                    "parent": "root",
                    "category": "process",
                    "node_type": "process",
                    "what": "Collect and validate data",
                    "why": "Quality data enables accurate predictions",
                    "how": "Automated ETL with validation",
                    "examples": ["Transaction logs", "User events"],
                    "metrics": ["Completeness: >95%", "Latency: <10min"],
                    "details": ["Multiple data sources", "Real-time streaming", "Quality checks"],
                    "processes": ["Source setup", "Validation", "Storage"],
                    "considerations": ["Privacy compliance", "Data retention"],
                    "tools_technologies": ["Apache Kafka", "Spark"],
                    "stakeholders": ["Data Engineers", "Privacy Team"]
                }}
            ],
            "relationships": [
                {{"from": "root", "to": "phase1", "type": "initiates", "description": "System starts with data collection"}}
            ]
        }}

        Generate 6-8 main nodes with logical flow. Each node should contain detailed information.
        Use node_type values: start, process, decision, outcome, checkpoint, end
        Keep all text content under 100 characters per field to avoid JSON issues.
        """

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.messages.create(
                    model=PARSE_MODEL,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": parsing_prompt}]
                )

                content = response.content[0].text.strip()
                content = self._clean_json_response(content)
                parsed_data = json.loads(content)

                if self._validate_detailed_parsed_data(parsed_data):
                    print(f"✅ Generated {len(parsed_data.get('concepts', []))} detailed concepts")
                    return parsed_data
                else:
                    print(f"⚠️ Invalid detailed data structure, attempt {attempt + 1}")

            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed, attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print("📝 Raw response:", content[:300] + "...")

            except Exception as e:
                print(f"⚠️ API error, attempt {attempt + 1}: {e}")

        print("🔄 Using intelligent fallback structure")
        return self._create_intelligent_fallback(prompt)

    async def _structure_knowledge_detailed(self, parsed_data: Dict, original_prompt: str) -> Dict[str, Any]:
        """Organize detailed concepts into a structured hierarchy with enhanced layout"""

        structuring_prompt = f"""
        Create a comprehensive visual layout for this detailed mindmap data: {json.dumps(parsed_data, indent=2)}

        Return ONLY valid JSON in this exact format:

        {{
            "title": "{parsed_data.get('main_topic', 'Mindmap')}",
            "description": "{parsed_data.get('topic_description', 'Comprehensive mindmap')}",
            "layout_type": "hierarchical",
            "domain": "{parsed_data.get('domain', 'general')}",
            "complexity": "{parsed_data.get('complexity_level', 'intermediate')}",
            "metadata": {{
                "total_nodes": 0,
                "max_depth": 0,
                "creation_context": "Generated from detailed analysis"
            }},
            "nodes": [
                {{
                    "id": "root",
                    "title": "Central Topic",
                    "description": "Comprehensive description",
                    "level": 0,
                    "x": 400,
                    "y": 200,
                    "width": 200,
                    "height": 80,
                    "color": "#2c3e50",
                    "shape": "rectangle",
                    "category": "core",
                    "details": ["detail1", "detail2"],
                    "processes": ["process1"],
                    "considerations": ["consideration1"],
                    "expanded": true
                }},
                {{
                    "id": "node1",
                    "title": "Major Component",
                    "description": "Detailed explanation",
                    "level": 1,
                    "x": 200,
                    "y": 350,
                    "width": 180,
                    "height": 70,
                    "color": "#3498db",
                    "shape": "rounded_rectangle",
                    "category": "process",
                    "details": ["detail1", "detail2"],
                    "processes": ["process1"],
                    "considerations": ["consideration1"],
                    "expanded": false
                }}
            ],
            "edges": [
                {{
                    "id": "edge1",
                    "from": "root",
                    "to": "node1",
                    "label": "contains",
                    "description": "Relationship description",
                    "color": "#7f8c8d",
                    "weight": 2,
                    "style": "solid"
                }}
            ]
        }}

        Enhanced Layout rules:
        - Root node at center (400, 200) with larger size (200x80)
        - Level 1 nodes distributed in semicircle below root (y=350-400)
        - Level 2 nodes positioned below their parents (y=500-550)
        - Space nodes adequately (180-220px apart horizontally)
        - Use semantic colors:
          * Core concept: "#2c3e50" (dark blue-gray)
          * Process: "#3498db" (blue)
          * Component: "#27ae60" (green)
          * Method: "#e74c3c" (red)
          * Tool: "#f39c12" (orange)
          * Outcome: "#9b59b6" (purple)
        - Vary node sizes based on importance and content amount
        - All nodes start as collapsed (expanded: false) except root
        - Include all details, processes, and considerations from parsed data
        - No extra text, just JSON
        """

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.messages.create(
                    model=STRUCTURE_MODEL,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": structuring_prompt}]
                )

                content = response.content[0].text.strip()
                content = self._clean_json_response(content)
                structured_data = json.loads(content)

                if self._validate_detailed_structured_data(structured_data):
                    # Update metadata
                    structured_data["metadata"]["total_nodes"] = len(structured_data.get("nodes", []))
                    structured_data["metadata"]["max_depth"] = max([node.get("level", 0) for node in structured_data.get("nodes", [])], default=0)
                    return structured_data
                else:
                    print(f"⚠️ Invalid detailed structure format, attempt {attempt + 1}")

            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed, attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print("📝 Raw response:", content[:300] + "...")

            except Exception as e:
                print(f"⚠️ API error, attempt {attempt + 1}: {e}")

        print("🔄 Using fallback detailed structure")
        return self._create_detailed_fallback_structure(parsed_data)

    async def _generate_detailed_xml(self, structured_data: Dict, original_prompt: str) -> str:
        """Generate comprehensive XML mindmap from detailed structured data"""

        xml_prompt = f"""
        Generate a comprehensive XML mindmap from this detailed structured data:

        Structured data: {json.dumps(structured_data, indent=2)}
        Original prompt: "{original_prompt}"

        Create valid XML with this enhanced structure:

        <?xml version="1.0" encoding="UTF-8"?>
        <mindmap version="2.0" editable="true">
            <metadata>
                <title>{{title}}</title>
                <description>{{description}}</description>
                <created_at>{{current_timestamp}}</created_at>
                <layout_type>{{layout_type}}</layout_type>
                <domain>{{domain}}</domain>
                <complexity>{{complexity_level}}</complexity>
                <total_nodes>{{node_count}}</total_nodes>
                <max_depth>{{max_depth}}</max_depth>
                <generation_context>Generated from: {{original_prompt}}</generation_context>
            </metadata>
            <nodes>
                <node id="{{unique_id}}" level="{{level}}" category="{{category}}" expanded="{{true/false}}">
                    <content>
                        <title>{{node_title}}</title>
                        <description>{{detailed_description}}</description>
                    </content>
                    <position x="{{x_coord}}" y="{{y_coord}}" width="{{width}}" height="{{height}}"/>
                    <style color="{{hex_color}}" shape="{{shape}}" border="{{border_style}}"/>
                    <details>
                        <item>{{detail_1}}</item>
                        <item>{{detail_2}}</item>
                    </details>
                    <processes>
                        <step>{{process_1}}</step>
                        <step>{{process_2}}</step>
                    </processes>
                    <considerations>
                        <point>{{consideration_1}}</point>
                        <point>{{consideration_2}}</point>
                    </considerations>
                </node>
            </nodes>
            <edges>
                <edge id="{{edge_id}}" source="{{source_id}}" target="{{target_id}}">
                    <label>{{relationship_label}}</label>
                    <description>{{relationship_description}}</description>
                    <style color="{{hex_color}}" weight="{{thickness}}" line_style="{{solid/dashed}}"/>
                </edge>
            </edges>
        </mindmap>

        Requirements:
        - All node IDs must be unique
        - All coordinates must be integers
        - Colors must be valid hex codes
        - Include ALL nodes and edges from the structured data
        - Include all details, processes, and considerations for each node
        - XML must be valid and well-formed
        - Use current timestamp for created_at
        - Set editable="true" for interactive editing
        - Include comprehensive metadata

        Return ONLY the XML content, no other text.
        """

        try:
            response = await self.client.messages.create(
                model=GENERATE_XML_MODEL,
                max_tokens=6000,
                messages=[{"role": "user", "content": xml_prompt}]
            )

            xml_content = response.content[0].text.strip()

            # Clean up XML if it has markdown formatting
            if xml_content.startswith('```xml'):
                xml_content = xml_content[6:]
            if xml_content.endswith('```'):
                xml_content = xml_content[:-3]

            return xml_content.strip()

        except Exception as e:
            print(f"❌ Error in detailed XML generation: {e}")
            return self._create_detailed_fallback_xml(structured_data, original_prompt)

    async def _validate_xml(self, xml_content: str) -> str:
        """Validate and correct enhanced XML if needed"""

        validation_prompt = f"""
        Validate and fix this enhanced XML mindmap if needed:

        {xml_content}

        Check for:
        1. Valid XML syntax with proper encoding
        2. All opening tags have matching closing tags
        3. All attributes are properly quoted
        4. Node IDs are unique across the document
        5. Edge source/target IDs reference existing nodes
        6. Coordinates are valid integers
        7. Colors are valid hex codes (6-digit format)
        8. All required elements are present (title, description, details, etc.)
        9. Proper nesting of detail items, process steps, and consideration points
        10. Metadata completeness

        If there are errors, fix them systematically and return the corrected XML.
        If it's valid, return it as-is.
        Maintain the enhanced structure with all detailed information.

        Return ONLY the XML content, no other text or explanations.
        """

        try:
            response = await self.client.messages.create(
                model=VALIDATE_XML_MODEL,
                max_tokens=6000,
                messages=[{"role": "user", "content": validation_prompt}]
            )

            validated_xml = response.content[0].text.strip()

            # Clean up XML if it has markdown formatting
            if validated_xml.startswith('```xml'):
                validated_xml = validated_xml[6:]
            if validated_xml.endswith('```'):
                validated_xml = validated_xml[:-3]

            return validated_xml.strip()

        except Exception as e:
            print(f"❌ Error in validation: {e}")
            return xml_content

    def _clean_json_response(self, content: str) -> str:
        """Clean up Claude's response to extract valid JSON"""
        # Remove markdown code blocks
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            content = content[start:end]
        elif '```' in content:
            start = content.find('```') + 3
            end = content.rfind('```')
            content = content[start:end]

        # Find JSON object boundaries
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx]

        # Clean up common JSON issues
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        import re
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        return content.strip()

    def _validate_detailed_parsed_data(self, data: Dict) -> bool:
        """Validate detailed parsed data structure"""
        required_keys = ["main_topic", "topic_description", "mindmap_type", "concepts", "relationships"]
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data["concepts"], list) or len(data["concepts"]) == 0:
            return False

        # Check first concept has required detailed fields
        if data["concepts"]:
            concept = data["concepts"][0]
            required_concept_keys = ["id", "title", "description", "level", "what", "why", "how", "examples", "metrics"]
            if not all(key in concept for key in required_concept_keys):
                return False

        return True

    def _create_intelligent_fallback(self, prompt: str) -> Dict[str, Any]:
        """Create intelligent domain-specific fallback based on prompt analysis"""

        # Analyze prompt for domain hints
        prompt_lower = prompt.lower()
        domain = "general"
        workflow_type = "sequential"

        if any(word in prompt_lower for word in ["machine learning", "ml", "ai", "model", "algorithm", "data"]):
            domain = "machine_learning"
        elif any(word in prompt_lower for word in ["architecture", "system", "software", "api", "database"]):
            domain = "software_architecture"
        elif any(word in prompt_lower for word in ["business", "strategy", "marketing", "sales", "revenue"]):
            domain = "business_strategy"
        elif any(word in prompt_lower for word in ["learn", "education", "course", "study", "training"]):
            domain = "education"

        # Extract key terms
        words = prompt.split()
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'how', 'what', 'when', 'where', 'why', 'create', 'make', 'generate', 'mindmap', 'map', 'system', 'design'}
        key_words = [w for w in words if w.lower() not in stop_words and len(w) > 3][:8]

        main_topic = ' '.join(prompt.split()[0:4]).title()

        # Create domain-specific root concept
        concepts = [{
            "id": "root",
            "title": main_topic,
            "description": f"Comprehensive {domain.replace('_', ' ')} system addressing {main_topic.lower()}",
            "level": 0,
            "parent": None,
            "category": "system",
            "node_type": "start",
            "what": f"Complete {main_topic.lower()} implementation",
            "why": f"Addresses critical business need in {domain.replace('_', ' ')}",
            "how": "Systematic approach with proven methodologies",
            "examples": [f"Industry example 1 for {main_topic}", f"Use case in {domain}"],
            "metrics": ["Success rate: >90%", "Implementation time: 3-6 months", "ROI: 2-5x"],
            "details": [
                f"Core architecture for {main_topic.lower()}",
                "Scalable and maintainable design",
                "Integration with existing systems"
            ],
            "processes": [
                "Phase 1: Requirements and planning",
                "Phase 2: Design and development",
                "Phase 3: Testing and deployment",
                "Phase 4: Monitoring and optimization"
            ],
            "considerations": [
                "Risk mitigation and contingency planning",
                "Resource allocation and timeline management"
            ],
            "tools_technologies": self._get_domain_tools(domain),
            "stakeholders": self._get_domain_stakeholders(domain)
        }]

        relationships = []

        # Generate domain-specific process flow
        if domain == "machine_learning":
            process_flow = ["Data Collection", "Feature Engineering", "Model Training", "Validation", "Deployment", "Monitoring"]
        elif domain == "software_architecture":
            process_flow = ["Requirements Analysis", "System Design", "Implementation", "Testing", "Deployment", "Maintenance"]
        elif domain == "business_strategy":
            process_flow = ["Market Analysis", "Strategy Planning", "Resource Allocation", "Execution", "Performance Tracking"]
        else:
            process_flow = key_words[:6] if len(key_words) >= 6 else ["Planning", "Design", "Implementation", "Testing", "Deployment"]

        # Create detailed process nodes
        for i, process in enumerate(process_flow):
            concept_id = f"process_{i+1}"
            concepts.append({
                "id": concept_id,
                "title": process,
                "description": f"Comprehensive {process.lower()} stage with detailed implementation",
                "level": 1,
                "parent": "root",
                "category": "process",
                "node_type": "process" if i < len(process_flow)-1 else "outcome",
                "what": f"Execute {process.lower()} with best practices",
                "why": f"Critical step for successful {main_topic.lower()}",
                "how": f"Systematic approach to {process.lower()}",
                "examples": [f"Example method for {process}", f"Tool/technique for {process}"],
                "metrics": [f"{process} completion: 100%", f"Quality score: >85%", f"Timeline adherence: >90%"],
                "details": [
                    f"Key deliverables for {process.lower()}",
                    f"Quality criteria and acceptance tests",
                    f"Dependencies and prerequisites"
                ],
                "processes": [
                    f"Step 1: {process} planning and preparation",
                    f"Step 2: {process} execution",
                    f"Step 3: {process} validation and review"
                ],
                "considerations": [
                    f"Common challenges in {process.lower()}",
                    f"Best practices for {process.lower()}"
                ],
                "tools_technologies": self._get_domain_tools(domain),
                "stakeholders": self._get_domain_stakeholders(domain)
            })

            relationships.append({
                "from": "root" if i == 0 else f"process_{i}",
                "to": concept_id,
                "type": "initiates" if i == 0 else "leads_to",
                "description": f"Sequential flow from {'start' if i == 0 else process_flow[i-1]} to {process}"
            })

        return {
            "main_topic": main_topic,
            "topic_description": f"Comprehensive {domain.replace('_', ' ')} implementation covering all critical aspects",
            "mindmap_type": "flowchart",
            "domain": domain,
            "complexity_level": "intermediate",
            "workflow_type": workflow_type,
            "concepts": concepts,
            "relationships": relationships
        }

    def _get_domain_tools(self, domain: str) -> List[str]:
        """Get relevant tools for domain"""
        tools_map = {
            "machine_learning": ["Python", "TensorFlow", "scikit-learn", "MLflow"],
            "software_architecture": ["Docker", "Kubernetes", "AWS/Azure", "MongoDB"],
            "business_strategy": ["Excel", "Tableau", "Salesforce", "HubSpot"],
            "education": ["LMS Platform", "Assessment Tools", "Video Conferencing", "Analytics"]
        }
        return tools_map.get(domain, ["Generic Tool 1", "Platform 2", "Framework 3"])

    def _get_domain_stakeholders(self, domain: str) -> List[str]:
        """Get relevant stakeholders for domain"""
        stakeholders_map = {
            "machine_learning": ["Data Scientists", "ML Engineers", "Product Managers"],
            "software_architecture": ["Software Architects", "DevOps Engineers", "QA Team"],
            "business_strategy": ["Business Analysts", "Executive Team", "Marketing"],
            "education": ["Instructors", "Students", "Academic Administration"]
        }
        return stakeholders_map.get(domain, ["Project Manager", "Technical Team", "Stakeholders"])

    def _validate_detailed_structured_data(self, data: Dict) -> bool:
        """Validate detailed structured data"""
        required_keys = ["title", "description", "layout_type", "nodes", "edges"]
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data["nodes"], list) or len(data["nodes"]) == 0:
            return False

        # Check first node has required detailed fields
        if data["nodes"]:
            node = data["nodes"][0]
            required_node_keys = ["id", "title", "description", "x", "y", "details", "processes", "considerations"]
            if not all(key in node for key in required_node_keys):
                return False

        return True

    def _create_detailed_fallback_concepts(self, prompt: str) -> Dict[str, Any]:
        """Create detailed fallback concept structure"""
        words = prompt.lower().split()
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'how', 'what', 'when', 'where', 'why', 'create', 'make', 'generate', 'mindmap', 'map'}
        key_words = [w for w in words if w not in stop_words and len(w) > 2][:5]

        main_topic = ' '.join(prompt.split()[0:3]).title()

        concepts = [{
            "id": "root",
            "title": main_topic,
            "description": f"Comprehensive analysis of {main_topic.lower()}",
            "level": 0,
            "parent": None,
            "category": "core",
            "details": [
                f"Core concept focusing on {main_topic.lower()}",
                "Requires systematic approach",
                "Multiple interconnected components"
            ],
            "processes": [
                "Initial analysis and planning",
                "Implementation and execution"
            ],
            "considerations": [
                "Consider all stakeholder requirements",
                "Ensure scalable and maintainable solution"
            ]
        }]

        relationships = []

        for i, word in enumerate(key_words):
            concept_id = f"concept_{i+1}"
            concepts.append({
                "id": concept_id,
                "title": word.title(),
                "description": f"Key component related to {word}",
                "level": 1,
                "parent": "root",
                "category": "component",
                "details": [
                    f"Essential element of {word}",
                    f"Directly impacts overall {main_topic.lower()}"
                ],
                "processes": [
                    f"Analyze {word} requirements",
                    f"Implement {word} solution"
                ],
                "considerations": [
                    f"Optimize {word} performance",
                    f"Ensure {word} reliability"
                ]
            })
            relationships.append({
                "from": "root",
                "to": concept_id,
                "type": "contains",
                "description": f"Main system contains {word} component"
            })

        return {
            "main_topic": main_topic,
            "topic_description": f"Comprehensive mindmap covering all aspects of {main_topic.lower()}",
            "mindmap_type": "hierarchical",
            "domain": "general",
            "complexity_level": "intermediate",
            "concepts": concepts,
            "relationships": relationships
        }

    def _create_detailed_fallback_structure(self, parsed_data: Dict) -> Dict[str, Any]:
        """Create detailed fallback structure with flowchart layout"""
        title = parsed_data.get("main_topic", "Mindmap")
        description = parsed_data.get("topic_description", "Comprehensive system analysis")
        concepts = parsed_data.get("concepts", [])
        domain = parsed_data.get("domain", "general")
        workflow_type = parsed_data.get("workflow_type", "sequential")

        nodes = []
        edges = []

        # Enhanced color scheme based on node types
        color_map = {
            "start": "#2c3e50",      # Dark blue-gray
            "process": "#3498db",     # Blue
            "decision": "#e74c3c",    # Red
            "outcome": "#27ae60",     # Green
            "checkpoint": "#f39c12",  # Orange
            "end": "#9b59b6"          # Purple
        }

        # Layout configurations for different workflow types
        if workflow_type == "flowchart" or workflow_type == "sequential":
            # Vertical flowchart layout
            start_x, start_y = 600, 150
            spacing_y = 200

            for i, concept in enumerate(concepts):
                node_type = concept.get("node_type", "process")
                level = concept.get("level", 0)

                # Calculate position for flowchart
                if level == 0:
                    x, y = start_x, start_y
                    width, height = 300, 100
                else:
                    x = start_x + (level - 1) * 50  # Slight offset for levels
                    y = start_y + (i * spacing_y)
                    width, height = 250, 80

                nodes.append({
                    "id": concept["id"],
                    "title": concept["title"][:30],
                    "description": concept.get("description", "Process component"),
                    "level": level,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "color": color_map.get(node_type, "#3498db"),
                    "shape": "diamond" if node_type == "decision" else "rectangle",
                    "category": concept.get("category", "process"),
                    "node_type": node_type,
                    "what": concept.get("what", "Process step"),
                    "why": concept.get("why", "Critical for success"),
                    "how": concept.get("how", "Systematic implementation"),
                    "examples": concept.get("examples", ["Example 1", "Example 2"]),
                    "metrics": concept.get("metrics", ["Metric 1", "Metric 2"]),
                    "details": concept.get("details", ["Detail 1", "Detail 2"]),
                    "processes": concept.get("processes", ["Step 1", "Step 2"]),
                    "considerations": concept.get("considerations", ["Consideration 1"]),
                    "tools_technologies": concept.get("tools_technologies", ["Tool 1"]),
                    "stakeholders": concept.get("stakeholders", ["Role 1"]),
                    "expanded": level == 0
                })

        # Create edges based on relationships
        relationships = parsed_data.get("relationships", [])
        for i, rel in enumerate(relationships):
            edges.append({
                "id": f"edge_{i+1}",
                "from": rel["from"],
                "to": rel["to"],
                "label": rel.get("type", "connects"),
                "description": rel.get("description", "Process flow"),
                "color": "#34495e",
                "weight": 3,
                "style": "solid"
            })

        return {
            "title": title,
            "description": description,
            "layout_type": "flowchart",
            "domain": domain,
            "complexity": parsed_data.get("complexity_level", "intermediate"),
            "workflow_type": workflow_type,
            "metadata": {
                "total_nodes": len(nodes),
                "max_depth": max([node.get("level", 0) for node in nodes], default=0),
                "creation_context": "Enhanced intelligent structure"
            },
            "nodes": nodes,
            "edges": edges
        }

    def _create_detailed_fallback_xml(self, structured_data: Dict, original_prompt: str) -> str:
        """Create detailed fallback XML if generation fails"""

        title = structured_data.get("title", "Mindmap")
        description = structured_data.get("description", "Comprehensive mindmap")
        timestamp = datetime.now().isoformat()

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<mindmap version="2.0" editable="true">
    <metadata>
        <title>{title}</title>
        <description>{description}</description>
        <created_at>{timestamp}</created_at>
        <layout_type>hierarchical</layout_type>
        <domain>general</domain>
        <complexity>intermediate</complexity>
        <total_nodes>1</total_nodes>
        <max_depth>0</max_depth>
        <generation_context>Generated from: {original_prompt}</generation_context>
    </metadata>
    <nodes>
        <node id="root" level="0" category="core" expanded="true">
            <content>
                <title>{title}</title>
                <description>{description}</description>
            </content>
            <position x="400" y="300" width="200" height="80"/>
            <style color="#2c3e50" shape="rectangle" border="solid"/>
            <details>
                <item>Core concept requiring systematic approach</item>
                <item>Multiple interconnected components</item>
            </details>
            <processes>
                <step>Initial analysis and planning</step>
                <step>Implementation and execution</step>
            </processes>
            <considerations>
                <point>Consider stakeholder requirements</point>
                <point>Ensure scalable solution</point>
            </considerations>
        </node>
    </nodes>
    <edges>
    </edges>
</mindmap>"""

# Utility functions remain the same with enhanced support
async def generate_mindmap_from_prompt(prompt: str, api_key: str = None) -> str:
    """Simple function to generate detailed mindmap XML from a prompt"""

    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set or api_key not provided")

    generator = MindmapGenerator(api_key)
    return await generator.generate_mindmap(prompt)

def save_mindmap_xml(xml_content: str, filename: str = None) -> str:
    """Save XML content to file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detailed_mindmap_{timestamp}.xml"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"💾 Enhanced mindmap saved to: {filename}")
    return filename

# Main execution
async def main():
    """Main function for command line usage"""
    import sys

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your detailed mindmap prompt: ")

    if not prompt.strip():
        print("❌ Empty prompt provided")
        sys.exit(1)

    try:
        start_time = time.time()
        xml_content = await generate_mindmap_from_prompt(prompt, api_key)
        end_time = time.time()

        filename = save_mindmap_xml(xml_content)

        print(f"\n📊 Enhanced generation completed in {end_time - start_time:.2f} seconds")
        print(f"📄 XML length: {len(xml_content)} characters")
        print(f"💾 Saved to: {filename}")

        print_xml = input("\nPrint detailed XML to console? (y/n): ").lower().startswith('y')
        if print_xml:
            print("\n" + "="*60)
            print("GENERATED DETAILED XML:")
            print("="*60)
            print(xml_content)
            print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())