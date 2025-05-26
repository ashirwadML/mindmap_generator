# Agentic Mindmap Generation System

## Overview

An intelligent agentic framework that transforms natural language prompts into structured XML mindmap representations using coordinated AI agents powered by Anthropic's API. The system employs a multi-stage pipeline with specialized agents to parse, structure, generate, and validate mindmap data.

## Architecture

### System Design Principles

- **Agentic Architecture**: Distributed agent system with specialized responsibilities
- **Streamlined Pipeline**: Direct validation-to-user flow for optimal performance
- **Semantic Intelligence**: Advanced NLP for hierarchical relationship extraction
- **Robust Validation**: Multi-layered quality assurance with self-correction capabilities

### Core Components

#### 1. Parser Agent
**Primary Function**: Natural language understanding and concept extraction

**Technical Capabilities**:
- Semantic tokenization and entity recognition
- Dependency parsing for hierarchical structures
- Intent classification (hierarchical, network, flow-based mindmaps)
- Coreference resolution for concept linking
- Named entity recognition for proper concept identification

**Input**: Raw natural language prompt
**Output**: Structured semantic data with extracted concepts and relationships

#### 2. Structure Agent
**Primary Function**: Knowledge graph construction and relationship mapping

**Technical Capabilities**:
- Directed acyclic graph (DAG) construction
- Edge detection and relationship typing
- Hierarchy inference through linguistic patterns
- Semantic clustering for related concepts
- Cycle detection and resolution algorithms

**Input**: Structured semantic data from Parser Agent
**Output**: Knowledge graph representation with nodes, edges, and hierarchical relationships

#### 3. XML Generator Agent
**Primary Function**: Template-based XML synthesis

**Technical Capabilities**:
- Schema-compliant XML construction
- Layout algorithm integration (force-directed, hierarchical)
- Coordinate assignment for spatial positioning
- Style attribute injection for visual rendering
- Template optimization for various mindmap types

**Input**: Knowledge graph from Structure Agent
**Output**: Raw XML mindmap representation

#### 4. Validation Agent
**Primary Function**: Quality assurance and final output delivery

**Technical Capabilities**:
- Schema compliance verification
- Semantic consistency checking
- Format optimization for target renderers
- Self-correction loops with iterative refinement
- Quality scoring and confidence metrics
- Direct user delivery

**Input**: Raw XML from Generator Agent
**Output**: Validated XML mindmap delivered to user

## Data Flow Pipeline

```
User Prompt → Parser Agent → Structured Data → Structure Agent →
Knowledge Graph → XML Generator → Raw XML → Validation Agent →
Validated XML → User
```

## Technical Specifications

### XML Schema Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mindmap version="1.0">
  <metadata>
    <title>{{mindmap_title}}</title>
    <created_at>{{timestamp}}</created_at>
    <layout_type>{{hierarchical|network|flow}}</layout_type>
  </metadata>
  <nodes>
    <node id="{{unique_id}}" level="{{hierarchy_level}}">
      <content>{{node_text}}</content>
      <position x="{{x_coord}}" y="{{y_coord}}"/>
      <style color="{{hex_color}}" shape="{{shape_type}}"/>
    </node>
  </nodes>
  <edges>
    <edge id="{{edge_id}}" source="{{source_node_id}}" target="{{target_node_id}}">
      <label>{{relationship_type}}</label>
      <style weight="{{thickness}}" color="{{hex_color}}"/>
    </edge>
  </edges>
</mindmap>
```

### Agent Communication Protocol

**Message Format**:
```json
{
  "agent_id": "string",
  "timestamp": "ISO_8601",
  "message_type": "data|error|status",
  "payload": {
    "data": "object",
    "metadata": "object"
  },
  "error_context": "optional_string"
}
```

### Error Handling & Recovery

#### Validation Agent Self-Correction Loop
```python
def validation_workflow(xml_input):
    validation_result = validate_schema(xml_input)

    if validation_result.is_valid():
        return deliver_to_user(xml_input)
    else:
        corrected_xml = self_correct(xml_input, validation_result.errors)
        return validation_workflow(corrected_xml)  # Recursive correction
```

#### Rollback Mechanisms
- **Agent-level rollback**: Each agent maintains state checkpoints
- **Pipeline rollback**: Full pipeline restart on critical failures
- **Graceful degradation**: Simplified output on repeated validation failures

## Quality Assurance

### Multi-Stage Validation
1. **Syntax Validation**: XML well-formedness
2. **Schema Validation**: Compliance with mindmap XSD
3. **Semantic Validation**: Logical relationship consistency
4. **Visual Validation**: Rendering compatibility checks

### Quality Metrics
- **Completeness Score**: Percentage of concepts captured
- **Accuracy Score**: Relationship mapping precision
- **Consistency Score**: Internal logical coherence
- **Renderability Score**: Visual output quality assessment

## Performance Optimizations

### Caching Strategies
- **Pattern Recognition Cache**: Common mindmap structures
- **Validation Rule Cache**: Frequently used validation patterns
- **Template Cache**: Pre-optimized XML templates

### Asynchronous Processing
- **Non-blocking agent communication**
- **Parallel validation checks**
- **Streaming output for large mindmaps**

## Usage Examples

### Usage
```python
pip install -r requirements.txt
python run_server.py
```
