import sqlite3

class Database:
    def __init__(self, db_name='loja_roupas.db'):
        self.conn = sqlite3.connect(db_name)
        self.criar_tabela()

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            tam TEXT NOT NULL,
            cor TEXT NOT NULL,
            gen TEXT NOT NULL,
            prec REAL NOT NULL,
            desc TEXT
        )
        ''')
        self.conn.commit()

    def add_produto(self, tipo, tam, cor, gen, prec, desc):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO produto (tipo, tam, cor, gen, prec, desc)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tipo, tam, cor, gen, prec, desc))
        self.conn.commit()

    def get_all_produtos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM produto')
        return cursor.fetchall()

    def update_produto(self, pid, tipo, tam, cor, gen, prec, desc):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE produto
            SET tipo=?, tam=?, cor=?, gen=?, prec=?, desc=?
            WHERE id=?
        ''', (tipo, tam, cor, gen, prec, desc, pid))
        self.conn.commit()

    def delete_produto(self, pid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM produto WHERE id=?', (pid,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()