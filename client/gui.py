import tkinter as tk
from tkinter import ttk, colorchooser


class ConfigGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Display / Controller Configuration")
        self.configure(padx=10, pady=10)

        # Dynamic options (set externally)
        self.raw_screen_names = []      # list of names only
        self.encoded_screens = []       # list of "id|name"
        self.com_options = []

        # Inputs per screen ID
        self.input_options_by_screen_id = {}

        # Inputs per screen index (0,1,2)
        self.input_options_per_screen = {0: [], 1: [], 2: []}

        # Default colors
        self.default_colorA = "#ffffff"
        self.default_colorB = "#ffffff"

        # Internal state
        self.screen_vars = []
        self.screen_combos = []

        self.selected_inputs_A = ["", "", ""]
        self.selected_inputs_B = ["", "", ""]

        self.setup_a_inputs = []
        self.setup_a_combos = []

        self.setup_b_inputs = []
        self.setup_b_combos = []

        # Optional callback
        self.screen_selection_callback = None

        self.create_widgets()

    # ---------------------------------------------------------
    #  SETTERS CALLED BY EXTERNAL SCRIPT
    # ---------------------------------------------------------
    def set_com_options(self, options):
        self.com_options = options
        self.com_combo["values"] = options
        self.com_var.set("")

    def set_screen_options(self, names):
        """
        names = ["Screen A", "Screen A", "Screen B"]
        Encoded as:
        ["0|Screen A", "1|Screen A", "2|Screen B"]
        """
        self.raw_screen_names = names
        self.encoded_screens = [f"{i}|{name}" for i, name in enumerate(names)]

        for var, combo in zip(self.screen_vars, self.screen_combos):
            var.set("")
            combo["values"] = self.encoded_screens

    def set_input_options_for_screen_id(self, screen_id, options):
        """
        Assign input options to a specific screen instance (ID).
        Example: screen_id = 0 for "0|Screen A"
        """
        self.input_options_by_screen_id[screen_id] = options

    def set_default_colors(self, colorA, colorB):
        self.default_colorA = colorA
        self.default_colorB = colorB
        self.color_a_preview.config(bg=colorA)
        self.color_b_preview.config(bg=colorB)

    def set_screen_selection_callback(self, callback):
        self.screen_selection_callback = callback

    # ---------------------------------------------------------
    #  SCREEN SELECTION MUTUAL EXCLUSION (based on encoded ID)
    # ---------------------------------------------------------
    def update_screen_selection(self):
        selected = [v.get() for v in self.screen_vars if v.get()]

        for var, combo in zip(self.screen_vars, self.screen_combos):
            current = var.get()
            new_values = [
                opt for opt in self.encoded_screens
                if opt not in selected or opt == current
            ]
            combo["values"] = new_values
            if current not in new_values:
                var.set("")

    def reset_screens(self):
        for var in self.screen_vars:
            var.set("")
        for combo in self.screen_combos:
            combo["values"] = self.encoded_screens

    # ---------------------------------------------------------
    #  INPUT MUTUAL EXCLUSION BETWEEN SETUP A AND B
    # ---------------------------------------------------------
    def update_input_options(self, screen_index):
        selected_A = self.selected_inputs_A[screen_index]
        selected_B = self.selected_inputs_B[screen_index]

        base = self.input_options_per_screen[screen_index]

        # Setup A
        new_A = [opt for opt in base if opt != selected_B]
        self.setup_a_combos[screen_index]["values"] = new_A
        if selected_A not in new_A:
            self.setup_a_inputs[screen_index].set("")

        # Setup B
        new_B = [opt for opt in base if opt != selected_A]
        self.setup_b_combos[screen_index]["values"] = new_B
        if selected_B not in new_B:
            self.setup_b_inputs[screen_index].set("")

    def on_input_change_A(self, idx):
        self.selected_inputs_A[idx] = self.setup_a_inputs[idx].get()
        self.update_input_options(idx)

    def on_input_change_B(self, idx):
        self.selected_inputs_B[idx] = self.setup_b_inputs[idx].get()
        self.update_input_options(idx)

    # ---------------------------------------------------------
    #  RESET SETUP A / RESET SETUP B
    # ---------------------------------------------------------
    def reset_setup_A(self):
        for i in range(3):
            self.setup_a_inputs[i].set("")
            self.selected_inputs_A[i] = ""
            self.setup_a_combos[i]["values"] = self.input_options_per_screen[i]
            self.update_input_options(i)

    def reset_setup_B(self):
        for i in range(3):
            self.setup_b_inputs[i].set("")
            self.selected_inputs_B[i] = ""
            self.setup_b_combos[i]["values"] = self.input_options_per_screen[i]
            self.update_input_options(i)

    # ---------------------------------------------------------
    #  COLOR PICKER
    # ---------------------------------------------------------
    def choose_color(self, preview_label):
        color = colorchooser.askcolor(title="Choose color")
        if color and color[1]:
            preview_label.config(bg=color[1])

    # ---------------------------------------------------------
    #  SCREEN CHANGED → LOAD INPUTS FOR THAT SCREEN ID
    # ---------------------------------------------------------
    def _screen_changed(self, index, var):
        encoded = var.get()
        if not encoded:
            return

        # Extract ID and name from "id|name"
        screen_id_str, screen_name = encoded.split("|", 1)
        screen_id = int(screen_id_str)

        # Load input options for this specific screen instance
        if screen_id in self.input_options_by_screen_id:
            options = self.input_options_by_screen_id[screen_id]

            # Update Setup A
            self.setup_a_inputs[index].set("")
            self.setup_a_combos[index]["values"] = options

            # Update Setup B
            self.setup_b_inputs[index].set("")
            self.setup_b_combos[index]["values"] = options

            # Update internal per-screen options
            self.input_options_per_screen[index] = options

            # Refresh mutual exclusion
            self.update_input_options(index)

        # Update screen mutual exclusion
        self.update_screen_selection()

        # External callback
        if self.screen_selection_callback:
            self.screen_selection_callback(index, screen_name)

    # ---------------------------------------------------------
    #  GUI LAYOUT
    # ---------------------------------------------------------
    def create_widgets(self):
        # --- Top COM selector and screens ---
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # COM selector
        ttk.Label(top_frame, text="COM Selector").grid(row=0, column=0, sticky="w")
        self.com_var = tk.StringVar()
        self.com_combo = ttk.Combobox(top_frame, textvariable=self.com_var, width=15)
        self.com_combo.grid(row=1, column=0, sticky="w", padx=(0, 20))

        # Screen selectors
        for i in range(3):
            ttk.Label(top_frame, text=f"Screen {i+1}").grid(row=0, column=i+1, sticky="w")

            var = tk.StringVar()
            combo = ttk.Combobox(top_frame, textvariable=var, width=15, state="readonly")
            combo.grid(row=1, column=i+1, sticky="w", padx=(0, 10))

            var.trace_add("write", lambda *args, idx=i, v=var: self._screen_changed(idx, v))

            self.screen_vars.append(var)
            self.screen_combos.append(combo)

        # Reset Screens button BELOW the dropdowns
        reset_btn = ttk.Button(top_frame, text="Reset Screens", command=self.reset_screens)
        reset_btn.grid(row=2, column=0, columnspan=4, pady=(8, 0))

        # --- Setup A ---
        setup_a_frame = ttk.LabelFrame(self, text="Setup A")
        setup_a_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        for i in range(3):
            ttk.Label(setup_a_frame, text=f"Screen {i+1}: Input").grid(row=0, column=i, sticky="w", padx=5)

            var = tk.StringVar()
            combo = ttk.Combobox(setup_a_frame, textvariable=var, width=15)
            combo.grid(row=1, column=i, sticky="w", padx=5)

            var.trace_add("write", lambda *args, idx=i: self.on_input_change_A(idx))

            self.setup_a_inputs.append(var)
            self.setup_a_combos.append(combo)

        # Reset Setup A button
        reset_A_btn = ttk.Button(setup_a_frame, text="Reset Setup A", command=self.reset_setup_A)
        reset_A_btn.grid(row=3, column=2, sticky="e", pady=5, padx=5)

        # Color A
        color_a_frame = ttk.Frame(setup_a_frame)
        color_a_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        ttk.Label(color_a_frame, text="Color on controller").grid(row=0, column=0, sticky="w")
        self.color_a_preview = tk.Label(color_a_frame, width=4, height=1, relief="solid", bg=self.default_colorA)
        self.color_a_preview.grid(row=0, column=1, padx=5)
        self.color_a_preview.bind("<Button-1>", lambda e: self.choose_color(self.color_a_preview))

        # --- Setup B ---
        setup_b_frame = ttk.LabelFrame(self, text="Setup B")
        setup_b_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        for i in range(3):
            ttk.Label(setup_b_frame, text=f"Screen {i+1}: Input").grid(row=0, column=i, sticky="w", padx=5)

            var = tk.StringVar()
            combo = ttk.Combobox(setup_b_frame, textvariable=var, width=15)
            combo.grid(row=1, column=i, sticky="w", padx=5)

            var.trace_add("write", lambda *args, idx=i: self.on_input_change_B(idx))

            self.setup_b_inputs.append(var)
            self.setup_b_combos.append(combo)

        # Reset Setup B button
        reset_B_btn = ttk.Button(setup_b_frame, text="Reset Setup B", command=self.reset_setup_B)
        reset_B_btn.grid(row=3, column=2, sticky="e", pady=5, padx=5)

        # Color B
        color_b_frame = ttk.Frame(setup_b_frame)
        color_b_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        ttk.Label(color_b_frame, text="Color on controller").grid(row=0, column=0, sticky="w")
        self.color_b_preview = tk.Label(color_b_frame, width=4, height=1, relief="solid", bg=self.default_colorB)
        self.color_b_preview.grid(row=0, column=1, padx=5)
        self.color_b_preview.bind("<Button-1>", lambda e: self.choose_color(self.color_b_preview))

        # --- Save button ---
        save_frame = ttk.Frame(self)
        save_frame.grid(row=3, column=0, sticky="e")
        ttk.Button(save_frame, text="Save", command=self.save_config).grid(row=0, column=0, pady=(5, 0))

    # ---------------------------------------------------------
    #  SAVE (DEMO)
    # ---------------------------------------------------------
    def save_config(self):
        print("COM:", self.com_var.get())
        print("Screens:", [v.get() for v in self.screen_vars])
        print("Setup A inputs:", [v.get() for v in self.setup_a_inputs])
        print("Setup B inputs:", [v.get() for v in self.setup_b_inputs])
        print("Color A:", self.color_a_preview.cget("bg"))
        print("Color B:", self.color_b_preview.cget("bg"))
        print("Configuration saved (demo).")
