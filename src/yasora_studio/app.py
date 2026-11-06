"""Cross-platform desktop UI for the locally bundled MarkItDown engine."""
from __future__ import annotations
import argparse
from pathlib import Path
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from . import VERSION
from .converter import convert_one
from .paths import default_output, source_items
from .updates import latest_versions, RELEASES, installed_engine_version

BG = "#111827"
PANEL = "#1e293b"
TEXT = "#f1f5f9"
MUTED = "#b6c4d5"
TEAL = "#14b8a6"


class Studio:
    def __init__(self, root: tk.Tk, initial_path: str | None = None):
        self.root = root
        self.sources: list[Path] = []
        self.events: queue.Queue = queue.Queue()
        self.cancel = threading.Event()
        self.busy = False
        self.output = tk.StringVar(value=str(default_output()))
        self.overwrite = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Ready — your documents stay on your device")
        self.counter = tk.StringVar(value="No files selected")
        self.root.title(f"Yasora Markdown Studio {VERSION}")
        self.root.geometry("900x650")
        self.root.minsize(670, 510)
        self.root.configure(bg=BG)
        self._icon()
        self._build()
        if initial_path:
            self.add_sources([Path(initial_path)])
        self.root.after(100, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _icon(self) -> None:
        asset = Path(__file__).parent / "assets" / "studio.png"
        try:
            self.root._yasora_icon = tk.PhotoImage(file=str(asset))
            self.root.iconphoto(True, self.root._yasora_icon)
        except (OSError, tk.TclError):
            pass
        if sys.platform == "win32":
            try:
                self.root.iconbitmap(str(Path(__file__).parent / "assets" / "studio.ico"))
            except tk.TclError:
                pass

    def _build(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Y.TFrame", background=BG)
        style.configure("Y.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 20, "bold"))
        style.configure("Y.TButton", background=PANEL, foreground=TEXT, padding=(13, 9), borderwidth=0, font=("Segoe UI", 10))
        style.map("Y.TButton", background=[("active", "#31445f"), ("disabled", "#263243")], foreground=[("disabled", "#8b97a6")])
        style.configure("Accent.TButton", background=TEAL, foreground="#052e2b", padding=(17, 10), borderwidth=0, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#5eead4"), ("disabled", "#276a68")])
        style.configure("Y.TEntry", padding=7)
        style.configure("Y.Horizontal.TProgressbar", background=TEAL, troughcolor=PANEL, thickness=9)
        style.configure("Y.Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=28, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Y.Treeview.Heading", background="#29384e", foreground=TEXT, padding=7)
        style.map("Y.Treeview", background=[("selected", "#315c67")])
        frame = ttk.Frame(self.root, style="Y.TFrame", padding=(23, 20))
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Yasora Markdown Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=f"Powered by Microsoft MarkItDown · Installed engine {installed_engine_version()} · Local conversion", style="Muted.TLabel").pack(anchor="w", pady=(1, 15))

        actions = ttk.Frame(frame, style="Y.TFrame")
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(actions, text="+ Add Files", style="Y.TButton", command=self._select_files).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="+ Add Folder", style="Y.TButton", command=self._select_folder).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Clear", style="Y.TButton", command=self._clear).pack(side="left")
        ttk.Label(actions, textvariable=self.counter, style="Muted.TLabel").pack(side="right")

        columns = ("name", "type", "location")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", style="Y.Treeview", height=9)
        for key, heading, width in [("name", "File / folder", 240), ("type", "Kind", 80), ("location", "Location", 440)]:
            self.table.heading(key, text=heading)
            self.table.column(key, width=width, minwidth=80, stretch=key == "location")
        self.table.pack(fill="both", expand=True)

        outrow = ttk.Frame(frame, style="Y.TFrame")
        outrow.pack(fill="x", pady=(14, 6))
        ttk.Label(outrow, text="Output folder", style="Y.TLabel").pack(side="left", padx=(0, 10))
        ttk.Entry(outrow, textvariable=self.output, style="Y.TEntry").pack(side="left", fill="x", expand=True, padx=(0, 7))
        ttk.Button(outrow, text="Browse", style="Y.TButton", command=self._browse_output).pack(side="left")

        toggles = ttk.Frame(frame, style="Y.TFrame")
        toggles.pack(fill="x", pady=(2, 12))
        checkbox = tk.Checkbutton(toggles, text="Overwrite existing converted files", variable=self.overwrite, bg=BG, fg=TEXT, activebackground=BG, activeforeground=TEXT, selectcolor=PANEL)
        checkbox.pack(side="left")
        self.progress = ttk.Progressbar(frame, style="Y.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 8))
        ttk.Label(frame, textvariable=self.status, style="Muted.TLabel").pack(anchor="w", pady=(0, 10))

        control = ttk.Frame(frame, style="Y.TFrame")
        control.pack(fill="x", pady=(0, 11))
        self.convert_button = ttk.Button(control, text="Convert to Markdown", style="Accent.TButton", command=self._start)
        self.convert_button.pack(side="left", padx=(0, 8))
        self.cancel_button = ttk.Button(control, text="Cancel", style="Y.TButton", command=self.cancel.set, state="disabled")
        self.cancel_button.pack(side="left", padx=(0, 8))
        ttk.Button(control, text="Open Output", style="Y.TButton", command=self._open_output).pack(side="left")
        ttk.Button(control, text="Check Updates", style="Y.TButton", command=self._check_updates).pack(side="right")

        self.log = tk.Text(frame, height=6, bg="#0b1220", fg="#d1e7e3", insertbackground=TEXT, relief="flat", font=("Consolas", 9), wrap="word", padx=8, pady=8)
        self.log.pack(fill="both", expand=False)
        self.log.configure(state="disabled")
        self._log("Ready. Add documents or a folder. Folder contents are scanned recursively.")

    def _log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def add_sources(self, paths: list[Path]) -> None:
        if self.busy:
            return
        old = {os.path.normcase(str(p)) for p in self.sources}
        for p in paths:
            path = p.expanduser().absolute()
            if path.exists() and not path.is_symlink() and os.path.normcase(str(path)) not in old:
                self.sources.append(path)
                self.table.insert("", "end", values=(path.name, "Folder" if path.is_dir() else "File", str(path.parent)))
                old.add(os.path.normcase(str(path)))
        self.counter.set(f"{len(self.sources)} selected")

    def _select_files(self) -> None:
        chosen = filedialog.askopenfilenames(title="Select documents")
        self.add_sources([Path(p) for p in chosen])

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder to convert")
        if folder:
            self.add_sources([Path(folder)])

    def _browse_output(self) -> None:
        folder = filedialog.askdirectory(title="Select Markdown destination", initialdir=str(Path.home()))
        if folder:
            self.output.set(folder)

    def _clear(self) -> None:
        if self.busy:
            return
        self.sources.clear()
        for entry in self.table.get_children():
            self.table.delete(entry)
        self.counter.set("No files selected")

    def _start(self) -> None:
        if self.busy:
            return
        if not self.sources:
            messagebox.showinfo("Select documents", "Add at least one file or folder first.")
            return
        destination = Path(self.output.get().strip()).expanduser()
        if not str(destination).strip():
            messagebox.showerror("Output folder", "Choose a valid output directory.")
            return
        if not destination.is_absolute():
            messagebox.showerror("Output folder", "Use an absolute output directory.")
            return
        pairs = source_items(self.sources, destination)
        if not pairs:
            messagebox.showinfo("No supported documents", "No matching files found. Check the selected paths.")
            return
        self.busy = True
        self.cancel.clear()
        self.convert_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.configure(maximum=len(pairs), value=0)
        self.status.set(f"Converting {len(pairs)} document(s)...")
        thread = threading.Thread(target=self._worker, args=(pairs, destination, self.overwrite.get()), daemon=True)
        thread.start()

    def _worker(self, pairs: list[tuple[Path, Path]], output: Path, overwrite: bool) -> None:
        done = skipped = failed = 0
        for source, relative in pairs:
            if self.cancel.is_set():
                break
            try:
                kind = convert_one(source, output / relative, overwrite=overwrite)
                if kind == "converted":
                    done += 1
                else:
                    skipped += 1
                self.events.put(("log", f"{kind.upper()}: {source.name} → {relative}"))
            except Exception as exc:
                failed += 1
                self.events.put(("log", f"ERROR: {source}: {type(exc).__name__}: {exc}"))
            self.events.put(("progress", done + skipped + failed))
        self.events.put(("finished", (done, skipped, failed, self.cancel.is_set())))

    def _drain_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "log":
                    self._log(str(payload))
                elif kind == "progress":
                    self.progress.configure(value=payload)
                elif kind == "finished":
                    converted, skipped, failed, cancelled = payload
                    self.status.set(f"{'Cancelled' if cancelled else 'Finished'} — {converted} converted, {skipped} skipped, {failed} failed")
                    self._log(self.status.get())
                    self.busy = False
                    self.convert_button.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
                elif kind == "updates":
                    info = payload
                    open_page = messagebox.askyesno("Version information", f"App installed: {info['app_installed']}\nApp release: {info['app_latest']}\n\nEngine installed: {info['engine_installed']}\nEngine on PyPI: {info['engine_latest']}\n\nThe engine is updated by installing a reviewed new Yasora app release. Direct pip updates of frozen binaries are disabled.\n\nOpen Yasora Releases page?")
                    if open_page:
                        webbrowser.open(RELEASES)
                elif kind == "error":
                    messagebox.showerror("Update check", str(payload))
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._drain_events)

    def _open_output(self) -> None:
        directory = Path(self.output.get().strip()).expanduser()
        if not directory.is_dir():
            messagebox.showinfo("Output", "The output folder hasn't been created yet.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(directory))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(directory)])
            else:
                subprocess.Popen(["xdg-open", str(directory)])
        except OSError as exc:
            messagebox.showerror("Open folder", str(exc))

    def _check_updates(self) -> None:
        self.status.set("Checking GitHub releases and PyPI...")
        threading.Thread(target=lambda: self.events.put(("updates", latest_versions())), daemon=True).start()

    def _close(self) -> None:
        if self.busy:
            if not messagebox.askyesno("Conversion in progress", "Cancel and close? The current document may finish processing."):
                return
            self.cancel.set()
        self.root.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Yasora Markdown Studio")
    parser.add_argument("--convert", metavar="PATH", help="Select a local file or folder from the Explorer context menu")
    parser.add_argument("--smoke-test", nargs=2, metavar=("INPUT", "OUTPUT"), help="Headless bundled-engine conversion test")
    parser.add_argument("--engine-version", action="store_true", help="Print the packaged MarkItDown version")
    parser.add_argument("path", nargs="?", help="Optional document opened from the operating system")
    args = parser.parse_args()
    if args.engine_version:
        print(installed_engine_version())
        return
    if args.smoke_test:
        try:
            state = convert_one(Path(args.smoke_test[0]), Path(args.smoke_test[1]), overwrite=True)
            if state != "converted" or not Path(args.smoke_test[1]).is_file():
                raise RuntimeError("Smoke-test Markdown file missing")
            print("YASORA_SMOKE_TEST_OK", installed_engine_version())
        except Exception as exc:
            print(f"YASORA_SMOKE_TEST_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
            raise SystemExit(1)
        return
    root = tk.Tk()
    Studio(root, args.convert or args.path)
    root.mainloop()
