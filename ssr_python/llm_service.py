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
        self.timeout = float(os.environ.get('OLLAMA_TIMEOUT', 300))  # 5 minutes default

        # RAG toggle — when enabled, routes chat through RAG pipeline instead of legacy
        self.use_rag = os.environ.get('RAG_ENABLED', 'false').lower() == 'true'
        if self.use_rag:
            from rag.agent.rag_agent import RAGAgent
            self.rag_agent = RAGAgent()
            self.rag_agent.load()
            llm_logger.info("RAG pipeline enabled and loaded")

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

        llm_logger.info(f"LLM Service initialized: model={self.model_name}, timeout={self.timeout}s, rag={self.use_rag}")

        self.component_guide = self._load_component_guide()

    def _load_component_guide(self) -> str:
        """Load the LLM Component Guide as system context."""
        guide_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config', 'COMPONENT_SYNTAX_REFERENCE.md'
        )

        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: COMPONENT_SYNTAX_REFERENCE.md not found at {guide_path}")
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

### For Component DELETION:
- When user asks to remove/delete a selected component
- Do NOT output any YAML — the selected component will be removed from the page
- Add `<!-- ACTION: delete -->` comment at the START of your response
- REQUIRES a component to be selected — if none is selected, use ACTION: error instead

### For INSERTING a Component as Child:
- When user asks to add a new component INSIDE a selected container (page, layout-row, layout-column, form, etc.)
- Output the new component YAML (just the component to insert, not the whole page)
- Add `<!-- ACTION: insert_child -->` comment at the START of your response
- REQUIRES a container to be selected. If selected component is NOT a container, use insert_after instead

### For INSERTING a Component After Selection:
- When user asks to add a new component AFTER or BELOW the selected component
- Output the new component YAML (just the component to insert)
- Add `<!-- ACTION: insert_after -->` comment at the START of your response
- REQUIRES a component to be selected — if none is selected, use ACTION: create instead

### Choosing the Right Action:
- "delete/remove this" → ACTION: delete
- "add X inside this section/column/row" → ACTION: insert_child (container selected)
- "add X after/below this" → ACTION: insert_after
- "change/update/modify this" → ACTION: modify
- "create/build a page/website" → ACTION: create

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

**CORRECT - Delete action:**
<!-- ACTION: delete -->
I've removed the heading component.

**CORRECT - Insert child action (add inside a container):**
<!-- ACTION: insert_child -->
I've added a paragraph inside the selected column:

```yaml
- name: paragraph
  properties:
    text: Welcome to our website
    typography: {{ size: md }}
```

**CORRECT - Insert after action (add below/after):**
<!-- ACTION: insert_after -->
I've added a button after the selected heading:

```yaml
- name: button
  properties:
    text: Get Started
    appearance: {{ background: {{ color: '#3b82f6' }} }}
```

