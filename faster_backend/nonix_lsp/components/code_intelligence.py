from typing import Union, List, Dict, Tuple
from pathlib import Path


class LSPCodeIntelligence:
    """Code intelligence component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def get_definition(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Get definition location for symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Definition location information
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("definition", text_document_position)

    def find_references(self, file_path: Union[str, Path], line: int, char: int,
                       include_declaration: bool = True) -> List[Dict]:
        """
        Find all references to symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)
            include_declaration: Include declaration in results

        Returns:
            List of reference locations
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("references", text_document_position)

    def get_hover_info(self, file_path: Union[str, Path], line: int, char: int) -> Dict:
        """
        Get hover information for symbol at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)

        Returns:
            Hover information
        """
        position = self.lsp.structs.Position(line=line, character=char)
        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("hover", text_document_position)

    def get_completions(self, file_path: Union[str, Path], line: int, char: int,
                       trigger_character: str = None) -> Dict:
        """
        Get completion suggestions at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)
            trigger_character: Character that triggered completion

        Returns:
            Completion items
        """
        position = self.lsp.structs.Position(line=line, character=char)

        # Create completion context if trigger character provided
        context = None
        if trigger_character:
            context = self.lsp.structs.CompletionContext(
                trigger_kind=self.lsp.structs.CompletionTriggerKind.TriggerCharacter,
                trigger_character=trigger_character
            )

        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("completion", text_document_position, context)

    def get_signature_help(self, file_path: Union[str, Path], line: int, char: int,
                          trigger_character: str = None) -> Dict:
        """
        Get signature help at position

        Args:
            file_path: Path to file
            line: Line number (0-indexed)
            char: Character position (0-indexed)
            trigger_character: Character that triggered signature help

        Returns:
            Signature help information
        """
        position = self.lsp.structs.Position(line=line, character=char)

        text_document_position = self.lsp.structs.TextDocumentPosition(
            text_document=self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path)),
            position=position
        )

        return self.lsp._make_request("signatureHelp", text_document_position)

    def get_document_symbols(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Get all symbols in a document

        Args:
            file_path: Path to file

        Returns:
            List of document symbols
        """
        text_document = self.lsp.structs.TextDocumentIdentifier(uri=self.lsp._get_file_uri(file_path))

        return self.lsp._make_request("documentSymbol", text_document)

    def get_workspace_symbols(self, query: str) -> List[Dict]:
        """
        Search for symbols in workspace

        Args:
            query: Symbol search query

        Returns:
            List of workspace symbols
        """
        return self.lsp._make_request("workspace_symbol", query)
