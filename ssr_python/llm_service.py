"""
LLM Service for Swift Sites - Ollama API Integration

Handles all LLM interactions for website generation and modification.
Each request is stateless - no conversation history is maintained.
Uses Ollama API (local or cloud) for LLM inference.
"""

import os
import re
import yaml
import logging
from ollama import Client

# Configure LLM-specific logger
llm_logger = logging.getLogger('llm_service')
llm_logger.setLevel(logging.DEBUG)

# File handler - logs to ssr_python/logs/llm_chat.log
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'llm_chat.log')

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
llm_logger.addHandler(file_handler)


class LLMService:
    """Service for interacting with Ollama API (local or cloud)."""

    def __init__(self):
        """Initialize the LLM service for Ollama (local or cloud)."""
        self.api_key = os.environ.get('OLLAMA_API_KEY', '')
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'https://ollama.com')
        self.model_name = os.environ.get('OLLAMA_MODEL', 'llama3:latest')
        self.timeout = float(os.environ.get('OLLAMA_TIMEOUT', 120))  # 2 minutes default

        # Configure client with optional API key for cloud
        if self.api_key:
            self.client = Client(
                host=self.base_url,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=self.timeout
            )
        else:
            # Local Ollama (no auth needed)
            self.client = Client(host=self.base_url, timeout=self.timeout)

        llm_logger.info(f"LLM Service initialized: model={self.model_name}, timeout={self.timeout}s")

        self.component_guide = self._load_component_guide()

    def _load_component_guide(self) -> str:
        """Load the LLM Component Guide as system context."""
        guide_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'LLM_COMPONENT_GUIDE.md'
        )

        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: LLM_COMPONENT_GUIDE.md not found at {guide_path}")
            return ""

    def _navigate_to_path(self, structure, path: list):
        """Navigate to a component by path array.

        Args:
            structure: The parsed YAML structure (list or dict)
            path: Array of keys/indices like [0, 'components', 1]

        Returns:
            The component at the path, or None if not found
        """
        current = structure
        for key in path:
            try:
                if isinstance(current, list) and isinstance(key, int):
                    current = current[key]
                elif isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            except (IndexError, KeyError, TypeError):
                return None
        return current

    def _extract_component_yaml(self, yaml_content: str, path: list) -> str:
        """Extract a component's YAML from the full document by path.

        Args:
            yaml_content: The full YAML content string
            path: Array of keys/indices to the component

        Returns:
            YAML string of just that component, or None if extraction fails
        """
        try:
            structure = yaml.safe_load(yaml_content)
            component = self._navigate_to_path(structure, path)
            if component is None:
                return None
            return yaml.dump(component, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except yaml.YAMLError:
            return None

    def _validate_yaml(self, yaml_content: str) -> dict:
        """Validate YAML syntax and basic structure.

        Args:
            yaml_content: The YAML string to validate

        Returns:
            dict with 'valid' (bool) and 'error' (str or None)
        """
        try:
            parsed = yaml.safe_load(yaml_content)

            # Check for required 'name' field in components
            if isinstance(parsed, list):
                for i, item in enumerate(parsed):
                    if isinstance(item, dict) and 'name' not in item:
                        return {'valid': False, 'error': f'Component at index {i} missing required "name" field'}
            elif isinstance(parsed, dict) and 'name' not in parsed:
                return {'valid': False, 'error': 'Component missing required "name" field'}

            return {'valid': True, 'error': None}
        except yaml.YAMLError as e:
            return {'valid': False, 'error': str(e)}

    def _build_system_prompt(self) -> str:
        """Build the system prompt with component guide."""
        return f"""You are an AI assistant for Swift Sites, a YAML-based website builder. Your role is to help users create and modify websites by generating valid YAML configurations.

## Your Capabilities
1. Create complete website structures from descriptions
2. Modify specific components when the user has one selected
3. Explain how components work and suggest improvements

## Component Guide
{self.component_guide}

## Output Rules

### For NEW Website Creation:
- Output complete YAML starting with `- name: page`
- Include all necessary nested components
- Use sensible defaults from the component guide
- Add `<!-- ACTION: create -->` comment at the START of your response

### For Component MODIFICATION:
- Output ONLY the modified component, not the entire page
- The component will be merged at the selected path
- Add `<!-- ACTION: modify -->` comment at the START of your response
- Output the component starting with `- name: component-name` or just `name: component-name`

### For Explanations/Questions:
- Provide helpful text response
- Do NOT output YAML unless explicitly asked
- Add `<!-- ACTION: explain -->` comment at the START of your response

### YAML Format Requirements:
- Always wrap YAML in ```yaml code blocks
- **CRITICAL: Use 2-space indentation for YAML hierarchy** - YAML requires proper indentation!
- Each nested level must be indented 2 spaces from its parent
- Include all required properties
- Use valid token values only (see component guide)
- Remember: `items`, `tabs`, `slides`, `columns` go at COMPONENT level, not inside `properties`

**INDENTATION EXAMPLE:**
```
- name: page          # Level 0
  properties:         # Level 1 (2 spaces)
    appearance:       # Level 2 (4 spaces)
      background:     # Level 3 (6 spaces)
        color: '#fff' # Level 4 (8 spaces)
  components:         # Level 1 (2 spaces)
    - name: heading   # Level 2 (4 spaces)
      properties:     # Level 3 (6 spaces)
        text: Hello   # Level 4 (8 spaces)
```

### Important Rules:
1. ALWAYS include the ACTION comment at the very start of your response
2. For modifications, only output the component being modified
3. Use realistic placeholder content (not "Lorem ipsum")
4. Follow the design token system for consistency
5. **Keep explanations minimal** - focus on outputting correct YAML. Brief 1-sentence intro is fine, but no lengthy explanations

### Output Format Examples

**CORRECT - Create action:**
<!-- ACTION: create -->
Here's your landing page with a hero section:

```yaml
- name: page
  properties:
    appearance: {{ background: {{ color: '#ffffff' }} }}
  components:
    - name: heading
      properties:
        text: Welcome
        typography: {{ size: xxxl, weight: bold }}
```

**CORRECT - Modify action:**
<!-- ACTION: modify -->
I've updated the heading to be red and larger:

```yaml
- name: heading
  properties:
    text: Welcome
    typography: {{ size: xxxl, weight: bold, color: '#ff0000' }}
```

**CORRECT - Error action (when you can't fulfill the request):**
<!-- ACTION: error -->
I cannot modify that component because [reason]. Please try [suggestion].

**WRONG - Never output multiple YAML blocks:**
<!-- ACTION: create -->
Here's option 1:
```yaml
...
```
Here's option 2:
```yaml
...
```
This is WRONG! Only include ONE yaml block per response.
"""

    def _build_prompt(self, message: str, current_yaml: str, selected_component: dict = None) -> str:
        """Build the user prompt with context."""
        prompt_parts = []

        # Current YAML state
        if current_yaml and current_yaml.strip():
            prompt_parts.append(f"""[CURRENT YAML STATE]
```yaml
{current_yaml}
```""")
        else:
            prompt_parts.append("[CURRENT YAML STATE]\nNo content yet - empty editor")

        # Selected component context
        if selected_component:
            component_path = selected_component.get('path', [])
            prompt_parts.append(f"""
[SELECTED COMPONENT]
Currently selected: {selected_component.get('name', 'unknown')} at path {component_path}
Component ID: {selected_component.get('id', 'unknown')}""")

            # Extract and include current component's YAML structure
            if current_yaml and component_path:
                component_yaml = self._extract_component_yaml(current_yaml, component_path)
                if component_yaml:
                    prompt_parts.append(f"""
[CURRENT COMPONENT STRUCTURE]
```yaml
{component_yaml}```
Modify this component based on the user's request. Preserve existing structure (items, tabs, slides, columns) unless asked to change them.""")

            prompt_parts.append("\nWhen modifying, output ONLY this component with updated properties.")
        else:
            prompt_parts.append("\n[SELECTED COMPONENT]\nNo component currently selected. For modifications, create or replace the entire page.")

        # User request
        prompt_parts.append(f"\n[USER REQUEST]\n{message}")

        return "\n".join(prompt_parts)

    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response to extract YAML and action type.

        Validates YAML syntax and basic structure before returning.
        If validation fails, returns an error action instead.
        """
        result = {
            "response": response_text,
            "yaml": None,
            "action": "explain"
        }

        # Extract action type from comment - check first 150 chars first (enforce placement)
        action_match = re.search(r'<!--\s*ACTION:\s*(\w+)\s*-->', response_text[:150], re.IGNORECASE)
        if not action_match:
            # Fallback: search entire response
            action_match = re.search(r'<!--\s*ACTION:\s*(\w+)\s*-->', response_text, re.IGNORECASE)

        if action_match:
            action = action_match.group(1).lower()
            if action in ('create', 'modify', 'explain', 'error'):
                result["action"] = action

        # Extract YAML from code blocks - try multiple patterns
        yaml_patterns = [
            r'```yaml\s*([\s\S]*?)```',      # Standard markdown
            r'```YAML\s*([\s\S]*?)```',      # Uppercase
            r'`{3,}yaml\s*([\s\S]*?)`{3,}',  # Variable backticks
        ]

        yaml_content = None
        for pattern in yaml_patterns:
            yaml_matches = re.findall(pattern, response_text, re.IGNORECASE)
            if yaml_matches:
                yaml_content = yaml_matches[0].strip()
                break

        if yaml_content:
            # Validate YAML syntax
            validation = self._validate_yaml(yaml_content)
            if validation['valid']:
                result["yaml"] = yaml_content
                # Replace response with simple message - discard LLM explanation text
                result["response"] = "Here's the generated YAML:"
            else:
                # YAML has issues but still return it with warning
                result["yaml"] = yaml_content
                result["response"] = "Generated YAML (with potential issues):"
                result["warning"] = f"YAML may have issues: {validation['error']}"
                llm_logger.warning(f"YAML validation warning: {validation['error']}")
        else:
            # No YAML found - keep original response for explain/error actions
            pass

        return result

    def chat(self, message: str, current_yaml: str, selected_component: dict = None) -> dict:
        """
        Send a message to the LLM and get a response.

        Args:
            message: User's message
            current_yaml: Current YAML content from editor
            selected_component: Currently selected component info (optional)
                - id: Component DOM ID
                - path: YAML path array
                - name: Component type name

        Returns:
            dict with keys:
                - response: Full AI response text
                - yaml: Extracted YAML string or None
                - action: "create", "modify", "explain", or "error"
                - error: Error message if action is "error"
        """
        try:
            # Build prompts
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_prompt(message, current_yaml, selected_component)

            # Build messages array for Ollama chat API
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]

            # Log request
            llm_logger.info("=" * 80)
            llm_logger.info("NEW CHAT REQUEST")
            llm_logger.info(f"User Message: {message}")
            llm_logger.info(f"Selected Component: {selected_component}")
            llm_logger.info(f"Current YAML Length: {len(current_yaml) if current_yaml else 0} chars")
            llm_logger.debug(f"USER PROMPT:\n{user_prompt}")

            # Call Ollama API (works for both local and cloud)
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'num_predict': int(os.environ.get('LLM_MAX_TOKENS', 4096)),
                    'temperature': float(os.environ.get('LLM_TEMPERATURE', 0.7)),
                }
            )

            # Extract response text
            response_text = response['message']['content']
            result = self._parse_response(response_text)

            # Log response
            llm_logger.info(f"RAW RESPONSE ({len(response_text)} chars):\n{response_text}")
            llm_logger.info(f"PARSED: action={result['action']}, yaml_length={len(result['yaml']) if result['yaml'] else 0}")
            if result.get('error'):
                llm_logger.error(f"Parse Error: {result['error']}")

            return result

        except ConnectionRefusedError as e:
            llm_logger.error(f"Connection refused: {str(e)}")
            return {
                "response": "Cannot connect to Ollama. Please ensure Ollama is running.",
                "yaml": None,
                "action": "error",
                "error": "Connection refused"
            }
        except Exception as e:
            error_msg = str(e)
            llm_logger.error(f"API error: {error_msg}")

            # Handle timeout errors
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                return {
                    "response": f"Request timed out after {self.timeout}s. The model may be overloaded. Try a simpler request.",
                    "yaml": None,
                    "action": "error",
                    "error": "Request timed out"
                }

            if 'unauthorized' in error_msg.lower() or '401' in error_msg:
                return {
                    "response": "AI authentication failed. Please contact the administrator.",
                    "yaml": None,
                    "action": "error",
                    "error": "Authentication failed"
                }
            return {
                "response": "Error communicating with the AI service. Please try again.",
                "yaml": None,
                "action": "error",
                "error": "API communication error"
            }


# Singleton instance for reuse
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service_instance

    if _llm_service_instance is None:
        _llm_service_instance = LLMService()

    return _llm_service_instance
