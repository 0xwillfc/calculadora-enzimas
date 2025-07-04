from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox


APP_TITLE = "Calculadora de Atividade Enzimática"
WINDOW_SIZE = "640x610"


@dataclass(frozen=True)
class ExtinctionAssaySpec:
    prefix: str
    display_name: str
    result_unit: str
    epsilon_default: str
    sample_volume_default: str
    result_color: str
    scale_factor: float = 1.0
    total_volume_default: str = "300,0"
    path_length_default: str = "0,9"
    blank_default: str = "0,0"


CAT_SPEC = ExtinctionAssaySpec(
    prefix="cat",
    display_name="Catalase (CAT)",
    result_unit="µmol/min/mg",
    epsilon_default="0,04",
    sample_volume_default="10,0",
    result_color="blue",
)

GST_SPEC = ExtinctionAssaySpec(
    prefix="gst",
    display_name="GST",
    result_unit="nmol/min/mg",
    epsilon_default="9,6",
    sample_volume_default="20,0",
    result_color="green",
    scale_factor=1000.0,
)


class InputValidationError(ValueError):
    """Raised when a required field is empty or invalid."""


def parse_number(entry_widget, label_text):
    raw_value = entry_widget.get().strip().replace(",", ".")
    if not raw_value:
        raise InputValidationError(f"O campo '{label_text}' é obrigatório.")

    try:
        return float(raw_value)
    except (ValueError, tk.TclError) as exc:
        raise InputValidationError(
            f"O campo '{label_text}' deve conter um valor numérico válido."
        ) from exc


def parse_text(entry_widget, label_text):
    value = entry_widget.get().strip()
    if not value:
        raise InputValidationError(f"O campo '{label_text}' é obrigatório.")
    return value


def require_positive(value, label_text):
    if value <= 0:
        raise InputValidationError(f"O campo '{label_text}' deve ser maior que zero.")


def format_result(value):
    return f"{value:.4f}".replace(".", ",")


def calculate_extinction_assay(entries, spec):
    sample_id = parse_text(entries[f"{spec.prefix}_sample_id"], "ID da Amostra")
    delta_abs_sample = parse_number(
        entries[f"{spec.prefix}_delta_abs_sample"], "ΔAbs/min (Amostra)"
    )
    delta_abs_blank = parse_number(
        entries[f"{spec.prefix}_delta_abs_blank"], "ΔAbs/min (Branco)"
    )
    protein_conc = parse_number(
        entries[f"{spec.prefix}_protein"], "Concentração de Proteína (mg/mL)"
    )
    path_length = parse_number(
        entries[f"{spec.prefix}_path_length"], "Caminho Óptico (d) (cm)"
    )
    total_volume = parse_number(
        entries[f"{spec.prefix}_v_total"], "Volume Total (Vt) (µL)"
    )
    sample_volume = parse_number(
        entries[f"{spec.prefix}_v_sample"], "Volume da Amostra (Vs) (µL)"
    )
    epsilon = parse_number(
        entries[f"{spec.prefix}_epsilon"], "Coeficiente de Extinção (ε)"
    )

    for numeric_value, label_text in (
        (protein_conc, "Concentração de Proteína (mg/mL)"),
        (path_length, "Caminho Óptico (d) (cm)"),
        (total_volume, "Volume Total (Vt) (µL)"),
        (sample_volume, "Volume da Amostra (Vs) (µL)"),
        (epsilon, "Coeficiente de Extinção (ε)"),
    ):
        require_positive(numeric_value, label_text)

    corrected_absorbance = delta_abs_sample - delta_abs_blank
    dilution_factor = total_volume / sample_volume
    denominator = epsilon * path_length * protein_conc
    activity = (corrected_absorbance * dilution_factor * spec.scale_factor) / denominator

    return sample_id, f"{format_result(activity)} {spec.result_unit}"


