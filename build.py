import os
import re
import shlex
import subprocess
import sys
import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from matplotlib.ticker import FuncFormatter

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def error(msg: str):
    print(f"{Colors.RED}{msg}{Colors.RESET}")

def success(msg: str):
    print(f"{Colors.GREEN}{msg}{Colors.RESET}")

def info(msg: str):
    print(f"{Colors.BLUE}{msg}{Colors.RESET}")

def warning(msg: str):
    print(f"{Colors.YELLOW}{msg}{Colors.RESET}")

SOURCE_MD_FILE = "guia.md"
DOCX_FILE = "guia.docx"
REFERENCE_DOC = "PlantillaGuia.docx"  # optional; used only if it exists


# ----------------------------
# Models
# ----------------------------

@dataclass
class PlotDirective:
    kind: str
    file: str
    params: Dict[str, str]
    raw_block: str


# ----------------------------
# Helpers
# ----------------------------

def ensure_working_directory():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)


def check_python_dependencies():
    try:
        import numpy  # noqa: F401
        import matplotlib  # noqa: F401
    except Exception:
        error("Faltan dependencias de Python (numpy/matplotlib).")
        info("Instálalas con:")
        print("  python -m pip install numpy matplotlib")
        sys.exit(1)


def parse_key_value_lines(block_text: str) -> Dict[str, str]:
    """
    Parse lines with key=value. Supports quoted values.
    Ignores empty lines.
    """
    params: Dict[str, str] = {}
    lines = [ln.strip() for ln in block_text.splitlines()]

    for ln in lines:
        if not ln:
            continue
        if ln.startswith("#"):
            continue
        if "=" not in ln:
            # ignore malformed lines rather than crash hard
            continue

        key, value = ln.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Allow quotes in values: title="some text"
        # shlex handles quotes nicely.
        try:
            tokens = shlex.split(value)
            value = tokens[0] if tokens else ""
        except Exception:
            # fallback: raw value
            pass

        params[key] = value

    return params


def extract_plot_directives(markdown_text: str) -> List[PlotDirective]:
    """
    Extract blocks like:
    <!-- plot
    kind=func2d
    file=graficas/xxx.png
    expr=...
    -->
    """
    directives: List[PlotDirective] = []

    pattern = r"<!--\s*plot\s*(.*?)-->"
    matches = re.findall(pattern, markdown_text, flags=re.DOTALL | re.IGNORECASE)

    for raw in matches:
        params = parse_key_value_lines(raw)
        kind = params.get("kind", "").strip()
        file_ = params.get("file", "").strip()

        if not kind or not file_:
            # skip incomplete directives
            continue

        directives.append(PlotDirective(kind=kind, file=file_, params=params, raw_block=raw))

    return directives


def extract_markdown_image_paths(markdown_text: str) -> List[str]:
    """
    Extract markdown image paths from patterns like:
    ![alt text](path)
    """
    # simple regex good enough for our controlled input
    pattern = r"!\[[^\]]*\]\(([^)]+)\)"
    paths = re.findall(pattern, markdown_text)
    # strip optional title after path, e.g. (path "title")
    cleaned = []
    for p in paths:
        p = p.strip()
        # Remove possible title segment: path "title"
        if " " in p:
            p = p.split(" ", 1)[0].strip()
        cleaned.append(p)
    return cleaned


def ensure_parent_folder(file_path: str):
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def safe_eval_numpy_expr(expr: str, variables: Dict[str, object]):
    """
    Evaluate a numpy expression safely-ish (no builtins).
    This is NOT a full sandbox, but it blocks obvious builtins and keeps
    evaluation constrained to provided names.
    """
    allowed_globals = {}
    return eval(expr, allowed_globals, variables)  # noqa: S307


