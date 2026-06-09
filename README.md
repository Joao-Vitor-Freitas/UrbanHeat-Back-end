# UrbanHeat

Sistema de monitoramento ambiental desenvolvido para a Global Solution da FIAP. O UrbanHeat coleta, armazena e analisa dados de temperatura e umidade para mapear ilhas de calor urbanas em Porto Alegre. O objetivo é fornecer a gestores públicos uma ferramenta ágil e baseada em dados para priorizar intervenções de mitigação climática, como arborização e pavimentação sustentável.

## O que é o HeatScore?

O **HeatScore** é o motor analítico do projeto. Trata-se de um índice de 0 a 100 que quantifica a severidade térmica de uma região utilizando os dados dos últimos 30 dias. 

Em vez de se basear apenas na temperatura instantânea, o algoritmo avalia o comportamento crônico do clima da região:

$$HeatScore = \left(\frac{T_{avg}}{50}\right) \times 40 + (F_{high} \times 30) + (D_{crit} \times 20) + (P_{hum} \times 10)$$

* **$T_{avg}$ (Peso 40):** Temperatura média histórica.
* **$F_{high}$ (Peso 30):** Frequência de leituras extremas ($\ge 35^\circ C$).
* **$D_{crit}$ (Peso 20):** Duração do tempo em que a região permaneceu sob calor crítico.
* **$P_{hum}$ (Peso 10):** Penalidade proporcional à escassez de umidade no ar.

As regiões são então classificadas automaticamente em quatro níveis de alerta: **Low** (0-24), **Moderate** (25-49), **High** (50-74) e **Critical** (75-100).

---

## 🚀 Como Executar o Projeto (Ambiente Local)

O ambiente foi configurado para rodar de forma isolada, via software, permitindo o desenvolvimento e validação sem a necessidade do hardware do Arduino conectado.

**1. Instale as dependências do Python**
```bash
pip install -r requirements.txt
```

**2. Inicie a API (Backend)**
O comando abaixo irá inicializar o servidor e criar o banco de dados local `urbanheat.db` com todas as tabelas necessárias automaticamente. 

Certifique-se de estar dentro do diretório do projeto e com o ambiente virtual ativado (se estiver usando um).

```bash
uvicorn api:app --reload
```


**3. Teste a API REST**
Com o servidor rodando, abra seu navegador para acessar a documentação interativa gerada automaticamente pelo FastAPI (Swagger UI). Nela você poderá inspecionar e testar todos os endpoints de forma visual:

* 🔗 **Acesse:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Cadastre Regiões e Sensores
Antes de enviar medições, o banco de dados precisa saber quais regiões e sensores existem. Acesse a documentação interativa (Swagger UI) e utilize os seguintes endpoints:

1. Expanda a rota **`POST /regions/`** e clique em "Try it out".
2. Insira o JSON com o nome da região (ex: `{"name": "Zona Norte"}`) e clique em "Execute". **Anote o `id` retornado na resposta.**
3. Expanda a rota **`POST /sensors/`** e clique em "Try it out".
4. Cadastre um sensor vinculando-o à região criada (ex: `{"sensor_code": "A1", "region_id": 1}`) e clique em "Execute".

### 5. Simule o Envio de Dados
Para ver o dashboard reagindo aos dados, abra um **novo terminal** (mantenha o servidor Uvicorn rodando no primeiro) e rode o script de simulação que envia medições de temperatura e umidade continuamente para a API:

```bash
python mock_sensor.py
