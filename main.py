import tkinter as tk
from tkinter import ttk, messagebox
import csv
import tkinter.filedialog as filedialog
from tkinter.ttk import Treeview
from database import Database

USER = "admin"
PASSWORD = "admin"

def verificar_login():
    usuario = entry_user.get()
    senha = entry_password.get()

    if usuario == USER and senha == PASSWORD:
        janela_login.withdraw()
        abrir_dashboard()
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos")

class Dashboard:
    def __init__(self, master):
        self.master = master
        self.db = Database()
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Loja de Roupas - Dashboard")
        self.master.state('zoomed')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_main_frame()
        self.create_sidebar()
        self.create_product_list()
        self.refresh_product_list()

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.master, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def create_sidebar(self):
        sidebar = tk.Frame(self.main_frame, bg='#2c3e50', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        sidebar.pack_propagate(False)

        btn_style = {
            'width': 20,
            'height': 2,
            'bg': '#34495e',
            'fg': 'white',
            'font': ('Helvetica', 10),
            'relief': tk.FLAT,
            'activebackground': '#2980b9'
        }

        tk.Button(sidebar, text="Novo Produto", command=self.abrir_cadastro, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Atualizar Produto", command=self.abrir_atualizacao, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Exportar CSV", command=self.exportar_csv, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Atualizar Lista", command=self.refresh_product_list, **btn_style).pack(pady=10)

    def create_product_list(self):
        list_frame = tk.Frame(self.main_frame, bg='white')
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Tipo', 'Tamanho', 'Cor', 'Gênero', 'Preço', 'Descrição')
        self.tree = Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<Double-1>', self.on_item_select)

    def refresh_product_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for produto in self.db.get_all_produtos():
            self.tree.insert('', tk.END, values=produto)

    def abrir_cadastro(self):
        self.cadastro_window = tk.Toplevel(self.master)
        self.cadastro_window.title("Novo Produto")
        self.cadastro_window.geometry("400x500")
        
        campos = ['Tipo', 'Tamanho', 'Cor', 'Gênero', 'Preço', 'Descrição']
        self.entries = {}
        
        for i, campo in enumerate(campos):
            tk.Label(self.cadastro_window, text=campo).pack(pady=5)
            self.entries[campo] = tk.Entry(self.cadastro_window)
            self.entries[campo].pack(pady=5)
        
        tk.Button(self.cadastro_window, text="Salvar", 
                 command=self.save_product).pack(pady=20)

    def save_product(self):
        try:
            values = [self.entries[k].get() for k in self.entries]
            if not all(values):
                raise ValueError("Todos os campos devem ser preenchidos")
            
            self.db.add_produto(*values)
            self.refresh_product_list()
            self.cadastro_window.destroy()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def abrir_atualizacao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para atualizar")
            return
            
        item = self.tree.item(selected[0])
        self.update_window = tk.Toplevel(self.master)
        self.update_window.title("Atualizar Produto")
        self.update_window.geometry("400x500")
        
        self.update_entries = {}
        campos = ['Tipo', 'Tamanho', 'Cor', 'Gênero', 'Preço', 'Descrição']
        
        for i, (campo, valor) in enumerate(zip(campos, item['values'][1:])):
            tk.Label(self.update_window, text=campo).pack(pady=5)
            self.update_entries[campo] = tk.Entry(self.update_window)
            self.update_entries[campo].insert(0, valor)
            self.update_entries[campo].pack(pady=5)
        
        self.current_id = item['values'][0]
        
        tk.Button(self.update_window, text="Atualizar", 
                 command=self.update_product).pack(pady=10)
        tk.Button(self.update_window, text="Excluir", 
                 command=self.delete_product).pack(pady=10)

    def update_product(self):
        try:
            values = [self.update_entries[k].get() for k in self.update_entries]
            self.db.update_produto(self.current_id, *values)
            self.refresh_product_list()
            self.update_window.destroy()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def delete_product(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este produto?"):
            self.db.delete_produto(self.current_id)
            self.refresh_product_list()
            self.update_window.destroy()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")

    def on_item_select(self, event):
        self.abrir_atualizacao()

    def exportar_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filepath:
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Tipo', 'Tamanho', 'Cor', 'Gênero', 'Preço', 'Descrição'])
                for produto in self.db.get_all_produtos():
                    writer.writerow(produto)
            messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")

def abrir_dashboard():
    dashboard_window = tk.Toplevel()
    app = Dashboard(dashboard_window)
    dashboard_window.protocol("WM_DELETE_WINDOW", lambda: exit())

# Interface de Login
janela_login = tk.Tk()
janela_login.title("Login - Loja de Roupas")
janela_login.geometry("300x200")

frame_login = tk.Frame(janela_login, padx=20, pady=20)
frame_login.pack(expand=True)

tk.Label(frame_login, text="Usuário:").grid(row=0, column=0, pady=5)
entry_user = tk.Entry(frame_login)
entry_user.grid(row=0, column=1, pady=5)

tk.Label(frame_login, text="Senha:").grid(row=1, column=0, pady=5)
entry_password = tk.Entry(frame_login, show="*")
entry_password.grid(row=1, column=1, pady=5)

tk.Button(frame_login, text="Login", command=verificar_login).grid(row=2, column=0, columnspan=2, pady=20)

janela_login.mainloop()