# Documentacao de Features - Panorama da Educacao Basica v2.0

## Paginas do Dashboard

### KPIs
Visao consolidada dos indicadores chave: taxa de aprovacao, reprovacao, abandono e IDEB.
Exibe valores atuais com deltas em relacao ao periodo anterior e progresso em relacao as metas.

### Tendencias
Evolucao temporal dos indicadores com selecao de metricas e granularidade.
Suporta comparacao de multiplos indicadores no mesmo grafico.

### Segmentacao
Analise comparativa entre segmentos: regiao, UF, dependencia administrativa,
localizacao e etapa de ensino. Exibe estatisticas descritivas e graficos de barras.

### Analise de Coorte
Acompanhamento de grupos de alunos ao longo do tempo.
Gera matriz de retencao colorida para identificar padroes de evasao.

### Funil Educacional
Visualizacao do fluxo de alunos desde a matricula ate a conclusao.
Calcula taxas de conversao entre cada etapa do funil.

### Retencao e Evasao
Analise detalhada das taxas de retencao e evasao com tres modos de visualizacao:
serie temporal, comparativo regional e detalhamento tabular.

## Componentes

### Filtros Dinamicos
Sistema de filtros hierarquicos (regiao -> estado) com suporte a multipla selecao.
Filtros por dependencia administrativa e etapa de ensino.

### Seletor de Datas
Suporte a presets (ultimo ano, 3, 5, 10 anos) e selecao personalizada.
Seletor de ano com validacao de intervalo.

### Editor SQL
Editor integrado com templates pre-definidos, validacao de seguranca
(bloqueia DDL/DML), limite de linhas configuravel.

### Graficos Plotly
Biblioteca de graficos reutilizaveis: linha, barra, pizza, heatmap.
Paleta de cores consistente e template padronizado.

### Tabelas Paginadas
Exibicao tabular com paginacao, busca textual, formatacao numerica automatica
e tabelas pivot.

### Cartoes de Metrica
Componente reutilizavel para exibicao de KPIs com delta e barra de progresso.

## Analytics

### Projecoes (Forecasting)
Projecao linear e media movel com R-quadrado para avaliacao da qualidade do modelo.
Visualizacao combinada de dados historicos e projecao.

### Deteccao de Anomalias
Tres metodos complementares: Z-Score, IQR e variacao subita.
Classificacao de severidade e descricao contextualizada.

### Benchmarks
Comparacao com metas do PNE, media nacional e top 10%.
Visualizacao em gauge com faixas coloridas.

### Qualidade de Dados
Verificacoes automaticas de completude, duplicatas, intervalos validos
e atualidade dos dados. Pontuacao geral de qualidade.

### Comparacao de Periodos
Comparacao lado a lado entre dois periodos com variacao absoluta e percentual.
Grafico de barras agrupadas para visualizacao.

### Linhagem de Dados
Rastreabilidade das fontes de dados (Censo Escolar, IDEB, PNAD) e
transformacoes aplicadas ate a visualizacao no dashboard.

## Infraestrutura

### Alertas
Sistema de alertas com regras configuraveis, niveis de severidade
(critico, aviso, info) e reconhecimento de alertas.

### Relatorios Agendados
Agendamento de relatorios automaticos com frequencia configuravel
(diario, semanal, mensal, trimestral).

### Exportacao
Suporte a exportacao em CSV, Excel (multiplas abas com formatacao)
e PDF (com tabelas formatadas).

### Queries Salvas
Persistencia de queries frequentes com categorias, tags e busca.

### Historico de Queries
Registro automatico de queries executadas com metricas de performance.

### Performance
Cache em multiplas camadas (memoria e Streamlit), otimizacao de tipos de dados,
lazy loading de secoes do dashboard e monitoramento de performance.

### Autenticacao
Login basico com hash SHA-256 e gerenciamento via Streamlit Secrets.

### Colaboracao
Sistema de comentarios em elementos do dashboard e anotacoes em graficos
com tipos diferenciados (nota, alerta, meta, observacao).

## Stack Tecnologica

| Componente | Tecnologia | Versao |
|------------|-----------|--------|
| Frontend | Streamlit | >= 1.28 |
| Graficos | Plotly | >= 5.18 |
| Dados | Pandas | >= 2.1 |
| Data Lake | BigQuery | >= 3.12 |
| Autenticacao | google-auth | >= 2.23 |
| Excel | xlsxwriter | >= 3.1 |
| Container | Docker | 3.8 |
