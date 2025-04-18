import json
import google.generativeai as genai
from google.genai import types
from google.generativeai.types import GenerationConfig
from app.config import settings

class AgentSystem:
    def __init__(self):
        """Initialize the agent system."""
        try:
            # Configure the API key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Initialize the model
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            # Create a proper generation config
            self.generation_config = GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini API: {str(e)}")
            
        self.query_optimizer = None
        self.command_graph = None

    def test_connection(self):
        """Test the API connection with a simple request."""
        response = self.model.generate_content(
            "test",
            generation_config=self.generation_config
        )
        return response.text
    
    def query_analyzer_agent(self, query, embedding_manager=None, data_manager=None):
        """Agent responsible for understanding the user's intent and reformulating the query."""
        # Simplified version for Vercel deployment
        prompt = f"""
        You are a Query Analyzer Agent. Your role is to:
        1. Understand the true intent behind a user's UNIX command query
        2. Identify key concepts and command requirements
        3. Reformulate or expand the query if needed for better retrieval
        4. Return a structured analysis that will help with command retrieval
        
        User Query: {query}
        
        Respond with a JSON object with these fields:
        - intent: the main purpose of the query
        - keywords: key terms for retrieval
        - reformulated_query: an improved version of the original query
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        
        try:
            # Remove any markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            analysis = json.loads(response_text.strip())
            return analysis
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            return {
                "intent": "unknown", 
                "keywords": [query], 
                "reformulated_query": query,
                "original_query": query
            }
    
    def retrieval_agent(self, query, analysis, embedding_manager=None, data_manager=None):
        """Agent responsible for retrieving relevant commands based on the query."""
        # Simplified version for Vercel deployment
        keywords = analysis.get("keywords", [query])
        intent = analysis.get("intent", "")
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # Use the reformulated query if available
        if "reformulated_query" in analysis and analysis["reformulated_query"] != query:
            main_query = analysis["reformulated_query"]
        else:
            main_query = query
            
        # For Vercel deployment, we'll return a simple response
        prompt = f"""
        You are a UNIX Command Assistant. Based on the following query and analysis, 
        provide a list of relevant UNIX commands that would help accomplish the task.
        
        Query: {main_query}
        Intent: {intent}
        Keywords: {', '.join(keywords)}
        
        Respond with a JSON object containing:
        - commands: an array of command objects, each with:
          - name: the command name
          - description: a brief description
          - example: a simple example of usage
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        
        try:
            # Remove any markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result.get("commands", []), "Generated command suggestions"
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            return [], "Error generating command suggestions"
    
    def response_generator_agent(self, query, analysis, context):
        """Agent responsible for generating the final response to the user."""
        prompt = f'''
You are a UNIX Command Assistant. Format your response using strict markdown structure:

### Command Overview
Brief description of the command's purpose and functionality.

### Syntax
```bash
command [options] arguments
```

### Key Options
- `-option`: Description
- `--long-option`: Description

### Examples
```bash
# Example 1: Basic usage
command -option value

# Example 2: Advanced usage
command --long-option value
```

### Notes
Important considerations or warnings

Based on the query: "{query}"
Context: {context}

Remember to:
1. Use proper heading levels (###)
2. Wrap all commands in `backticks`
3. Use ```bash for code blocks
4. Use bullet points with - for lists
5. Keep explanations clear and concise
6. Add descriptive comments in code examples
'''

        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        
        # Clean and format the response
        response_text = response.text.strip()
        if not response_text.startswith("### "):
            response_text = "### Command Overview\n" + response_text
        
        return response_text 