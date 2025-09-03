from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class TemplateService:
    """Jinja2-based template service for LLM instructions"""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # Default to templates directory relative to this service
            template_dir = Path(__file__).parent.parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_llm_instructions(self,
                               persona: Any,
                               artist: Optional[Any] = None,
                               context: Optional[Dict[str, Any]] = None) -> str:
        """Render LLM system prompt with persona and artist merging"""

        template = self.env.get_template('llm_instructions/persona_system_prompt.jinja2')

        # Prepare context variables
        template_vars = {
            'persona': persona,
            'artist': artist,
            'has_artist': artist is not None,
            'has_artist_persona': artist and artist.persona,
            'system_prompt': persona.system_prompt or "",
            'artist_persona': artist.persona if artist and artist.persona else "",
        }

        # Add any additional context
        if context:
            template_vars.update(context)

        return template.render(**template_vars).strip()


# Global instance
template_service = TemplateService()
