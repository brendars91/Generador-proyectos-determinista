#!/usr/bin/env python3
"""
AGCCE RAG Indexer
Indexa el codebase usando smart-coding-mcp para busqueda semantica.

Uso: python rag_indexer.py [--reindex] [--status]
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Importar utilidades comunes
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
except ImportError:
    class Colors:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_info(msg): print(f"[i] {msg}")
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


# Archivo de estado del indice
INDEX_STATE_FILE = ".rag_index_state.json"


def load_index_state() -> Dict[str, Any]:
    """Carga estado del indice."""
    if os.path.exists(INDEX_STATE_FILE):
        with open(INDEX_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_indexed": None,
        "files_indexed": 0,
        "workspace": None,
        "status": "not_indexed"
    }


def save_index_state(state: Dict[str, Any]) -> None:
    """Guarda estado del indice."""
    with open(INDEX_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def get_project_files(extensions: List[str] = None) -> List[str]:
    """Obtiene lista de archivos del proyecto."""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.json', '.md', '.yaml', '.yml']
    
    files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.agent'}
    
    for root, dirs, filenames in os.walk('.'):
        # Excluir directorios
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files


def index_codebase(force: bool = False) -> Dict[str, Any]:
    """
    Indexa el codebase para busqueda semantica.
    
    Nota: Esta funcion prepara el estado local.
    La indexacion real se hace via smart-coding-mcp cuando se usa.
    """
    print(make_header("AGCCE RAG Indexer v1.0"))
    
    state = load_index_state()
    workspace = os.getcwd()
    
    # Verificar si ya esta indexado
    if not force and state.get("status") == "indexed" and state.get("workspace") == workspace:
        log_info(f"Codebase ya indexado en {state.get('last_indexed')}")
        log_info(f"Archivos: {state.get('files_indexed')}")
        print(f"\n{Colors.YELLOW}Usa --reindex para forzar re-indexacion{Colors.RESET}")
        return state
    
    log_info(f"Workspace: {workspace}")
    print()
    
    # Obtener archivos
    print(f"{Colors.BOLD}[1/3] Escaneando archivos...{Colors.RESET}")
    files = get_project_files()
    print(f"  Encontrados: {len(files)} archivos")
    
    # Clasificar por tipo
    print(f"\n{Colors.BOLD}[2/3] Clasificando por tipo...{Colors.RESET}")
    by_type = {}
    for f in files:
        ext = os.path.splitext(f)[1] or 'other'
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count}")
    
    # Actualizar estado
    print(f"\n{Colors.BOLD}[3/3] Actualizando estado de indexacion...{Colors.RESET}")
    
    state = {
        "last_indexed": datetime.now().isoformat(),
        "files_indexed": len(files),
        "workspace": workspace,
        "status": "indexed",
        "file_types": by_type,
        "indexed_files": files[:100]  # Guardar primeros 100 para referencia
    }
    
    save_index_state(state)
    
    log_pass(f"Indexacion completada: {len(files)} archivos")
    print(f"\n{Colors.GREEN}=== INDEXING COMPLETE ==={Colors.RESET}")
    
    # Nota sobre smart-coding-mcp
    print(f"\n{Colors.BLUE}[i] El indice semantico se actualiza automaticamente")
    print(f"    cuando se usa smart-coding-mcp para busquedas.{Colors.RESET}\n")
    
    return state


def get_index_status() -> None:
    """Muestra estado actual del indice."""
    print(make_header("RAG Index Status"))
    
    state = load_index_state()
    
    if state.get("status") != "indexed":
        log_warn("Codebase no indexado")
        print(f"\n{Colors.YELLOW}Ejecuta: python rag_indexer.py{Colors.RESET}")
        return
    
    print(f"{Colors.CYAN}Workspace:{Colors.RESET} {state.get('workspace')}")
    print(f"{Colors.CYAN}Ultimo indexado:{Colors.RESET} {state.get('last_indexed')}")
    print(f"{Colors.CYAN}Archivos:{Colors.RESET} {state.get('files_indexed')}")
    print(f"\n{Colors.BOLD}Por tipo:{Colors.RESET}")
    for ext, count in state.get('file_types', {}).items():
        print(f"  {ext}: {count}")
    
    log_pass("Indice activo")


def search_codebase(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Busca en el codebase usando busqueda semantica.
    
    Esta funcion es un wrapper que seria llamado internamente.
    La busqueda real usa smart-coding-mcp via el agente.
    """
    # Este es un placeholder - la busqueda real se hace via MCP
    return [{
        "note": "La busqueda semantica se ejecuta via smart-coding-mcp",
        "query": query,
        "max_results": max_results,
        "instruction": "Usa mcp_smart-coding-mcp_a_semantic_search con este query"
    }]


def main():
    if len(sys.argv) < 2:
        # Default: indexar
        index_codebase()
        return
    
    arg = sys.argv[1]
    
    if arg == "--reindex":
        index_codebase(force=True)
    elif arg == "--status":
        get_index_status()
    elif arg == "--help":
        print(f"Uso: python {sys.argv[0]} [--reindex | --status | --help]")
        print("\nOpciones:")
        print("  (sin args)  Indexa el codebase (si no esta indexado)")
        print("  --reindex   Fuerza re-indexacion completa")
        print("  --status    Muestra estado del indice")
    else:
        print(f"Opcion desconocida: {arg}")
        print(f"Usa --help para ver opciones")
        sys.exit(1)


if __name__ == '__main__':
    main()
