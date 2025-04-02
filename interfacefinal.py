import tkinter as tk
from tkinter import messagebox
import pygame
from lib import SistemaLogin, Movimento, GerenciadorCSV

class InterfaceCuboMagico(SistemaLogin):
    def __init__(self, root, gerenciador_csv):
        super().__init__(gerenciador_csv)
        self.root = root
        self.gerenciador_csv = gerenciador_csv
        self.usuario_logado = None

        self.root.title("Sistema de Cubo Mágico")
        self.root.geometry("800x600")

        self.frame_login = tk.Frame(self.root)
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

        self.criar_tela_login()

    def criar_tela_login(self):
        tk.Label(self.frame_login, text="Cadastro", font=("Merriweather", 15)).pack(pady=5)
        tk.Label(self.frame_login, text="Usuário:").pack(pady=5)
        
        self.entry_usuario = tk.Entry(self.frame_login)
        self.entry_usuario.pack(pady=5)
        
        tk.Label(self.frame_login, text="Senha:").pack(pady=5)
        
        self.entry_senha = tk.Entry(self.frame_login, show="*")
        self.entry_senha.pack(pady=5)

        frame_botoes = tk.Frame(self.frame_login)
        frame_botoes.pack(pady=5)

        tk.Button(frame_botoes, text="Cadastrar", command=self.cadastrar_usuario).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Login", command=self.login_usuario).pack(side="left", padx=5)

    def cadastrar_usuario(self):
        self.usuario = self.entry_usuario.get()  
        self.senha = self.entry_senha.get()  
        if GerenciadorCSV.usuario_existe(self.gerenciador_csv.arquivo_csv, self.usuario):
            messagebox.showerror("Cadastro", "Usuário já cadastrado.")
        else:
            mensagem = self.cadastrar(self.usuario, self.senha)
            self.gerenciador_csv.salvar_usuario_em_arquivo(self.usuario, self.senha, "0", "0")
            messagebox.showinfo("Cadastro", mensagem)

    def login_usuario(self):
        self.usuario = self.entry_usuario.get()  
        self.senha = self.entry_senha.get()  
        if self.login(self.usuario, self.senha):
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            self.usuario_logado = self.usuario
            metas, total_cubos_resolvidos, estado_cubo, movimentos_realizados = self.gerenciador_csv.obter_dados_usuario(self.usuario)
            total_usuarios = GerenciadorCSV.total_usuarios(self.gerenciador_csv.arquivo_csv)
            messagebox.showinfo("Total de Usuários", f"Você é o nosso usuário número {total_usuarios}!")
            self.root.destroy() 
            iniciar_pygame(self.usuario, metas, total_cubos_resolvidos, estado_cubo, movimentos_realizados) 
        else:
            messagebox.showerror("Login", "Usuário ou senha incorretos.")
def iniciar_pygame(usuario, metas, total_cubos_resolvidos, estado_cubo, movimentos_realizados):
    gerenciador_csv = GerenciadorCSV("usuarios.csv")
    movimento = Movimento(gerenciador_csv, usuario, meta=metas, total_cubos_resolvidos=total_cubos_resolvidos, estado_cubo=estado_cubo)
    movimento.movimentos_realizados = movimentos_realizados
    interface = InterfacePygame(movimento)
    interface.loop_principal()

class InterfacePygame:
    def __init__(self, movimento):
        self.movimento = movimento
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Cubo Mágico")
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.background = pygame.image.load("C:/Users/oaugu/Downloads/backgroung.jpeg")
        self.background = pygame.transform.scale(self.background, (800, 600))

    def salvar_estado_cubo(self):
        self.movimento.gerenciador_csv.atualizar_usuario(
            self.movimento.usuario,
            self.movimento.meta,
            self.movimento.total_cubos_resolvidos,
            self.movimento.obter_estado_cubo(),
            self.movimento.movimentos_realizados
        )
    def desenhar_cubo(self):
        cores = {
            'w': (255, 255, 255),
            'y': (255, 255, 0),
            'b': (0, 0, 255),
            'g': (0, 255, 0),
            'r': (255, 0, 0),
            'o': (255, 165, 0)
        }
        faces = {
            'w': self.movimento.facewhite,
            'y': self.movimento.faceyellow,
            'b': self.movimento.faceblue,
            'g': self.movimento.facegreen,
            'r': self.movimento.facered,
            'o': self.movimento.faceorange
        }
        posicoes = {
            'w': (300, 160),
            'g': (300, 280),
            'y': (300, 400),
            'o': (180, 280),
            'r': (420, 280),
            'b': (540, 280)
        }
        
        for cor, face in faces.items():
            pos = posicoes[cor]
            for i in range(3):
                for j in range(3):
                    pygame.draw.rect(self.screen, cores[face[i, j]], (pos[0] + j*40, pos[1] + i*40, 40, 40))
                    pygame.draw.rect(self.screen, (0, 0, 0), (pos[0] + j*40, pos[1] + i*40, 40, 40), 1)

    def loop_principal(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.salvar_estado_cubo()
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if event.key == pygame.K_c:
                        self.movimento.iniciar_cronometro()
                    elif event.key == pygame.K_f:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.f_inverse()
                            self.movimento.movimentos_realizados.append('f_inverse')
                        else:
                            self.movimento.f()
                            self.movimento.movimentos_realizados.append('f')
                    elif event.key == pygame.K_r:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.r_inverse()
                            self.movimento.movimentos_realizados.append('r_inverse')
                        else:
                            self.movimento.r()
                            self.movimento.movimentos_realizados.append('r')
                    elif event.key == pygame.K_u:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.u_inverse()
                            self.movimento.movimentos_realizados.append('u_inverse')
                        else:
                            self.movimento.u()
                            self.movimento.movimentos_realizados.append('u')
                    elif event.key == pygame.K_b:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.b_inverse()
                            self.movimento.movimentos_realizados.append('b_inverse')
                        else:
                            self.movimento.b()
                            self.movimento.movimentos_realizados.append('b')
                    elif event.key == pygame.K_l:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.l_inverse()
                            self.movimento.movimentos_realizados.append('l_inverse')
                        else:
                            self.movimento.l()
                            self.movimento.movimentos_realizados.append('l')
                    elif event.key == pygame.K_d:
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            self.movimento.d_inverse()
                            self.movimento.movimentos_realizados.append('d_inverse')
                        else:
                            self.movimento.d()
                            self.movimento.movimentos_realizados.append('d')
                    elif event.key == pygame.K_s:
                        self.movimento.embaralhar()
                    elif event.key == pygame.K_a:
                        self.movimento.autosolver()

                    if self.movimento.verificar_resolucao():
                        self.movimento.parar_cronometro()

            self.screen.blit(self.background, (0, 0))
            self.desenhar_cubo()
            pygame.display.flip()

        pygame.quit()

def main():
    arquivo_csv = "usuarios.csv"
    gerenciador_csv = GerenciadorCSV(arquivo_csv)

    root = tk.Tk()
    app = InterfaceCuboMagico(root, gerenciador_csv)
    root.mainloop()

if __name__ == "__main__":
    main()