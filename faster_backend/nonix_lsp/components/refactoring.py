from typing import Union, Dict
from pathlib import Path


class LSPRefactoring:
    """Refactoring component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def rename_symbol(self, file_path: Union[str, Path], line: int, char: int,
                     new_name: str) -> Dict:
        """
        Rename symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)
            new_name: New symbol name

        Returns:
            Workspace edit with changes
        """
        position = self.lsp.Position(line=line, character=char)
        return self.lsp._make_request(
            "textDocument/rename",
            self.lsp.RenameParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                position=position,
                new_name=new_name
            )
        )

    def prepare_rename(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Check if rename is possible at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Rename preparation info
        """
        position = self.lsp.Position(line=line, character=char)
        return self.lsp._make_request(
            "textDocument/prepareRename",
            self.lsp.PrepareRenameParams(
                text_document={'uri': self.lsp._get_file_uri(file_path)},
                position=position
            )
        )