def calculate_sod_beauchamp(entries):
    sample_id = parse_text(entries["sod_sample_id"], "ID da Amostra")
    abs_blank = parse_number(entries["sod_abs_blank"], "Abs (Branco / Controle)")
    abs_sample = parse_number(entries["sod_abs_sample"], "Abs (Amostra)")
    protein_conc = parse_number(
        entries["sod_protein"], "Concentração de Proteína (mg/mL)"
    )
    sample_volume_ul = parse_number(
        entries["sod_v_sample_beauchamp"], "Volume da Amostra (Vs) (µL)"
    )
    dilution_factor = parse_number(
        entries["sod_dilution_factor_beauchamp"], "Fator de Diluição"
    )

    require_positive(abs_blank, "Abs (Branco / Controle)")
    require_positive(protein_conc, "Concentração de Proteína (mg/mL)")
    require_positive(sample_volume_ul, "Volume da Amostra (Vs) (µL)")
    require_positive(dilution_factor, "Fator de Diluição")

    protein_mass_mg = protein_conc * (sample_volume_ul / 1000.0)
    require_positive(protein_mass_mg, "Massa de proteína na cubeta")

    inhibition_percent = ((abs_blank - abs_sample) / abs_blank) * 100.0
    activity = ((inhibition_percent / 50.0) * dilution_factor) / protein_mass_mg

    return sample_id, f"{format_result(activity)} U/mg", "SOD (Beauchamp)"


def calculate_sod_zhang(entries):
    sample_id = parse_text(entries["sod_sample_id"], "ID da Amostra")
    abs_blank = parse_number(entries["sod_abs_blank"], "Abs (Branco / Controle)")
    abs_sample = parse_number(entries["sod_abs_sample"], "Abs (Amostra)")
    total_volume = parse_number(
        entries["sod_v_total_zhang"], "Volume do Sistema (Vt) (µL)"
    )
    sample_volume = parse_number(
        entries["sod_v_sample_zhang"], "Volume da Amostra (Vs) (µL)"
    )
    dilution_factor = parse_number(
        entries["sod_dilution_factor_zhang"], "Fator de Diluição"
    )

    require_positive(abs_sample, "Abs (Amostra)")
    require_positive(total_volume, "Volume do Sistema (Vt) (µL)")
    require_positive(sample_volume, "Volume da Amostra (Vs) (µL)")
    require_positive(dilution_factor, "Fator de Diluição")

    activity = (
        ((abs_blank - abs_sample) / abs_sample)
        * (total_volume / sample_volume)
        * dilution_factor
    )

    return sample_id, f"{format_result(activity)} U/mL", "SOD (Zhang)"


class EnzymeActivityCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        self.cat_entries = {}
        self.gst_entries = {}
        self.sod_entries = {}

        self._configure_style()
        self._build_interface()

    def _configure_style(self):
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Helvetica", 11, "bold"))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TRadiobutton", background="#f0f0f0", font=("Helvetica", 10))

    def _build_interface(self):
        notebook = ttk.Notebook(self)
        notebook.pack(padx=10, pady=10, expand=True, fill="both")

        cat_frame = ttk.Frame(notebook, padding="15")
        gst_frame = ttk.Frame(notebook, padding="15")
        sod_frame = ttk.Frame(notebook, padding="15")

        notebook.add(cat_frame, text=CAT_SPEC.display_name)
        notebook.add(gst_frame, text=GST_SPEC.display_name)
        notebook.add(sod_frame, text="SOD")

        self._create_extinction_ui(cat_frame, CAT_SPEC, self.cat_entries, self.on_calculate_cat)
        self._create_extinction_ui(gst_frame, GST_SPEC, self.gst_entries, self.on_calculate_gst)
        self._create_sod_ui(sod_frame)

    def _create_extinction_ui(self, parent_frame, spec, entry_dict, callback):
        fields = (
            (f"{spec.prefix}_sample_id", "ID da Amostra", ""),
            (f"{spec.prefix}_delta_abs_sample", "ΔAbs/min (Amostra)", ""),
            (f"{spec.prefix}_delta_abs_blank", "ΔAbs/min (Branco)", spec.blank_default),
            (f"{spec.prefix}_protein", "Concentração de Proteína (mg/mL)", ""),
            (f"{spec.prefix}_path_length", "Caminho Óptico (d) (cm)", spec.path_length_default),
            (f"{spec.prefix}_v_total", "Volume Total (Vt) (µL)", spec.total_volume_default),
            (f"{spec.prefix}_v_sample", "Volume da Amostra (Vs) (µL)", spec.sample_volume_default),
            (f"{spec.prefix}_epsilon", "Coeficiente de Extinção (ε)", spec.epsilon_default),
        )

        for row_index, (field_key, label_text, default_value) in enumerate(fields):
            ttk.Label(parent_frame, text=label_text).grid(
                row=row_index, column=0, padx=5, pady=6, sticky="w"
            )
            entry_widget = ttk.Entry(parent_frame, width=25, font=("Helvetica", 10))
            entry_widget.insert(0, default_value)
            entry_widget.grid(row=row_index, column=1, padx=5, pady=6, sticky="ew")
            entry_dict[field_key] = entry_widget

        parent_frame.columnconfigure(1, weight=1)

        ttk.Button(parent_frame, text="Calcular Atividade", command=callback).grid(
            row=len(fields), column=0, columnspan=2, pady=20
        )

        result_label = ttk.Label(
            parent_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            foreground=spec.result_color,
        )
        result_label.grid(row=len(fields) + 1, column=0, columnspan=2, pady=5)
        entry_dict[f"{spec.prefix}_result_label"] = result_label

    def _create_sod_ui(self, parent_frame):
        common_fields_frame = ttk.Frame(parent_frame)
        common_fields_frame.pack(fill="x", pady=5)

        ttk.Label(common_fields_frame, text="ID da Amostra").grid(
            row=0, column=0, sticky="w", padx=5, pady=6
        )
        self.sod_entries["sod_sample_id"] = ttk.Entry(
            common_fields_frame, width=25, font=("Helvetica", 10)
        )
        self.sod_entries["sod_sample_id"].grid(
            row=0, column=1, sticky="ew", padx=5, pady=6
        )

        ttk.Label(common_fields_frame, text="Abs (Branco / Controle)").grid(
            row=1, column=0, sticky="w", padx=5, pady=6
        )
        self.sod_entries["sod_abs_blank"] = ttk.Entry(
            common_fields_frame, width=25, font=("Helvetica", 10)
        )
        self.sod_entries["sod_abs_blank"].grid(
            row=1, column=1, sticky="ew", padx=5, pady=6
        )

        ttk.Label(common_fields_frame, text="Abs (Amostra)").grid(
            row=2, column=0, sticky="w", padx=5, pady=6
        )
        self.sod_entries["sod_abs_sample"] = ttk.Entry(
            common_fields_frame, width=25, font=("Helvetica", 10)
        )
        self.sod_entries["sod_abs_sample"].grid(
            row=2, column=1, sticky="ew", padx=5, pady=6
        )
        common_fields_frame.columnconfigure(1, weight=1)

        radio_frame = ttk.Labelframe(
            parent_frame, text="Selecione o Método de Cálculo", padding="10"
        )
        radio_frame.pack(fill="x", pady=10)

        self.sod_entries["calc_type_var"] = tk.StringVar(value="beauchamp")
        ttk.Radiobutton(
            radio_frame,
            text="Atividade (U/mg) - Beauchamp",
            variable=self.sod_entries["calc_type_var"],
            value="beauchamp",
            command=self.toggle_sod_inputs,
        ).pack(anchor="w")
        ttk.Radiobutton(
            radio_frame,
            text="Atividade (U/mL) - Zhang",
            variable=self.sod_entries["calc_type_var"],
            value="zhang",
            command=self.toggle_sod_inputs,
        ).pack(anchor="w")

        self.beauchamp_frame = ttk.Labelframe(
            parent_frame, text="Dados para Beauchamp", padding="10"
        )
        self.zhang_frame = ttk.Labelframe(
            parent_frame, text="Dados para Zhang", padding="10"
        )

        self._create_sod_beauchamp_inputs()
        self._create_sod_zhang_inputs()
        self.toggle_sod_inputs()

        ttk.Button(parent_frame, text="Calcular Atividade", command=self.on_calculate_sod).pack(
            pady=20
        )

        result_label = ttk.Label(
            parent_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            foreground="purple",
        )
        result_label.pack(pady=5)
        self.sod_entries["sod_result_label"] = result_label

    def _create_sod_beauchamp_inputs(self):
        fields = (
            ("sod_protein", "Concentração de Proteína (mg/mL)", ""),
            ("sod_v_sample_beauchamp", "Volume da Amostra (Vs) (µL)", "30,0"),
            ("sod_dilution_factor_beauchamp", "Fator de Diluição", "1,0"),
        )

        for row_index, (field_key, label_text, default_value) in enumerate(fields):
            ttk.Label(self.beauchamp_frame, text=label_text).grid(
                row=row_index, column=0, sticky="w", padx=5, pady=6
            )
            entry_widget = ttk.Entry(self.beauchamp_frame, width=25, font=("Helvetica", 10))
            entry_widget.insert(0, default_value)
            entry_widget.grid(row=row_index, column=1, sticky="ew", padx=5, pady=6)
            self.sod_entries[field_key] = entry_widget

        self.beauchamp_frame.columnconfigure(1, weight=1)

    def _create_sod_zhang_inputs(self):
        fields = (
            ("sod_v_total_zhang", "Volume do Sistema (Vt) (µL)", "200,0"),
            ("sod_v_sample_zhang", "Volume da Amostra (Vs) (µL)", "30,0"),
            ("sod_dilution_factor_zhang", "Fator de Diluição", "1,0"),
        )

        for row_index, (field_key, label_text, default_value) in enumerate(fields):
            ttk.Label(self.zhang_frame, text=label_text).grid(
                row=row_index, column=0, sticky="w", padx=5, pady=6
            )
            entry_widget = ttk.Entry(self.zhang_frame, width=25, font=("Helvetica", 10))
            entry_widget.insert(0, default_value)
            entry_widget.grid(row=row_index, column=1, sticky="ew", padx=5, pady=6)
            self.sod_entries[field_key] = entry_widget

        self.zhang_frame.columnconfigure(1, weight=1)

    def toggle_sod_inputs(self):
        calc_type = self.sod_entries["calc_type_var"].get()
        if calc_type == "beauchamp":
            self.beauchamp_frame.pack(fill="x", pady=5, padx=10)
            self.zhang_frame.pack_forget()
        else:
            self.zhang_frame.pack(fill="x", pady=5, padx=10)
            self.beauchamp_frame.pack_forget()

    def _run_calculation(self, calculation_func, result_key):
        try:
            sample_id, result_text = calculation_func()
        except InputValidationError as exc:
            messagebox.showerror("Erro de Entrada", str(exc))
            return

        self._set_result(result_key, f"{sample_id}: {result_text}")

    def _set_result(self, result_key, text):
        for entry_group in (self.cat_entries, self.gst_entries, self.sod_entries):
            if result_key in entry_group:
                entry_group[result_key].config(text=text)
                return

    def on_calculate_cat(self):
        self._run_calculation(
            lambda: calculate_extinction_assay(self.cat_entries, CAT_SPEC),
            "cat_result_label",
        )

    def on_calculate_gst(self):
        self._run_calculation(
            lambda: calculate_extinction_assay(self.gst_entries, GST_SPEC),
            "gst_result_label",
        )

    def on_calculate_sod(self):
        calc_type = self.sod_entries["calc_type_var"].get()
        calculation = calculate_sod_beauchamp if calc_type == "beauchamp" else calculate_sod_zhang

        try:
            sample_id, result_text, method_name = calculation(self.sod_entries)
        except InputValidationError as exc:
            messagebox.showerror("Erro de Entrada", str(exc))
            return

        self.sod_entries["sod_result_label"].config(
            text=f"{sample_id}: {result_text} ({method_name})"
        )


if __name__ == "__main__":
    app = EnzymeActivityCalculatorApp()
    app.mainloop()
