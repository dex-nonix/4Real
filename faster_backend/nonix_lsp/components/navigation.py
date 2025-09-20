from typing import Union, List, Dict, Tuple
from pathlib import Path


class LSPNavigation:
    """Navigation component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def go_to_declaration(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Go to declaration of symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Declaration location
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("declaration", text_document_position)

    def go_to_type_definition(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Go to type definition of symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Type definition location
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("typeDefinition", text_document_position)

    def go_to_implementation(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Go to implementation of symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Implementation location
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("implementation", text_document_position)

    def get_document_highlights(self, file_path: Union[str, Path], line: int, char: int) -> List[Dict]:
        """
        Get document highlights for symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            List of document highlights
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("documentHighlight", text_document_position)

    def get_folding_ranges(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Get folding ranges for document

        Args:
            file_path: Path to file

        Returns:
            List of folding ranges
        """
        text_document = self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path))

        return self.lsp._make_request("folding_range", text_document)

    def get_selection_ranges(self, file_path: Union[str, Path], positions: List[Tuple[int, int]]) -> List[Dict]:
        """
        Get selection ranges for positions

        Args:
            file_path: Path to file
            positions: List of (line, char) positions

        Returns:
            List of selection ranges
        """
        text_document = self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path))

        request_id = self.lsp.lsp_client.selectionRange(
            text_document,
            [self.lsp.structs.Position(line=pos[0], character=pos[1]) for pos in positions]
        )