def to_float(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default


def to_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


# ----------------------------
# Plot generation (NumPy + Matplotlib)
# ----------------------------

def generate_func2d(d: PlotDirective):
    import numpy as np
    import matplotlib.pyplot as plt

    expr = d.params.get("expr", "").strip()
    if not expr:
        raise ValueError("Falta 'expr' en la directiva de tipo func2d.")

    xmin = to_float(d.params.get("xmin"), -5.0)
    xmax = to_float(d.params.get("xmax"), 5.0)
    n = to_int(d.params.get("n"), 400)

    title = d.params.get("title", "Gráfica")
    xlabel = d.params.get("xlabel", "x")
    ylabel = d.params.get("ylabel", "y")

    x = np.linspace(xmin, xmax, n)

    # Provide a small, useful namespace for expressions
    variables = {
        "np": np,
        "x": x,
        # common functions for convenience
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
    }

    y = safe_eval_numpy_expr(expr, variables)

    # Ensure numeric array
    y = np.asarray(y, dtype=float)

    # Mask non-finite values to avoid ugly spikes
    y[~np.isfinite(y)] = np.nan

    ensure_parent_folder(d.file)

    plt.figure()
    ax = plt.gca()
    ax.plot(x, y)

    # Center axes at origin
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    # Custom axis labels with padding
    ax_xlim = ax.get_xlim()
    ax_ylim = ax.get_ylim()
    x_padding = 0.02 * (ax_xlim[1] - ax_xlim[0])
    y_padding = 0.02 * (ax_ylim[1] - ax_ylim[0])

    # X-axis labels
    ax.text(ax_xlim[0], 0, f"-{xlabel}", ha="right", va="center")
    ax.text(ax_xlim[1], 0, xlabel, ha="left", va="center")

    # Y-axis labels (using f(x) notation for function plots)
    ax.text(x_padding, ax_ylim[1] - y_padding, "f(x)", ha="left", va="bottom")
    ax.text(x_padding, ax_ylim[0] + y_padding, "-f(x)", ha="left", va="top")

    # Hide zero labels to reduce clutter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: "" if np.isclose(val, 0) else f"{val:g}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: "" if np.isclose(val, 0) else f"{val:g}"))

    # plt.title(title)  # Commented out to avoid duplication with f(x) axis labels
    plt.grid(True)

    plt.savefig(d.file, dpi=300, bbox_inches="tight")
    plt.close()


def generate_vector2d(d: PlotDirective):
    import numpy as np
    import matplotlib.pyplot as plt

    fx_expr = d.params.get("Fx", "").strip()
    fy_expr = d.params.get("Fy", "").strip()
    if not fx_expr or not fy_expr:
        raise ValueError("Faltan 'Fx' o 'Fy' en la directiva de tipo vector2d.")

    xmin = to_float(d.params.get("xmin"), -3.0)
    xmax = to_float(d.params.get("xmax"), 3.0)
    ymin = to_float(d.params.get("ymin"), -3.0)
    ymax = to_float(d.params.get("ymax"), 3.0)
    n = to_int(d.params.get("n"), 20)

    title = d.params.get("title", "Campo vectorial")

    x = np.linspace(xmin, xmax, n)
    y = np.linspace(ymin, ymax, n)
    X, Y = np.meshgrid(x, y)

    variables = {
        "np": np,
        "x": X,
        "y": Y,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
    }

    U = safe_eval_numpy_expr(fx_expr, variables)
    V = safe_eval_numpy_expr(fy_expr, variables)

    U = np.asarray(U, dtype=float)
    V = np.asarray(V, dtype=float)

    U[~np.isfinite(U)] = 0.0
    V[~np.isfinite(V)] = 0.0

    ensure_parent_folder(d.file)

    plt.figure()
    ax = plt.gca()

    # Center axes at origin
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    ax.quiver(X, Y, U, V)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)

    # Custom axis labels for vector field
    ax_xlim = ax.get_xlim()
    ax_ylim = ax.get_ylim()
    x_padding = 0.02 * (ax_xlim[1] - ax_xlim[0])
    y_padding = 0.02 * (ax_ylim[1] - ax_ylim[0])

    ax.text(ax_xlim[0], 0, "-x", ha="right", va="center")
    ax.text(ax_xlim[1], 0, "x", ha="left", va="center")
    ax.text(x_padding, ax_ylim[1] - y_padding, "y", ha="left", va="bottom")
    ax.text(x_padding, ax_ylim[0] + y_padding, "-y", ha="left", va="top")

    # Hide zero labels
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: "" if np.isclose(val, 0) else f"{val:g}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: "" if np.isclose(val, 0) else f"{val:g}"))

    plt.savefig(d.file, dpi=300, bbox_inches="tight")
    plt.close()


