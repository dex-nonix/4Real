from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from .openapi_generator import OpenAPIGenerator


class CompactApiGenerator:
    """Generates compact YAML overviews from the full OpenAPI spec."""

    def __init__(self, service_router):
        self.service_router = service_router
        self.openapi_generator = OpenAPIGenerator()

    async def _convert_openapi_to_compact_yaml(self, openapi_spec: Dict[str, Any], service_filter: str = '') -> str:
        """Convert full OpenAPI spec to compact YAML overview."""

        # Header
        if service_filter:
            header = f"# COMPACT API OVERVIEW - Filtered: {service_filter}\n"
        else:
            header = "# COMPACT API OVERVIEW - All Services\n"

        header += f"# Generated at: {datetime.now().isoformat()}\n"
        header += f"# Total endpoints: {await self._count_total_endpoints(openapi_spec)}\n"

        # Add link to full OpenAPI JSON
        if service_filter:
            header += f"# Full OpenAPI: /api/openapi.json?services={service_filter}\n"
        else:
            header += "# Full OpenAPI: /api/openapi.json\n"

        header += "\n"

        # Process paths
        paths = openapi_spec.get('paths', {})
        if not paths:
            return header + "# No endpoints found\n"

        # Group by service (extract from tags or path patterns)
        service_groups = await self._group_paths_by_service(paths)

        # Generate YAML for each service
        yaml_content = header
        for service_name, service_paths in service_groups.items():
            yaml_content += f"# {service_name.upper()} SERVICE\n"
            yaml_content += f"{service_name}:\n"

            # Group paths by logical sections
            sections = await self._group_paths_by_section(service_paths)

            for section_name, section_paths in sections.items():
                yaml_content += f"  {section_name}:\n"

                for path, methods in section_paths.items():
                    for method, method_info in methods.items():
                        if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                            summary = method_info.get('summary', '') or method_info.get('description',
                                                                                        '') or 'No description'
                            # Truncate long summaries
                            if len(summary) > 50:
                                summary = summary[:47] + "..."

                            # Format: METHOD /path  # Description
                            line = f"    {method.upper()} {path:<40} # {summary}"
                            yaml_content += line + "\n"

                yaml_content += "\n"  # Empty line between sections

            yaml_content += "\n"  # Empty line between services

        return yaml_content

    async def _count_total_endpoints(self, openapi_spec: Dict[str, Any]) -> int:
        """Count total number of endpoints in OpenAPI spec."""
        total = 0
        paths = openapi_spec.get('paths', {})
        for path, methods in paths.items():
            for method in methods:
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    total += 1
        return total

    async def _group_paths_by_service(self, paths: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Group paths by service name."""
        service_groups = {}

        for path, methods in paths.items():
            # Extract service name from path (first segment after removing leading slash)
            path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
            if path_parts:
                service_name = path_parts[0]
                if service_name not in service_groups:
                    service_groups[service_name] = {}
                service_groups[service_name][path] = methods

        return service_groups

    async def _group_paths_by_section(self, service_paths: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Group paths by logical section within a service."""
        sections = {}

        for path, methods in service_paths.items():
            # Extract section from path (second segment if available)
            path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
            if len(path_parts) > 1:
                section_name = path_parts[1]
            else:
                section_name = 'root'

            if section_name not in sections:
                sections[section_name] = {}
            sections[section_name][path] = methods

        return sections
