import csv
import random
from faker import Faker
from datetime import datetime

NUMERO_DE_PEDIDOS = 1000
NOME_ARQUIVO = 'vendas_faker.csv'

fake = Faker('pt_BR')


PRODUTOS_POR_CATEGORIA = {
    'Eletrônicos': {
        'E01': ('Smartphone Z', 1599.90),
        'E02': ('Notebook Titan', 4299.00),
        'E03': ('Smartwatch Connect', 899.50),
        'E04': ('Tablet Vision', 1100.00),
        'E05': ('Fone de Ouvido Wave', 129.90),
        'E06': ('Monitor UltraWide 29"', 1350.00),
        'E07': ('Teclado Mecânico Gamer', 350.00),
        'E08': ('Mouse Óptico Pro', 99.90),
        'E09': ('Caixa de Som Bluetooth Max', 250.00),
        'E10': ('Webcam Full HD', 180.00),
    },
    'Livros': {
        'L01': ('O Segredo dos Dados', 55.00),
        'L02': ('A Ascensão do Código', 49.90),
        'L03': ('Beam em Ação', 79.90),
        'L04': ('Ficção Científica: Andromeda', 38.00),
        'L05': ('Biografia: A Mente Criadora', 62.50),
        'L06': ('Culinária para Iniciantes', 45.00),
        'L07': ('História do Brasil Colonial', 72.00),
        'L08': ('A Arte da Guerra', 30.00),
        'L09': ('Investimentos Inteligentes', 58.00),
        'L10': ('Contos Fantásticos', 41.50),
    },
    'Casa e Jardim': {
        'CJ01': ('Cadeira de Escritório Ergonômica', 249.90),
        'CJ02': ('Luminária de Mesa LED', 89.00),
        'CJ03': ('Kit Ferramentas 50 peças', 150.00),
        'CJ04': ('Vaso de Cerâmica Decorativo', 65.00),
        'CJ05': ('Jogo de Panelas Antiaderente', 299.90),
        'CJ06': ('Aspirador de Pó Vertical', 450.00),
        'CJ07': ('Prateleira de Madeira Maciça', 120.00),
        'CJ08': ('Cortina Blackout', 95.50),
        'CJ09': ('Regador de Plantas 5L', 40.00),
        'CJ10': ('Mesa de Centro Moderna', 180.00),
    },
    'Alimentos e Bebidas': {
        'AB01': ('Café Gourmet Grãos 1kg', 45.00),
        'AB02': ('Azeite Extra Virgem 500ml', 28.00),
        'AB03': ('Vinho Tinto Chileno', 65.00),
        'AB04': ('Chocolate Amargo 70%', 15.50),
        'AB05': ('Caixa de Chá Importado', 35.00),
        'AB06': ('Arroz Arbóreo para Risoto', 22.00),
        'AB07': ('Geleia Artesanal de Morango', 18.00),
        'AB08': ('Queijo Parmesão Peça', 55.00),
        'AB09': ('Suco de Uva Integral 1.5L', 19.90),
        'AB10': ('Mel Silvestre Orgânico', 32.00),
    },
    'Esportes e Lazer': {
        'EL01': ('Bicicleta Aro 29', 1200.00),
        'EL02': ('Tênis de Corrida', 350.00),
        'EL03': ('Bola de Futebol Oficial', 120.00),
        'EL04': ('Kit Halteres 10kg', 180.00),
        'EL05': ('Tapete de Yoga', 90.00),
        'EL06': ('Garrafa Térmica Inox 1L', 75.00),
        'EL07': ('Barraca de Camping 4 Pessoas', 450.00),
        'EL08': ('Raquete de Tênis', 280.00),
        'EL09': ('Óculos de Natação', 60.00),
        'EL10': ('Corda de Pular Profissional', 45.00),
    }
}

STATUS_ENTREGA = ['ENTREGUE', 'CANCELADO', 'EM_TRANSITO']
HEADER = ['ID_Pedido', 'Data_Pedido', 'ID_Cliente', 'Nome_Cliente', 'Itens_Pedido', 'Categoria', 'Status_Entrega', 'Cidade_Entrega', 'Valor_Frete']

lista_clientes = [(f'CLI{fake.unique.random_int(min=100, max=500)}', fake.name()) for _ in range(NUMERO_DE_PEDIDOS // 4)]

def gerar_itens_pedido(categoria):
    itens = []
    num_itens = 1 if random.random() < 0.8 else random.randint(2, 3)

    produtos_da_categoria = list(PRODUTOS_POR_CATEGORIA[categoria].items())

    for _ in range(num_itens):
        id_produto, (_, preco_base) = random.choice(produtos_da_categoria)
        preco_unitario = round(preco_base * random.uniform(0.95, 1.05), 2)
        quantidade = random.randint(1, 5)
        itens.append(f"{id_produto}:{preco_unitario}:{quantidade}")

    return ";".join(itens)


print(f"Gerando {NUMERO_DE_PEDIDOS} registros para o arquivo '{NOME_ARQUIVO}'...")

with open(NOME_ARQUIVO, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)

    for i in range(NUMERO_DE_PEDIDOS):
        id_pedido = 101 + i
        data_pedido = fake.date_between(start_date='-2y', end_date='today')
        id_cliente, nome_cliente = random.choice(lista_clientes)

        if random.random() < 0.1:
            nome_cliente = f" {nome_cliente} "

        categoria_original = random.choice(list(PRODUTOS_POR_CATEGORIA.keys()))

        itens_pedido = gerar_itens_pedido(categoria_original)

        categoria_final = categoria_original
        if random.random() < 0.2:
            categoria_final = categoria_original.lower()

        status = random.choices(STATUS_ENTREGA, weights=[75, 10, 15], k=1)[0]

        cidade = fake.city()
        if random.random() < 0.05:
            cidade = ''

        valor_frete = round(random.uniform(5.0, 80.0), 2)

        writer.writerow([
            id_pedido,
            data_pedido,
            id_cliente,
            nome_cliente,
            itens_pedido,
            categoria_final,
            status,
            cidade,
            valor_frete
        ])
