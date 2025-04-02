import csv
import os
import numpy as np
from tkinter import messagebox
import time
import random
from abc import ABC, abstractmethod

class GerenciadorCSV:
    def __init__(self, arquivo_csv):
        self.arquivo_csv = arquivo_csv
        
    @classmethod #Metodos de Classe
    def total_usuarios(cls, arquivo_csv):
        if os.path.exists(arquivo_csv):
            with open(arquivo_csv, mode='r', newline='') as file:
                reader = csv.reader(file)
                usuarios = list(reader)
                return len(usuarios)
        return 0

    @classmethod #Metodos de Classe
    def usuario_existe(cls, arquivo_csv, usuario):
        if os.path.exists(arquivo_csv):
            with open(arquivo_csv, mode='r', newline='') as file:
                reader = csv.reader(file)
                for u in reader:
                    if u[0] == usuario:
                        return True
        return False


    def carregar_usuarios(self):
        usuarios = []
        if os.path.exists(self.arquivo_csv):
            with open(self.arquivo_csv, mode='r', newline='') as file:
                reader = csv.reader(file)
                usuarios = list(reader)
        return usuarios

    def salvar_usuario_em_arquivo(self, usuario, senha, metas="0", total_cubos_resolvidos="0", estado_cubo=None, movimentos_realizados=None):
        if movimentos_realizados is None:
            movimentos_realizados = []
        usuarios = self.carregar_usuarios()
        for u in usuarios:
            if u[0] == usuario:
                return 
        with open(self.arquivo_csv, mode='a', newline='') as file:
            writer = csv.writer(file)
            estado_cubo_str = self.converter_estado_cubo_para_str(estado_cubo)
            movimentos_str = self.converter_movimentos_para_str(movimentos_realizados)
            writer.writerow([usuario, senha, metas, total_cubos_resolvidos, estado_cubo_str, movimentos_str])

    def atualizar_usuario(self, usuario, metas, total_cubos_resolvidos, estado_cubo, movimentos_realizados=None):
        if movimentos_realizados is None:
            movimentos_realizados = []
        usuarios = self.carregar_usuarios()
        with open(self.arquivo_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            for u in usuarios:
                if u[0] == usuario:
                    u[2] = metas
                    u[3] = total_cubos_resolvidos
                    u[4] = self.converter_estado_cubo_para_str(estado_cubo)
                    u[5] = self.converter_movimentos_para_str(movimentos_realizados)
                writer.writerow(u)

    def obter_dados_usuario(self, usuario):
        usuarios = self.carregar_usuarios()
        for u in usuarios:
            if u[0] == usuario:
                metas = int(u[2])
                total_cubos_resolvidos = int(u[3])
                estado_cubo = self.converter_str_para_estado_cubo(u[4])
                movimentos_realizados = self.converter_str_para_movimentos(u[5])
                return metas, total_cubos_resolvidos, estado_cubo, movimentos_realizados
        return 0, 0, None, [] 

    def converter_estado_cubo_para_str(self, estado_cubo):
        if estado_cubo is None:
            return ""
        return ";".join([",".join(face.flatten()) for face in estado_cubo])

    def converter_str_para_estado_cubo(self, estado_str):
        if not estado_str:
            return None
        faces = estado_str.split(";")
        return [np.array(face.split(",")).reshape(3, 3) for face in faces]

    def converter_movimentos_para_str(self, movimentos):
        return ",".join(movimentos)

    def converter_str_para_movimentos(self, movimentos_str):
        if not movimentos_str:
            return []
        return movimentos_str.split(",")

class ClasseAbstrataLogin(ABC): #Classe Abstrata
    def __init__(self, gerenciador_csv):
        self.gerenciador_csv = gerenciador_csv
        self._usuario = None
        self._senha = None

    @abstractmethod
    def cadastrar(self, usuario, senha):
        pass

    @abstractmethod
    def login(self, usuario, senha):
        pass
    
class SistemaLogin(ClasseAbstrataLogin):
    def __init__(self, gerenciador_csv):
        self.gerenciador_csv = gerenciador_csv
        self._usuario = None #Encapsulamento
        self._senha = None #Encapsulamento

    @property
    def usuario(self):
        return self._usuario #get

    @usuario.setter
    def usuario(self, valor):
        self._usuario = valor #set

    @property
    def senha(self):
        return self._senha #get

    @senha.setter
    def senha(self, valor):
        self._senha = valor #set

    def cadastrar(self, usuario, senha):
        self.usuario = usuario
        self.senha = senha
        usuarios = self.gerenciador_csv.carregar_usuarios()
        for u in usuarios:
            if u[0] == self.usuario:
                return "Usuário já cadastrado."
        self.gerenciador_csv.salvar_usuario_em_arquivo(self.usuario, self.senha, 0, 0)
        return "Usuário cadastrado com sucesso."

    def login(self, usuario, senha):
        self.usuario = usuario
        self.senha = senha
        usuarios = self.gerenciador_csv.carregar_usuarios()
        for u in usuarios:
            if u[0] == self.usuario:
                if u[1] == self.senha:
                    return True
                else:
                    return False
        return False

class Jogador(SistemaLogin): 
    def __init__(self, gerenciador_csv, usuario, meta=0, total_cubos_resolvidos=0):
        super().__init__(gerenciador_csv)
        self.usuario = usuario
        self.total_cubos_resolvidos = int(total_cubos_resolvidos)
        self.meta = int(meta)

    def verificar_metas(self, tempo_decorrido):
        if self.total_cubos_resolvidos == 5:
            messagebox.showinfo("Metas", "Total de 5 cubos resolvidos!")
            self.meta += 1
        
        if self.total_cubos_resolvidos == 10:
            messagebox.showinfo("Metas", "Total de 10 cubos resolvidos!")
            self.meta += 1
        
        if self.total_cubos_resolvidos == 50:
            messagebox.showinfo("Metas", "Total de 50 cubos resolvidos!")
            self.meta += 1

            self.gerenciador_csv.atualizar_usuario(self.usuario, self.meta, self.total_cubos_resolvidos, self.obter_estado_cubo())
            return True
        return False

class Puzle: 
    def __init__(self, dificuldade=1):
        self.dificuldade = dificuldade

class CuboMagico(Jogador, Puzle): #Herança Multipla 
    def __init__(self, gerenciador_csv, usuario, meta=0, total_cubos_resolvidos=0, estado_cubo=None):
        super().__init__(gerenciador_csv, usuario, meta=meta, total_cubos_resolvidos=total_cubos_resolvidos)
        Puzle.__init__(self, dificuldade=5)

        if estado_cubo is None:
            self.facewhite = np.array([
            ["w", "w", "w"],  
            ["w", "w", "w"], 
            ["w", "w", "w"]
        ])
            self.faceyellow = np.array([
                ["y", "y", "y"],  
                ["y", "y", "y"], 
                ["y", "y", "y"]   
            ])
            self.faceblue = np.array([
                ["b", "b", "b"],  
                ["b", "b", "b"], 
                ["b", "b", "b"]   
            ])
            self.facegreen = np.array([
                ["g", "g", "g"],  
                ["g", "g", "g"], 
                ["g", "g", "g"]   
            ])
            self.facered = np.array([
                ["r", "r", "r"],  
                ["r", "r", "r"], 
                ["r", "r", "r"]   
            ])
            self.faceorange = np.array([
                ["o", "o", "o"],  
                ["o", "o", "o"], 
                ["o", "o", "o"]   
            ])
        else:
            self.facewhite, self.faceyellow, self.faceblue, self.facegreen, self.facered, self.faceorange = estado_cubo

    def obter_estado_cubo(self):
        return [self.facewhite, self.faceyellow, self.faceblue, self.facegreen, self.facered, self.faceorange]

    def f(self): 
        temp_w = self.facewhite[2, :].copy()
        temp_r = self.facered[:, 0].copy()
        temp_y = self.faceyellow[0, :].copy()
        temp_o = self.faceorange[:, 2].copy()

        self.facered[:, 0] = temp_w
        self.faceyellow[0, :] = temp_r[::-1]
        self.faceorange[:, 2] = temp_y
        self.facewhite[2, :] = temp_o[::-1]

        self.facegreen = np.rot90(self.facegreen, -1)  

    def f_inverse(self):
        temp_w = self.facewhite[2, :].copy()
        temp_r = self.facered[:, 0].copy()
        temp_y = self.faceyellow[0, :].copy()
        temp_o = self.faceorange[:, 2].copy()

        self.facered[:, 0] = temp_y[::-1]
        self.faceyellow[0, :] = temp_o
        self.faceorange[:, 2] = temp_w[::-1]
        self.facewhite[2, :] = temp_r

        self.facegreen = np.rot90(self.facegreen, 1) 

    def r(self): 
        temp_w = self.facewhite[:, 2].copy()
        temp_y = self.faceyellow[:, 2].copy()
        temp_g = self.facegreen[:, 2].copy()
        temp_b = self.faceblue[:, 0].copy()

        self.facewhite[:, 2] = temp_g
        self.faceyellow[:, 2] = temp_b
        self.facegreen[:, 2] = temp_y
        self.faceblue[:, 0] = temp_w

        self.facered = np.rot90(self.facered, -1)  

    def r_inverse(self): 
        temp_w = self.facewhite[:, 2].copy()
        temp_y = self.faceyellow[:, 2].copy()
        temp_g = self.facegreen[:, 2].copy()
        temp_b = self.faceblue[:, 0].copy()

        self.facewhite[:, 2] = temp_b
        self.faceyellow[:, 2] = temp_g
        self.facegreen[:, 2] = temp_w
        self.faceblue[:, 0] = temp_y

        self.facered = np.rot90(self.facered, 1) 

    def u(self):
        temp_g = self.facegreen[0, :].copy()
        temp_b = self.faceblue[0, :].copy()
        temp_r = self.facered[0, :].copy()
        temp_o = self.faceorange[0, :].copy()

        self.facegreen[0, :] = temp_r
        self.faceblue[0, :] = temp_o
        self.facered[0, :] = temp_b
        self.faceorange[0, :] = temp_g

        self.facewhite = np.rot90(self.facewhite, -1)

    def u_inverse(self):
        temp_g = self.facegreen[0, :].copy()
        temp_b = self.faceblue[0, :].copy()
        temp_r = self.facered[0, :].copy()
        temp_o = self.faceorange[0, :].copy()

        self.facegreen[0, :] = temp_o
        self.faceblue[0, :] = temp_r
        self.facered[0, :] = temp_g
        self.faceorange[0, :] = temp_b

        self.facewhite = np.rot90(self.facewhite, 1)

    def b(self):
        temp_w = self.facewhite[0, :].copy()
        temp_y = self.faceyellow[2, :].copy()
        temp_r = self.facered[:, 2].copy()
        temp_o = self.faceorange[:, 0].copy()

        self.facewhite[0, :] = temp_r[::-1]
        self.faceyellow[2, :] = temp_o[::-1]
        self.facered[:, 2] = temp_y[::-1]
        self.faceorange[:, 0] = temp_w[::-1]

        self.faceblue = np.rot90(self.faceblue, -1)

    def b_inverse(self):
        temp_w = self.facewhite[0, :].copy()
        temp_y = self.faceyellow[2, :].copy()
        temp_r = self.facered[:, 2].copy()
        temp_o = self.faceorange[:, 0].copy()

        self.facewhite[0, :] = temp_o[::-1]
        self.faceyellow[2, :] = temp_r[::-1]
        self.facered[:, 2] = temp_w[::-1]
        self.faceorange[:, 0] = temp_y[::-1]

        self.faceblue = np.rot90(self.faceblue, 1)

    def l(self):
        temp_w = self.facewhite[:, 0].copy()
        temp_y = self.faceyellow[:, 0].copy()
        temp_g = self.facegreen[:, 0].copy()
        temp_b = self.faceblue[:, 2].copy()

        self.facewhite[:, 0] = temp_b
        self.faceyellow[:, 0] = temp_g
        self.facegreen[:, 0] = temp_w
        self.faceblue[:, 2] = temp_y

        self.faceorange = np.rot90(self.faceorange, -1)

    def l_inverse(self):
        temp_w = self.facewhite[:, 0].copy()
        temp_y = self.faceyellow[:, 0].copy()
        temp_g = self.facegreen[:, 0].copy()
        temp_b = self.faceblue[:, 2].copy()

        self.facewhite[:, 0] = temp_g
        self.faceyellow[:, 0] = temp_b
        self.facegreen[:, 0] = temp_y
        self.faceblue[:, 2] = temp_w

        self.faceorange = np.rot90(self.faceorange, 1)

    def d(self):
        temp_g = self.facegreen[2, :].copy()
        temp_b = self.faceblue[2, :].copy()
        temp_r = self.facered[2, :].copy()
        temp_o = self.faceorange[2, :].copy()

        self.facegreen[2, :] = temp_o
        self.faceblue[2, :] = temp_r
        self.facered[2, :] = temp_g
        self.faceorange[2, :] = temp_b

        self.faceyellow = np.rot90(self.faceyellow, -1)

    def d_inverse(self):
        temp_g = self.facegreen[2, :].copy()
        temp_b = self.faceblue[2, :].copy()
        temp_r = self.facered[2, :].copy()
        temp_o = self.faceorange[2, :].copy()

        self.facegreen[2, :] = temp_r
        self.faceblue[2, :] = temp_o
        self.facered[2, :] = temp_b
        self.faceorange[2, :] = temp_g

        self.faceyellow = np.rot90(self.faceyellow, 1)

class Movimento(CuboMagico):
    def __init__(self, gerenciador_csv, usuario, meta=0, total_cubos_resolvidos=0, estado_cubo=None):
        super().__init__(gerenciador_csv, usuario, meta=meta, total_cubos_resolvidos=total_cubos_resolvidos, estado_cubo=estado_cubo)
        self.movimentos_realizados = []
        self.tempo_inicial = None

    def iniciar_cronometro(self):
        if self.tempo_inicial is None:
            self.tempo_inicial = time.time()
            messagebox.showinfo("Cronometro", "Cronometro iniciado!")

    def parar_cronometro(self):
        if self.tempo_inicial is not None:
            tempo_final = time.time()
            tempo_decorrido = tempo_final - self.tempo_inicial
            messagebox.showinfo("Cronometro", f"Tempo decorrido: {tempo_decorrido:.2f} segundos")
            self.tempo_inicial = None

    def verificar_resolucao(self):
        faces = [self.facewhite, self.faceyellow, self.faceblue, self.facegreen, self.facered, self.faceorange]
        cores = ['w', 'y', 'b', 'g', 'r', 'o']
        for i in range(6):
            if not np.all(faces[i] == cores[i]):
                return False

        self.total_cubos_resolvidos += 1
        self.parar_cronometro()  

        self.gerenciador_csv.atualizar_usuario(self.usuario, self.meta, self.total_cubos_resolvidos, self.obter_estado_cubo())
        self.verificar_metas(None)
        return True

    def embaralhar(self, movimentos=20):
        movimentos_possiveis = ['f', 'f_inverse', 'r', 'r_inverse', 'u', 'u_inverse', 
                                'b', 'b_inverse', 'l', 'l_inverse', 'd', 'd_inverse']
        
        for _ in range(movimentos):
            movimento_escolhido = random.choice(movimentos_possiveis)
            self.movimentos_realizados.append(movimento_escolhido)
            
            if movimento_escolhido == 'f':
                self.f()
            elif movimento_escolhido == 'f_inverse':
                self.f_inverse()
            elif movimento_escolhido == 'r':
                self.r()
            elif movimento_escolhido == 'r_inverse':
                self.r_inverse()
            elif movimento_escolhido == 'u':
                self.u()
            elif movimento_escolhido == 'u_inverse':
                self.u_inverse()
            elif movimento_escolhido == 'b':
                self.b()
            elif movimento_escolhido == 'b_inverse':
                self.b_inverse()
            elif movimento_escolhido == 'l':
                self.l()
            elif movimento_escolhido == 'l_inverse':
                self.l_inverse()
            elif movimento_escolhido == 'd':
                self.d()
            elif movimento_escolhido == 'd_inverse':
                self.d_inverse()

    def autosolver(self):
        for movimento in reversed(self.movimentos_realizados):
            if movimento == 'f':
                self.f_inverse()
            elif movimento == 'f_inverse':
                self.f()
            elif movimento == 'r':
                self.r_inverse()
            elif movimento == 'r_inverse':
                self.r()
            elif movimento == 'u':
                self.u_inverse()
            elif movimento == 'u_inverse':
                self.u()
            elif movimento == 'b':
                self.b_inverse()
            elif movimento == 'b_inverse':
                self.b()
            elif movimento == 'l':
                self.l_inverse()
            elif movimento == 'l_inverse':
                self.l()
            elif movimento == 'd':
                self.d_inverse()
            elif movimento == 'd_inverse':
                self.d()

        messagebox.showinfo("AutoSolver", "Cubo resolvido automaticamente!")
        self.movimentos_realizados.clear()