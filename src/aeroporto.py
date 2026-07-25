import simpy
from config import CAPACIDADES

class Aeroporto:
    def __init__(self, env: simpy.Environment):
        self.env = env
        
        self.pistas_pequenas = simpy.Resource(env, capacity=CAPACIDADES['pistas_pequenas'])
        self.pista_grande = simpy.Resource(env, capacity=CAPACIDADES['pista_grande'])
        self.plataformas = simpy.Resource(env, capacity=CAPACIDADES['plataformas'])
        self.hangares = simpy.Resource(env, capacity=CAPACIDADES['hangares'])
        
        self.aeronaves_em_solo = 0
        self.total_pousos = 0
        self.total_decolagens = 0

    def gerenciar_pouso(self, nome_aeronave: str, tipo_tamanho: str, tempo_pouso: int):
        pista = self.pista_grande if tipo_tamanho == 'grande' else self.pistas_pequenas
        
        with pista.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} autorizada para pouso.")
            yield self.env.timeout(tempo_pouso)
            
            self.aeronaves_em_solo += 1
            self.total_pousos += 1
            print(f"[{self.env.now:05.1f}] {nome_aeronave} concluiu o pouso com sucesso.")

    def utilizar_plataforma(self, nome_aeronave: str, tempo_operacao: int):
        with self.plataformas.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} acoplada na plataforma.")
            yield self.env.timeout(tempo_operacao)
            print(f"[{self.env.now:05.1f}] {nome_aeronave} liberou a plataforma.")

    def realizar_manutencao(self, nome_aeronave: str, tempo_manutencao: int):
        with self.hangares.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} iniciou manutenção no hangar.")
            yield self.env.timeout(tempo_manutencao)
            print(f"[{self.env.now:05.1f}] {nome_aeronave} finalizou a manutenção e liberou o hangar.")

    def gerenciar_decolagem(self, nome_aeronave: str, tipo_tamanho: str, tempo_decolagem: int):
        pista = self.pista_grande if tipo_tamanho == 'grande' else self.pistas_pequenas
        
        with pista.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} autorizada para decolagem.")
            yield self.env.timeout(tempo_decolagem)
            
            self.aeronaves_em_solo -= 1
            self.total_decolagens += 1
            print(f"[{self.env.now:05.1f}] {nome_aeronave} decolou e deixou o espaço aéreo.")