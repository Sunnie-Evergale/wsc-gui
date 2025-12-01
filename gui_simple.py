#!/usr/bin/env python3
# gui_simple.py
# WSC Decompiler GUI - Simplified version without drag-and-drop dependencies

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import sys
from pathlib import Path
from decompiler import decompile_wsc_file


class WSCDecompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("WSC Decompiler GUI - Simple Version")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Settings
        self.settings_file = "settings.json"
        self.settings = {
            "output_dir": "",
            "last_input_dir": ""
        }

        # File lists
        self.wsc_files = []

        # Setup GUI
        self.setup_menu()
        self.setup_widgets()
        self.load_settings()

        # Handle closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Single WSC...", command=self.open_single_file)
        file_menu.add_command(label="Open Multiple WSC...", command=self.open_multiple_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Top frame for controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # File selection area
        file_frame = ttk.Frame(control_frame)
        file_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        ttk.Label(file_frame, text="Input Files:").grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Files list
        self.files_listbox = tk.Listbox(file_frame, height=4)
        self.files_listbox.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        files_scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.grid(row=1, column=1, sticky="ns")
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)

        # File buttons
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.grid(row=2, column=0, sticky="ew")

        ttk.Button(file_btn_frame, text="Add Single", command=self.open_single_file).pack(side="left", padx=(0, 5))
        ttk.Button(file_btn_frame, text="Add Multiple", command=self.open_multiple_files).pack(side="left", padx=(0, 5))
        ttk.Button(file_btn_frame, text="Clear Files", command=self.clear_files).pack(side="left", padx=(0, 5))
        ttk.Button(file_btn_frame, text="Remove Selected", command=self.remove_selected_file).pack(side="left")

        # File selection info
        info_frame = ttk.Frame(control_frame)
        info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        info_text = "Add .WSC files using the buttons above.\n"
        info_text += "For drag-and-drop support, install tkinterdnd2 and use gui.py instead."
        ttk.Label(info_frame, text=info_text, foreground="blue").pack()

        # Output directory
        output_frame = ttk.Frame(control_frame)
        output_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky="ew")

        self.start_button = ttk.Button(button_frame, text="Start Decompilation", command=self.start_decompilation)
        self.start_button.pack(side="left", padx=(0, 5))

        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side="left", padx=(0, 5))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(control_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def log(self, message, error=False):
        """Add message to log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update()
        if error:
            self.status_var.set(f"Error: {message}")
        else:
            self.status_var.set(message)

    def open_single_file(self):
        """Open single WSC file."""
        initial_dir = self.settings.get("last_input_dir", "")
        file_path = filedialog.askopenfilename(
            title="Select WSC file",
            initialdir=initial_dir,
            filetypes=[("WSC files", "*.WSC"), ("WSC files", "*.wsc"), ("All files", "*.*")]
        )
        if file_path:
            self.settings["last_input_dir"] = os.path.dirname(file_path)
            self.add_file(file_path)

    def open_multiple_files(self):
        """Open multiple WSC files."""
        initial_dir = self.settings.get("last_input_dir", "")
        file_paths = filedialog.askopenfilenames(
            title="Select WSC files",
            initialdir=initial_dir,
            filetypes=[("WSC files", "*.WSC"), ("WSC files", "*.wsc"), ("All files", "*.*")]
        )
        if file_paths:
            self.settings["last_input_dir"] = os.path.dirname(file_paths[0])
            for file_path in file_paths:
                self.add_file(file_path)

    def add_file(self, file_path):
        """Add file to list."""
        if file_path not in self.wsc_files:
            self.wsc_files.append(file_path)
            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            self.log(f"Added: {os.path.basename(file_path)}")

    def clear_files(self):
        """Clear all files."""
        self.wsc_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.log("Cleared all files")

    def remove_selected_file(self):
        """Remove selected file."""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            del self.wsc_files[index]
            self.files_listbox.delete(index)
            self.log("Removed selected file")

    def browse_output_dir(self):
        """Browse for output directory."""
        dir_path = filedialog.askdirectory(
            title="Select output directory",
            initialdir=self.output_var.get() or self.settings.get("output_dir", "")
        )
        if dir_path:
            self.output_var.set(dir_path)

    def start_decompilation(self):
        """Start the decompilation process."""
        if not self.wsc_files:
            messagebox.showwarning("No Files", "Please add WSC files first.")
            return

        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showwarning("No Output Directory", "Please select an output directory.")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.log(f"Created output directory: {output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return

        # Process files
        self.log(f"Starting decompilation of {len(self.wsc_files)} files...")
        success_count = 0
        error_count = 0

        for wsc_file in self.wsc_files:
            try:
                base_name = os.path.splitext(os.path.basename(wsc_file))[0]
                output_file = os.path.join(output_dir, f"{base_name}.txt")

                self.log(f"Processing: {os.path.basename(wsc_file)}")
                decompile_wsc_file(wsc_file, output_file)
                self.log(f"  -> {os.path.basename(output_file)}")
                success_count += 1

            except Exception as e:
                self.log(f"Error processing {os.path.basename(wsc_file)}: {e}", error=True)
                error_count += 1

        self.log(f"Decompilation complete: {success_count} success, {error_count} errors")

        if error_count == 0:
            messagebox.showinfo("Success", f"Successfully decompiled {success_count} files!")
        else:
            messagebox.showwarning("Partial Success",
                                f"Decompiled {success_count} files with {error_count} errors.")

    def clear_log(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Ready")

    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)

                # Apply settings
                if self.settings.get("output_dir"):
                    self.output_var.set(self.settings["output_dir"])

                self.log("Settings loaded successfully")
        except Exception as e:
            self.log(f"Could not load settings: {e}", error=True)

    def save_settings(self):
        """Save settings to file."""
        try:
            self.settings["output_dir"] = self.output_var.get()
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            self.log(f"Could not save settings: {e}", error=True)

    def on_closing(self):
        """Handle window closing."""
        self.save_settings()
        self.destroy()

    def show_about(self):
        """Show about dialog."""
        about_text = """WSC Decompiler GUI v1.0 (Simple Version)

A tool for decompiling .WSC script files with support for:
- Japanese CP932/Shift-JIS text decoding
- Speaker name detection
- Batch processing
- GitHub-style output format

Note: This version does not include drag-and-drop support.
For full drag-and-drop functionality, install tkinterdnd2
and use gui.py instead.

Created for visual novel script analysis."""
        messagebox.showinfo("About WSC Decompiler", about_text)


def main():
    """Main entry point."""
    try:
        app = WSCDecompilerGUI()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()