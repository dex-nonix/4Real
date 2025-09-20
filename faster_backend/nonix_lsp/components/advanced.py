from typing import Union, List, Dict, Tuple, Optional
from pathlib import Path


class LSPAdvanced:
    """Advanced features component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def get_call_hierarchy(self, file_path: Union[str, Path], line: int, char: int) -> List[Dict]:
        """
        Get call hierarchy for symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Call hierarchy items
        """
        position = self.lsp.Position(line=line, character=char)
        return self.lsp._make_request(
            "textDocument/prepareCallHierarchy",
            self.lsp.CallHierarchyPrepareParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                position=position
            )
        )

    def get_semantic_tokens(self, file_path: Union[str, Path]) -> Dict:
        """
        Get semantic tokens for document

        Args:
            file_path: Path to file

        Returns:
            Semantic tokens
        """
        return self.lsp._make_request(
            "textDocument/semanticTokens/full",
            self.lsp.SemanticTokensParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)}
            )
        )

    def get_inlay_hints(self, file_path: Union[str, Path], range_start: Optional[Tuple[int, int]] = None,
                       range_end: Optional[Tuple[int, int]] = None) -> List[Dict]:
        """
        Get inlay hints for document or range

        Args:
            file_path: Path to file
            range_start: Optional start position
            range_end: Optional end position

        Returns:
            List of inlay hints
        """
        params = self.lsp.InlayHintParams(
            text_document={'uri': self.lsp._get_file_uri(file_path)}
        )

        if range_start and range_end:
            params.range = {
                'start': self.lsp.Position(line=range_start[0], character=range_start[1]),
                'end': self.lsp.Position(line=range_end[0], character=range_end[1])
            }

        return self.lsp._make_request("textDocument/inlayHint", params)

    def get_inline_completions(self, file_path: Union[str, Path], line: int, char: int,
                              context: Optional[Dict] = None) -> Dict:
        """
        Get inline completions at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)
            context: Completion context

        Returns:
            Inline completion items
        """
        if context is None:
            context = {
                'selectedCompletionInfo': None,
                'triggerKind': 1  # Invoked
            }

        position = self.lsp.Position(line=line, character=char)
        return self.lsp._make_request(
            "textDocument/inlineCompletion",
            self.lsp.InlineCompletionParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                position=position,
                context=context
            )
        )
