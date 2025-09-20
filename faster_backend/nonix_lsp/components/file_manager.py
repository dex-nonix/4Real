from typing import Union, List, Dict, Optional
from pathlib import Path


class LSPFileManager:
    """File operations component"""

    def __init__(self, lsp_instance):
        self.lsp = lsp_instance

    def open(self, file_path: Union[str, Path], content: Optional[str] = None) -> None:
        """
        Open a file in the LSP server

        Args:
            file_path: Path to the file
            content: File content (if None, reads from disk)
        """
        if not self.lsp.is_initialized:
            raise Exception("LSP server not initialized")

        file_path = Path(file_path).resolve()

        if content is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        # Create text document item
        text_document_item = self.lsp.structs.TextDocumentItem(
            uri=self.lsp._get_file_uri(file_path),
            languageId=self.lsp._get_language_id(file_path),
            version=1,
            text=content
        )

        # Send didOpen notification
        self.lsp.lsp_client.did_open(text_document_item)

        self.lsp.open_files[str(file_path)] = {
            'uri': self.lsp._get_file_uri(file_path),
            'content': content,
            'version': 1
        }

        self.lsp.logger.debug(f"Opened file: {file_path}")

    def close(self, file_path: Union[str, Path]) -> None:
        """
        Close a file in the LSP server

        Args:
            file_path: Path to the file
        """
        if not self.lsp.is_initialized:
            raise Exception("LSP server not initialized")

        file_path = Path(file_path).resolve()

        # Create text document identifier
        text_document = self.lsp.structs.TextDocumentIdentifier(
            uri=self.lsp._get_file_uri(file_path)
        )

        # Send didClose notification
        self.lsp.lsp_client.did_close(text_document)

        self.lsp.open_files.pop(str(file_path), None)
        self.lsp.logger.debug(f"Closed file: {file_path}")

    def change(self, file_path: Union[str, Path], changes: List[Dict]) -> None:
        """
        Notify server of file changes

        Args:
            file_path: Path to the file
            changes: List of text changes
        """
        if not self.lsp.is_initialized:
            raise Exception("LSP server not initialized")

        file_path = Path(file_path).resolve()
        file_info = self.lsp.open_files.get(str(file_path))

        if not file_info:
            raise Exception(f"File not opened: {file_path}")

        file_info['version'] += 1

        # Create versioned text document identifier
        text_document = self.lsp.structs.VersionedTextDocumentIdentifier(
            uri=file_info['uri'],
            version=file_info['version']
        )

        # Convert changes to proper structs
        content_changes = []
        for change in changes:
            if 'range' in change:
                range_obj = self.lsp.structs.Range(
                    start=self.lsp.structs.Position(
                        line=change['range']['start']['line'],
                        character=change['range']['start']['character']
                    ),
                    end=self.lsp.structs.Position(
                        line=change['range']['end']['line'],
                        character=change['range']['end']['character']
                    )
                )
                content_changes.append(
                    self.lsp.structs.TextDocumentContentChangeEvent(
                        range=range_obj,
                        text=change['text']
                    )
                )
            else:
                content_changes.append(
                    self.lsp.structs.TextDocumentContentChangeEvent(
                        text=change['text']
                    )
                )

        # Send didChange notification
        self.lsp.lsp_client.did_change(text_document, content_changes)
        self.lsp.logger.debug(f"Changed file: {file_path}")

    def save(self, file_path: Union[str, Path]) -> None:
        """
        Notify server that file was saved

        Args:
            file_path: Path to the file
        """
        if not self.lsp.is_initialized:
            raise Exception("LSP server not initialized")

        file_path = Path(file_path).resolve()
        file_info = self.lsp.open_files.get(str(file_path))

        if not file_info:
            raise Exception(f"File not opened: {file_path}")

        # Create text document identifier
        text_document = self.lsp.structs.TextDocumentIdentifier(
            uri=file_info['uri']
        )

        # Send didSave notification
        self.lsp.lsp_client.did_save(text_document)
        self.lsp.logger.debug(f"Saved file: {file_path}")