def generate_plots(directives: List[PlotDirective]):
    if not directives:
        info("No se encontraron directivas de gráficas (<!-- plot ... -->).")
        return

    info(f"Se encontraron {len(directives)} directiva(s) de gráficas. Generando...\n")

    for i, d in enumerate(directives, start=1):
        info(f"  -> ({i}/{len(directives)}) Generando: {d.file}  [kind={d.kind}]")
        kind = d.kind.lower().strip()

        if kind == "func2d":
            generate_func2d(d)
        elif kind == "vector2d":
            generate_vector2d(d)
        else:
            raise ValueError(f"Tipo de gráfica no soportado: '{d.kind}'. Usa kind=func2d o kind=vector2d.")


def validate_images_exist(image_paths: List[str]):
    missing = [p for p in image_paths if not os.path.exists(p)]
    if missing:
        error("\nFaltan imágenes referenciadas en el Markdown:")
        for p in missing:
            error(f"  - {p}")
        error("\nNo se generará el Word para evitar un documento incompleto.")
        sys.exit(1)


def ensure_docx_not_locked(docx_path: str):
    """
    If Word has the file open, pandoc will fail with permission denied.
    We do a quick pre-check by trying to open the file for append.
    """
    if not os.path.exists(docx_path):
        return

    try:
        with open(docx_path, "ab"):
            pass
    except Exception:
        error(f"El archivo '{docx_path}' parece estar abierto (bloqueado) por Word.")
        error("Ciérralo y vuelve a ejecutar el comando.")
        sys.exit(1)


def run_pandoc():
    info("\nGenerando guia.docx con pandoc...")

    ensure_docx_not_locked(DOCX_FILE)

    cmd = [
        "pandoc",
        "--from=markdown+tex_math_single_backslash",
        "-o",
        DOCX_FILE,
        SOURCE_MD_FILE,
    ]

    if os.path.exists(REFERENCE_DOC):
        cmd.insert(1, f"--reference-doc={REFERENCE_DOC}")
        info(f"Usando plantilla de Word: {REFERENCE_DOC}")

    result = subprocess.run(cmd)
    if result.returncode == 0:
        success(f"Listo: {DOCX_FILE} generado correctamente.")
    else:
        error(f"Hubo un problema al ejecutar pandoc (código {result.returncode}).")
        sys.exit(result.returncode)


def main():
    ensure_working_directory()

    parser = argparse.ArgumentParser(description="Genera un documento de Word (DOCX) a partir de un archivo Markdown, incluyendo gráficos generados.")
    parser.add_argument('--source', default='guia.md', help='Documento orígen en Markdown')
    parser.add_argument('--output', default='guia.docx', help='Documento destino en Word (DOCX)')
    args = parser.parse_args()

    global SOURCE_MD_FILE, DOCX_FILE
    SOURCE_MD_FILE = args.source
    DOCX_FILE = args.output

    info("Iniciando construcción de la guía...")

    if not os.path.exists(SOURCE_MD_FILE):
        error(f"No se encontró el archivo Markdown '{SOURCE_MD_FILE}' en la carpeta:")
        error(os.getcwd())
        sys.exit(1)

    check_python_dependencies()

    with open(SOURCE_MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    directives = extract_plot_directives(content)
    image_paths = extract_markdown_image_paths(content)

    # Generate requested plots first
    generate_plots(directives)

    # Validate that referenced images exist (either generated or manually provided)
    validate_images_exist(image_paths)

    # Convert to Word
    run_pandoc()


if __name__ == "__main__":
    main()
