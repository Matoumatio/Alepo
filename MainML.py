import csv
import os
import tkinter as tk
from tkinter import messagebox

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alepo Translate (v1.2)")
        self.root.config(bg="#2C3E50")
        self.help_window = None
        self.dictionary_window = None

        self.language = "FR"
        self.csv_files = {
            "FR": os.path.join(os.path.dirname(__file__), "DicoFR.csv"),
            "EN": os.path.join(os.path.dirname(__file__), "DicoEN.csv"),
            "WordDicoFR": os.path.join(os.path.dirname(__file__), "WordDicoFR.csv"),
            "WordDicoEN": os.path.join(os.path.dirname(__file__), "WordDicoEN.csv")
        }
        self.dictionary = {}
        self.word_dictionary = {}

        self.create_widgets()
        self.load_dictionary()

    def create_widgets(self):
        self.lang_button = tk.Button(
            self.root, text="Switch to English", command=self.switch_language, bg="#34495E", fg="white",
            font=("Helvetica", 12, "bold"), relief="flat", bd=0
        )
        self.lang_button.pack(pady=15, padx=10, side=tk.TOP)

        self.label = tk.Label(self.root, text="Entrez un mot ou une phrase :", font=("Helvetica", 14), bg="#2C3E50", fg="white")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root, width=50, font=("Helvetica", 12), bd=2, relief="solid", borderwidth=2,
                              highlightthickness=0, highlightbackground="#34495E")
        self.entry.pack(pady=10)

        self.translate_button = tk.Button(
            self.root, text="Obtenir la traduction", command=self.get_translation, bg="#2980B9", fg="white",
            font=("Helvetica", 12, "bold"), relief="flat", bd=0
        )
        self.translate_button.pack(pady=15)

        self.text_results = tk.Text(self.root, width=60, height=15, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 12),
                                    bg="#34495E", fg="white", bd=0)
        self.text_results.pack(pady=15)

        buttons_frame = tk.Frame(self.root, bg="#2C3E50")
        buttons_frame.pack(pady=10)
        self.help_button = tk.Button(
            buttons_frame, text="Aide", command=self.display_help, bg="#1ABC9C", fg="white",
            font=("Helvetica", 12, "bold"), relief="flat", bd=0
        )
        self.help_button.pack(side=tk.LEFT, padx=5)

        self.dictionary_button = tk.Button(
            buttons_frame, text="Dictionnaire", command=self.display_dictionary, bg="#1ABC9C", fg="white",
            font=("Helvetica", 12, "bold"), relief="flat", bd=0
        )
        self.dictionary_button.pack(side=tk.LEFT, padx=5)

    def load_dictionary(self):
        self.dictionary = self.load_csv(self.csv_files[self.language], 'Lettre (romanisée)', 'Traduction')
        self.word_dictionary = self.load_csv(self.csv_files[f"WordDico{self.language}"], 'Mot (romanisée)', ['Traduction littérale', 'Traduction'])

    def load_csv(self, file_path, key_field, value_fields):
        if not os.path.isfile(file_path):
            messagebox.showerror("Erreur", f"Fichier introuvable : {file_path}")
            return {}

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                if isinstance(value_fields, list):
                    return {row[key_field].strip(): {field: row[field].strip() for field in value_fields} for row in reader}
                else:
                    return {row[key_field].strip(): row[value_fields].strip() for row in reader}
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec du chargement du fichier : {e}")
            return {}

    def switch_language(self):
        self.language = "EN" if self.language == "FR" else "FR"
        self.update_ui_texts()
        self.load_dictionary()

    def update_ui_texts(self):
        if self.language == "FR":
            self.lang_button.config(text="Switch to English")
            self.label.config(text="Entrez un mot ou une phrase :")
            self.translate_button.config(text="Obtenir la traduction")
            self.help_button.config(text="Aide")
            self.dictionary_button.config(text="Dictionnaire")
        else:
            self.lang_button.config(text="Passer en Français")
            self.label.config(text="Enter a word or phrase:")
            self.translate_button.config(text="Get Translation")
            self.help_button.config(text="Help")
            self.dictionary_button.config(text="Dictionary")

    def get_translation(self):
        phrase = self.entry.get().strip().upper()
        if not phrase:
            messagebox.showwarning("Entrée vide", "Veuillez entrer un mot ou une phrase.")
            return

        words = phrase.split()
        results = [self.translate_word(word) for word in words]
        self.display_results(phrase, results)

    def translate_word(self, word):
        results = {}
        i = 0
        while i < len(word):
            found = False
            for j in range(3, 0, -1):
                if i + j <= len(word):
                    combination = word[i:i+j]
                    if combination in self.dictionary:
                        translation = self.dictionary[combination]
                        results[combination] = (
                            translation if translation
                            else "No translation available" if self.language == "EN"
                            else "Traduction inexistante"
                        )
                        i += j
                        found = True
                        break
            if not found:
                results[word[i]] = "Letter not found" if self.language == "EN" else "Lettre inexistante"
                i += 1
        return results

    def display_results(self, phrase, results):
        self.text_results.config(state=tk.NORMAL)
        self.text_results.delete(1.0, tk.END)
        self.text_results.insert(tk.END, f">>> {phrase}\n-----\n")
        for word_results in results:
            for letter, translation in word_results.items():
                self.text_results.insert(tk.END, f"{letter} - {translation}\n")
            self.text_results.insert(tk.END, "-----\n")
        self.text_results.config(state=tk.DISABLED)

    def display_help(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            help_text = (">>> Aide: Liste des lettres et leurs traductions\n" if self.language == "FR" 
                         else ">>> Help: List of letters and their translations\n")
            help_text += "-----\n"
            for letter, translation in self.dictionary.items():
                help_text += f"{letter} - {translation if translation else 'No translation available' if self.language == 'EN' else 'Traduction inexistante'}\n"
            help_text += "-----\n"

            self.help_window = tk.Toplevel()
            self.help_window.title("Aide" if self.language == "FR" else "Help")
            self.help_window.geometry("600x400")
            self.help_window.config(bg="#2C3E50")

            text_help = tk.Text(self.help_window, width=60, height=20, wrap=tk.WORD, bg="#34495E", fg="white", font=("Helvetica", 12), bd=0)
            text_help.pack(pady=10)
            text_help.insert(tk.END, help_text)
            text_help.config(state=tk.DISABLED)

    def display_dictionary(self):
        if self.dictionary_window is None or not self.dictionary_window.winfo_exists():
            dictionary_text = (">>> Dictionnaire des mots et phrases\n" if self.language == "FR" 
                               else ">>> Dictionary of words and phrases\n")
            dictionary_text += "-----\n"
            for romanized, details in self.word_dictionary.items():
                dictionary_text += f"{romanized} - {details['Traduction littérale']} - {details['Traduction']}\n"
            dictionary_text += "-----\n"

            self.dictionary_window = tk.Toplevel()
            self.dictionary_window.title("Dictionnaire" if self.language == "FR" else "Dictionary")
            self.dictionary_window.geometry("600x400")
            self.dictionary_window.config(bg="#2C3E50")

            text_dict = tk.Text(self.dictionary_window, width=60, height=20, wrap=tk.WORD, bg="#34495E", fg="white", font=("Helvetica", 12), bd=0)
            text_dict.pack(pady=10)
            text_dict.insert(tk.END, dictionary_text)
            text_dict.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
