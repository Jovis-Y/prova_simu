import simpy #
from config import CAPACIDADES #

class Aeroporto:
    """
    Encapsula todos os recursos físicos do aeroporto modelados 
    como Resources do SimPy para controle de filas e concorrência.[cite: 1]
    Além disso, atua como gerenciador das rotinas de alocação de infraestrutura.
    """
    def __init__(self, env: simpy.Environment):
        self.env = env #[cite: 1]
        
        # Alocação das capacidades definidas nas configurações (config.py)[cite: 1]
        self.pistas_pequenas = simpy.Resource(env, capacity=CAPACIDADES['pistas_pequenas']) #[cite: 1]
        self.pista_grande = simpy.Resource(env, capacity=CAPACIDADES['pista_grande']) #[cite: 1]
        self.plataformas = simpy.Resource(env, capacity=CAPACIDADES['plataformas']) #[cite: 1]
        self.hangares = simpy.Resource(env, capacity=CAPACIDADES['hangares']) #[cite: 1]
        
        # Monitoramento de Estado (KPIs)
        self.aeronaves_em_solo = 0
        self.total_pousos = 0
        self.total_decolagens = 0

    def gerenciar_pouso(self, nome_aeronave: str, tipo_tamanho: str, tempo_pouso: int):
        """
        Processo que aloca a pista apropriada e simula a aproximação e o pouso.
        Aeronaves 'grandes' exigem a pista grande; outras priorizam as pistas pequenas.
        """
        pista = self.pista_grande if tipo_tamanho == 'grande' else self.pistas_pequenas #[cite: 1]
        
        with pista.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} autorizada para pouso.")
            yield self.env.timeout(tempo_pouso)
            
            self.aeronaves_em_solo += 1
            self.total_pousos += 1
            print(f"[{self.env.now:05.1f}] {nome_aeronave} concluiu o pouso com sucesso.")

    def utilizar_plataforma(self, nome_aeronave: str, tempo_operacao: int):
        """
        Aloca uma plataforma para procedimentos de embarque, desembarque e abastecimento.
        """
        with self.plataformas.request() as req: #[cite: 1]
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} acoplada na plataforma.")
            yield self.env.timeout(tempo_operacao)
            print(f"[{self.env.now:05.1f}] {nome_aeronave} liberou a plataforma.")

    def realizar_manutencao(self, nome_aeronave: str, tempo_manutencao: int):
        """
        Encaminha a aeronave para o hangar, bloqueando o recurso durante o período de reparo.
        """
        with self.hangares.request() as req: #[cite: 1]
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} iniciou manutenção no hangar.")
            yield self.env.timeout(tempo_manutencao)
            print(f"[{self.env.now:05.1f}] {nome_aeronave} finalizou a manutenção e liberou o hangar.")

    def gerenciar_decolagem(self, nome_aeronave: str, tipo_tamanho: str, tempo_decolagem: int):
        """
        Solicita a pista adequada para a saída e libera a aeronave do sistema.
        """
        pista = self.pista_grande if tipo_tamanho == 'grande' else self.pistas_pequenas #[cite: 1]
        
        with pista.request() as req:
            yield req
            print(f"[{self.env.now:05.1f}] {nome_aeronave} autorizada para decolagem.")
            yield self.env.timeout(tempo_decolagem)
            
            self.aeronaves_em_solo -= 1
            self.total_decolagens += 1
            print(f"[{self.env.now:05.1f}] {nome_aeronave} decolou e deixou o espaço aéreo.")