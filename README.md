# Panorama da Educacao Basica

Dashboard interativo para analise de dados educacionais, construido com Streamlit e integrado ao BigQuery.

## Visao Geral

O Panorama da Educacao Basica consolida indicadores educacionais de diversas fontes,
permitindo analise visual, projecoes, deteccao de anomalias e exportacao de relatorios.

## Stack Tecnologica

- Python 3.10+
- Streamlit >= 1.28
- Google BigQuery >= 3.12
- Pandas >= 2.1
- Plotly >= 5.18
- NumPy >= 1.25

## Estrutura do Projeto

```
src/
  config.py             - Configuracoes e logging
  core/
    bigquery_client.py   - Conexao BigQuery
    query_builder.py     - Construtor de queries
    cache_manager.py     - Cache em memoria
    csv_processor.py     - Processamento CSV
    performance.py       - Otimizacao de performance
    lazy_loader.py       - Carregamento preguicoso
    query_history.py     - Historico de queries
    saved_queries.py     - Queries salvas
  pages/
    kpis.py              - Indicadores chave
    trends.py            - Tendencias temporais
    segmentation.py      - Segmentacao comparativa
    cohort.py            - Analise de coorte
    funnel.py            - Funil educacional
    retention.py         - Retencao e evasao
  components/
    sidebar.py           - Navegacao lateral
    filters.py           - Filtros dinamicos
    date_picker.py       - Seletor de datas
    charts.py            - Graficos Plotly
    metrics_cards.py     - Cartoes de metrica
    tables.py            - Tabelas paginadas
    sql_editor.py        - Editor SQL
    theme.py             - Temas customizaveis
  exporters/
    csv_exporter.py      - Exportacao CSV
    excel_exporter.py    - Exportacao Excel
    pdf_exporter.py      - Exportacao PDF
  analytics/
    forecasting.py       - Projecoes
    anomaly_detection.py - Deteccao de anomalias
    benchmarks.py        - Benchmarks e metas
    data_quality.py      - Qualidade de dados
    data_lineage.py      - Linhagem de dados
    alerts.py            - Sistema de alertas
    scheduler.py         - Relatorios agendados
    period_comparison.py - Comparacao de periodos
  auth/
    authenticator.py     - Autenticacao basica
  collaboration/
    comments.py          - Comentarios
    annotations.py       - Anotacoes em graficos
app.py                   - Ponto de entrada
tests/                   - Testes automatizados
docs/                    - Documentacao
```

## Instalacao

```bash
pip install -r requirements.txt
```

## Execucao

```bash
streamlit run app.py
```

## Docker

```bash
docker compose up --build
```

## Testes

```bash
pytest tests/ -v
```

## Documentacao

- [Guia do Usuario](docs/user_guide.md)
- [Documentacao de Features](docs/features.md)

## Changelog

### v2.0.0 (2024-06-25)
- Analise de coorte, funil e retencao
- Projecoes e deteccao de anomalias
- Benchmarks com metas nacionais
- Verificacao de qualidade de dados
- Editor SQL com validacao
- Queries salvas e historico
- Exportacao Excel e PDF
- Temas customizaveis
- Sistema de alertas e relatorios agendados
- Colaboracao com comentarios e anotacoes
- Otimizacoes de performance e lazy loading

### v1.0.0 (2023-12-28)
- Dashboard base com KPIs, tendencias e segmentacao
- Conexao BigQuery com cache
- Filtros dinamicos e seletor de datas
- Graficos Plotly e tabelas paginadas
- Exportacao CSV
- Autenticacao basica
- Containerizacao Docker

## Licenca

GPL-3.0-or-later
