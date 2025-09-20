import os
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
        file_uri = f"file://{file_path}"

        if content is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        text_document_item = self.lsp.TextDocumentItem(
            uri=file_uri,
            languageId=self.lsp._get_language_id(file_path),
            version=1,
            text=content
        )

        params = self.lsp.DidOpenTextDocumentParams(text_document_item)
        self.lsp.lsp_client.did_open(params)

        self.lsp.open_files[str(file_path)] = {
            'uri': file_uri,
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
        file_uri = f"file://{file_path}"

        params = self.lsp.DidCloseTextDocumentParams(text_document={'uri': file_uri})
        self.lsp.lsp_client.did_close(params)

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

        params = self.lsp.DidChangeTextDocumentParams(
            text_document={
                'uri': file_info['uri'],
                'version': file_info['version']
            },
            content_changes=changes
        )

        self.lsp.lsp_client.did_change(params)
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

        params = self.lsp.DidSaveTextDocumentParams(
            text_document={'uri': file_info['uri']}
        )

        self.lsp.lsp_client.did_save(params)
        self.lsp.logger.debug(f"Saved file: {file_path}")
