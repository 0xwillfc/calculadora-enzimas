import tkinter as tk
from tkinter import ttk, messagebox

# --- Funções de Cálculo ---
# A lógica de cálculo é a mesma da versão de terminal (CLI)

def calculate_cat_activity(entries):
    """Calcula a atividade da CAT com base nos valores dos campos de entrada."""
    try:
        # Coleta e converte os valores dos campos de entrada
        delta_abs_sample = float(entries["cat_delta_abs_sample"].get())
        delta_abs_blank = float(entries["cat_delta_abs_blank"].get())
        protein_conc = float(entries["cat_protein"].get())
        path_length = float(entries["cat_path_length"].get())
        v_total = float(entries["cat_v_total"].get())
        v_sample = float(entries["cat_v_sample"].get())
        epsilon = 0.04  # Coeficiente de extinção molar para CAT

        # Validação para evitar divisão por zero
        if protein_conc == 0 or path_length == 0 or v_sample == 0:
            messagebox.showerror("Erro de Entrada", "Concentração de proteína, caminho óptico e volume da amostra não podem ser zero.")
            return None

        # Cálculo da atividade
        delta_abs_corrected = delta_abs_sample - delta_abs_blank
        dilution_factor = v_total / v_sample
        
        numerator = delta_abs_corrected * dilution_factor
        denominator = epsilon * path_length * protein_conc
        
        if denominator == 0:
            messagebox.showerror("Erro de Cálculo", "O denominador do cálculo resultou em zero. Verifique os valores.")
            return None

        activity = numerator / denominator
        return f"{activity:.4f} µmol/min/mg"

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos em todos os campos.")
        return None
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
        return None

def calculate_gst_activity(entries):
    """Calcula a atividade da GST com base nos valores dos campos de entrada."""
    try:
        # Coleta e converte os valores dos campos de entrada
        delta_abs_sample = float(entries["gst_delta_abs_sample"].get())
        delta_abs_blank = float(entries["gst_delta_abs_blank"].get())
        protein_conc = float(entries["gst_protein"].get())
        path_length = float(entries["gst_path_length"].get())
        v_total = float(entries["gst_v_total"].get())
        v_sample = float(entries["gst_v_sample"].get())
        epsilon = 9.6  # Coeficiente de extinção molar para GST

        # Validação para evitar divisão por zero
        if protein_conc == 0 or path_length == 0 or v_sample == 0:
            messagebox.showerror("Erro de Entrada", "Concentração de proteína, caminho óptico e volume da amostra não podem ser zero.")
            return None

        # Cálculo da atividade
        delta_abs_corrected = delta_abs_sample - delta_abs_blank
        dilution_factor = v_total / v_sample
        
        numerator = delta_abs_corrected * dilution_factor * 1000  # Fator 1000 para converter para nmol
        denominator = epsilon * path_length * protein_conc
        
        if denominator == 0:
            messagebox.showerror("Erro de Cálculo", "O denominador do cálculo resultou em zero. Verifique os valores.")
            return None

        activity = numerator / denominator
        return f"{activity:.4f} nmol/min/mg"
        
    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos em todos os campos.")
        return None
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
        return None

# --- Criação da Interface Gráfica (GUI) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Atividade Enzimática")
        self.geometry("550x500")
        self.resizable(False, False)

        # Estilo para os widgets
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 11, 'bold'))
        style.configure("TFrame", background='#f0f0f0')
        
        # Dicionários para guardar os campos de entrada
        self.cat_entries = {}
        self.gst_entries = {}

        # Criação das abas (Notebook)
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Aba da Calculadora CAT
        cat_frame = ttk.Frame(notebook, padding="10")
        notebook.add(cat_frame, text="Catalase (CAT)")
        self.create_calculator_ui(cat_frame, "cat", self.cat_entries, self.on_calculate_cat)

        # Aba da Calculadora GST
        gst_frame = ttk.Frame(notebook, padding="10")
        notebook.add(gst_frame, text="GST")
        self.create_calculator_ui(gst_frame, "gst", self.gst_entries, self.on_calculate_gst)

    def create_calculator_ui(self, parent_frame, prefix, entry_dict, calc_command):
        """Função genérica para criar a interface de uma calculadora."""
        
        # Dicionário com os rótulos e valores padrão
        fields = {
            f"{prefix}_delta_abs_sample": ("ΔAbs/min (Amostra)", ""),
            f"{prefix}_delta_abs_blank": ("ΔAbs/min (Branco)", "0.0"),
            f"{prefix}_protein": ("Concentração de Proteína (mg/mL)", ""),
            f"{prefix}_path_length": ("Caminho Óptico (d) (cm)", "0.9"),
            f"{prefix}_v_total": ("Volume Total (Vt) (µL)", "300.0"),
            f"{prefix}_v_sample": ("Volume da Amostra (Vs) (µL)", "10.0" if prefix == "cat" else "20.0")
        }

        # Cria os rótulos e campos de entrada dinamicamente
        for i, (key, (label_text, default_value)) in enumerate(fields.items()):
            label = ttk.Label(parent_frame, text=label_text, font=('Helvetica', 10))
            label.grid(row=i, column=0, padx=10, pady=8, sticky="w")
            
            entry = ttk.Entry(parent_frame, width=20, font=('Helvetica', 10))
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            entry_dict[key] = entry

        # Botão de cálculo
        calc_button = ttk.Button(parent_frame, text="Calcular Atividade", command=calc_command)
        calc_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

        # Frame para o resultado
        result_frame = ttk.Frame(parent_frame, padding="10", relief="groove")
        result_frame.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew", padx=10)
        
        result_label_title = ttk.Label(result_frame, text="Resultado:", font=('Helvetica', 10, 'bold'))
        result_label_title.pack()
        
        result_label_value = ttk.Label(result_frame, text="", font=('Helvetica', 14, 'bold'), foreground="blue" if prefix == "cat" else "green")
        result_label_value.pack(pady=5)
        entry_dict[f"{prefix}_result_label"] = result_label_value

    def on_calculate_cat(self):
        """Função chamada ao clicar no botão de calcular CAT."""
        result = calculate_cat_activity(self.cat_entries)
        if result is not None:
            self.cat_entries["cat_result_label"].config(text=result)

    def on_calculate_gst(self):
        """Função chamada ao clicar no botão de calcular GST."""
        result = calculate_gst_activity(self.gst_entries)
        if result is not None:
            self.gst_entries["gst_result_label"].config(text=result)


if __name__ == "__main__":
    app = App()
    app.mainloop()
