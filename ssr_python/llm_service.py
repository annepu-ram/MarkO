"""
LLM Service for Swift Sites — thin wrapper around the RAG agent providing
logging, response parsing, and error handling for the chat route.
"""

import os
import re
import yaml
import logging
from exceptions import CancelledError

llm_logger = logging.getLogger('llm_service')
llm_logger.setLevel(logging.DEBUG)

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
    """Thin wrapper over the RAG agent with logging and response parsing."""

    def __init__(self):
        from rag.agent.rag_agent import RAGAgent
        self.rag_agent = RAGAgent()
        self.rag_agent.load()
        llm_logger.info("LLMService initialized (RAG pipeline)")

    def _validate_yaml(self, yaml_content: str) -> dict:
        """Validate YAML syntax and basic structure."""
        try:
            parsed = yaml.safe_load(yaml_content)
            if isinstance(parsed, list):
                for i, item in enumerate(parsed):
                    if isinstance(item, dict) and 'name' not in item:
                        return {'valid': False, 'error': f'Component at index {i} missing required "name" field'}
            elif isinstance(parsed, dict) and 'name' not in parsed:
                return {'valid': False, 'error': 'Component missing required "name" field'}
            return {'valid': True, 'error': None}
        except yaml.YAMLError as e:
            return {'valid': False, 'error': str(e)}

    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response to extract YAML and action type."""
        result = {
            "response": response_text,
            "yaml": None,
            "action": "explain"
        }

        action_match = re.search(r'<!--\s*ACTION:\s*([\w-]+)\s*-->', response_text[:150], re.IGNORECASE)
        if not action_match:
            action_match = re.search(r'<!--\s*ACTION:\s*([\w-]+)\s*-->', response_text, re.IGNORECASE)

        if action_match:
            action = action_match.group(1).lower()
            if action in ('create', 'modify', 'explain', 'error', 'settings', 'delete', 'insert_child', 'insert_after'):
                result["action"] = action

        if result["action"] == 'delete':
            result["yaml"] = None
            return result

        yaml_patterns = [
            r'```yaml\s*([\s\S]*?)```',
            r'```YAML\s*([\s\S]*?)```',
            r'`{3,}yaml\s*([\s\S]*?)`{3,}',
        ]

        yaml_content = None
        for pattern in yaml_patterns:
            yaml_matches = re.findall(pattern, response_text, re.IGNORECASE)
            if yaml_matches:
                yaml_content = yaml_matches[0].strip()
                break

        if yaml_content:
            validation = self._validate_yaml(yaml_content)
            if validation['valid']:
                result["yaml"] = yaml_content
                result["response"] = "Here's the generated YAML:"
            else:
                result["yaml"] = yaml_content
                result["response"] = "Generated YAML (with potential issues):"
                result["warning"] = f"YAML may have issues: {validation['error']}"
                llm_logger.warning(f"YAML validation warning: {validation['error']}")

        return result

    def chat(self, message: str, current_yaml: str, selected_component: dict = None,
             selected_images: list = None, progress_fn=None,
             business_context: dict = None) -> dict:
        """Send a chat request through the RAG pipeline and parse the response.

        Returns a dict with keys: response, yaml, action, and optionally error/warning.
        """
        try:
            llm_logger.info("=" * 80)
            llm_logger.info("NEW CHAT REQUEST (RAG pipeline)")
            llm_logger.info(f"User Message: {message}")
            llm_logger.info(f"Selected Component: {selected_component}")
            llm_logger.info(f"Selected Images: {len(selected_images or [])} images")
            if business_context:
                llm_logger.info(
                    f"Business Context: business='{business_context.get('business_name')}' "
                    f"industry='{business_context.get('industry')}' "
                    f"variant='{business_context.get('variant_id')}' "
                    f"sections={len(business_context.get('sections') or [])}"
                )

            raw = self.rag_agent.chat(
                message, current_yaml, selected_component,
                selected_images=selected_images,
                progress_fn=progress_fn,
                business_context=business_context,
            )

            if progress_fn:
                progress_fn("Finalizing...")

            llm_logger.info(f"RAG RESPONSE ({len(raw)} chars):\n{raw}")
            result = self._parse_response(raw)
            llm_logger.info(
                f"PARSED: action={result['action']}, "
                f"yaml_length={len(result['yaml']) if result['yaml'] else 0}"
            )
            return result

        except CancelledError:
            raise
        except ConnectionRefusedError as e:
            llm_logger.error(f"Connection refused: {e}")
            return {
                "response": "Cannot reach the model backend.",
                "yaml": None,
                "action": "error",
                "error": "Connection refused",
            }
        except Exception as e:
            error_msg = str(e)
            llm_logger.error(f"Chat error: {error_msg}")
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                return {
                    "response": "Request timed out. The model may be overloaded. Try a simpler request.",
                    "yaml": None,
                    "action": "error",
                    "error": "Request timed out",
                }
            if 'unauthorized' in error_msg.lower() or '401' in error_msg:
                return {
                    "response": "Model backend authentication failed. Please contact the administrator.",
                    "yaml": None,
                    "action": "error",
                    "error": "Authentication failed",
                }
            return {
                "response": "Error communicating with the AI service. Please try again.",
                "yaml": None,
                "action": "error",
                "error": "API communication error",
            }


_llm_service_instance = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
