from typing import Union, List, Dict, Tuple
from pathlib import Path


class LSPFormatting:
    """Formatting component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def format_document(self, file_path: Union[str, Path], options: Dict = None) -> List[Dict]:
        """
        Format entire document

        Args:
            file_path: Path to file
            options: Formatting options

        Returns:
            List of text edits
        """
        if options is None:
            options = {
                'tabSize': 4,
                'insertSpaces': True,
                'trimTrailingWhitespace': True,
                'insertFinalNewline': True
            }

        return self.lsp._make_request(
            "textDocument/formatting",
            self.lsp.DocumentFormattingParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                options=options
            )
        )

    def format_range(self, file_path: Union[str, Path], range_start: Tuple[int, int],
                    range_end: Tuple[int, int], options: Dict = None) -> List[Dict]:
        """
        Format range in document

        Args:
            file_path: Path to file
            range_start: (line, char) start position
            range_end: (line, char) end position
            options: Formatting options

        Returns:
            List of text edits
        """
        if options is None:
            options = {
                'tabSize': 4,
                'insertSpaces': True,
                'trimTrailingWhitespace': True,
                'insertFinalNewline': True
            }

        return self.lsp._make_request(
            "textDocument/rangeFormatting",
            self.lsp.DocumentRangeFormattingParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                range={
                    'start': self.lsp.Position(line=range_start[0], character=range_start[1]),
                    'end': self.lsp.Position(line=range_end[0], character=range_end[1])
                },
                options=options
            )
        )

    def get_code_actions(self, file_path: Union[str, Path], range_start: Tuple[int, int],
                        range_end: Tuple[int, int], diagnostics: List[Dict] = None) -> List[Dict]:
        """
        Get available code actions for range

        Args:
            file_path: Path to file
            range_start: (line, char) start position
            range_end: (line, char) end position
            diagnostics: Associated diagnostics

        Returns:
            List of code actions
        """
        context = {}
        if diagnostics:
            context['diagnostics'] = diagnostics

        return self.lsp._make_request(
            "textDocument/codeAction",
            self.lsp.CodeActionParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                range={
                    'start': self.lsp.Position(line=range_start[0], character=range_start[1]),
                    'end': self.lsp.Position(line=range_end[0], character=range_end[1])
                },
                context=context
            )
        )