**CORRECT - Error action (when you can't fulfill the request):**
<!-- ACTION: error -->
I cannot modify that component because [reason]. Please try [suggestion].

**CORRECT - Settings action (when user asks for SEO or site settings):**
<!-- ACTION: settings -->
Here are the suggested SEO settings:

```yaml
metaDescription: "A compelling description for search engines"
ogTitle: "An engaging social sharing title"
```

### For Site Settings Generation:
- When user asks to "generate SEO", "create meta description", or "suggest settings"
- Add `<!-- ACTION: settings -->` comment at the START
- Output a YAML block with `metaDescription` and/or `ogTitle` fields
- Keep `metaDescription` to 150-160 characters
- Make `ogTitle` engaging for social media sharing

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

    def _build_image_context(self, selected_images: list) -> str:
        """Build image context block for the LLM prompt."""
        if not selected_images:
            return ""

        lines = ["[AVAILABLE IMAGES - Use these URLs in image components]"]
        for i, img in enumerate(selected_images, 1):
            url = img.get('url', '')
            alt = img.get('altText', '')
            orientation = img.get('orientation', 'unknown')
            photographer = img.get('photographer', '')
            credit = f" (Photo by {photographer})" if photographer else ""
            lines.append(f"{i}. {url} — \"{alt}\" [{orientation}]{credit}")

        lines.append("""
Match images to sections by their descriptions and orientation:
- Use [landscape] images for hero banners, full-width sections, backgrounds
- Use [portrait] images for sidebars, team cards, testimonial avatars
- Use [square] images for product cards, grid items, logos
Do NOT use any external URLs. Only use the images listed above.""")
        return "\n".join(lines)

    def _build_prompt(self, message: str, current_yaml: str, selected_component: dict = None,
                      selected_images: list = None) -> str:
        """Build the user prompt with context."""
        prompt_parts = []

        # Available images context
        image_ctx = self._build_image_context(selected_images or [])
        if image_ctx:
            prompt_parts.append(image_ctx)

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
            component_name = selected_component.get('name', 'unknown')

            # Determine if selected component is a container
            container_names = ['page', 'layout-row', 'layout-column', 'columnsgrid',
                               'form', 'video-background', 'hamburger', 'tabs',
                               'accordion', 'carousel', 'ticker']
            is_container = component_name in container_names

            prompt_parts.append(f"""
[SELECTED COMPONENT]
Currently selected: {component_name} at path {component_path}
Component ID: {selected_component.get('id', 'unknown')}
Is container (can hold children): {is_container}""")

            # Extract and include current component's YAML structure
            if current_yaml and component_path:
                component_yaml = self._extract_component_yaml(current_yaml, component_path)
                if component_yaml:
                    prompt_parts.append(f"""
[CURRENT COMPONENT STRUCTURE]
```yaml
{component_yaml}```
Modify this component based on the user's request. Preserve existing structure (items, tabs, slides, columns) unless asked to change them.""")

            prompt_parts.append("\nWhen modifying, output ONLY this component with updated properties. You can also delete it, or insert new components as children or after it.")
        else:
            prompt_parts.append("\n[SELECTED COMPONENT]\nNo component currently selected. For modifications, create or replace the entire page. Cannot use delete, insert_child, or insert_after without a selection.")

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
        action_match = re.search(r'<!--\s*ACTION:\s*([\w-]+)\s*-->', response_text[:150], re.IGNORECASE)
        if not action_match:
            # Fallback: search entire response
            action_match = re.search(r'<!--\s*ACTION:\s*([\w-]+)\s*-->', response_text, re.IGNORECASE)

        if action_match:
            action = action_match.group(1).lower()
            if action in ('create', 'modify', 'explain', 'error', 'settings', 'delete', 'insert_child', 'insert_after'):
                result["action"] = action

        # Delete action needs no YAML — operates on selected component
        if result["action"] == 'delete':
            result["yaml"] = None
            return result

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

    def chat(self, message: str, current_yaml: str, selected_component: dict = None,
             selected_images: list = None, progress_fn=None) -> dict:
        """
        Send a message to the LLM and get a response.

        Args:
            message: User's message
            current_yaml: Current YAML content from editor
            selected_component: Currently selected component info (optional)
            selected_images: Downloaded images with local URLs for context (optional)
            progress_fn: Callback for progress status updates

        Returns:
            dict with keys:
                - response: Full AI response text
                - yaml: Extracted YAML string or None
                - action: "create", "modify", "explain", or "error"
                - error: Error message if action is "error"
        """
        try:
            # RAG pipeline path
            if self.use_rag:
                llm_logger.info("=" * 80)
                llm_logger.info("NEW CHAT REQUEST (RAG pipeline)")
                llm_logger.info(f"User Message: {message}")
                llm_logger.info(f"Selected Component: {selected_component}")
                llm_logger.info(f"Selected Images: {len(selected_images or [])} images")
                raw = self.rag_agent.chat(message, current_yaml, selected_component,
                                          selected_images=selected_images, progress_fn=progress_fn)
                if progress_fn:
                    progress_fn("Finalizing...")
                llm_logger.info(f"RAG RESPONSE ({len(raw)} chars):\n{raw}")
                result = self._parse_response(raw)
                llm_logger.info(f"PARSED: action={result['action']}, yaml_length={len(result['yaml']) if result['yaml'] else 0}")
                return result

            # Legacy pipeline path
            if progress_fn:
                progress_fn("Generating response...")
            # Build prompts
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_prompt(message, current_yaml, selected_component,
                                             selected_images=selected_images)

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
