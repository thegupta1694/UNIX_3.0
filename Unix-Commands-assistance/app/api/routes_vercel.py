from flask import Blueprint, request, jsonify, render_template
from app.core.agent_vercel import AgentSystem
from app.config import settings

# Create a blueprint for the API
api = Blueprint('api', __name__)

# Initialize the agent system
agent = AgentSystem()

# Initialize resources
def initialize_resources():
    """Initialize resources needed for the application."""
    try:
        # Test the connection to the Gemini API
        agent.test_connection()
        print("Gemini API connection successful")
        return True
    except Exception as e:
        print(f"Error initializing resources: {e}")
        return False

@api.route('/api/query', methods=['POST'])
def query():
    """Handle a query from the user."""
    try:
        data = request.json
        query_text = data.get('query', '')
        
        if not query_text:
            return jsonify({"error": "No query provided"}), 400
        
        # Analyze the query
        analysis = agent.query_analyzer_agent(query_text)
        
        # Retrieve relevant commands
        commands, context = agent.retrieval_agent(query_text, analysis)
        
        # Generate a response
        response = agent.response_generator_agent(query_text, analysis, context)
        
        return jsonify({
            "query": query_text,
            "analysis": analysis,
            "commands": commands,
            "response": response
        })
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/test', methods=['GET'])
def test():
    """Test the API connection."""
    try:
        result = agent.test_connection()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500 