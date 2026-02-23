Dashboard interativo para análise de dados educacionais, construído com Streamlit e integrado ao BigQuery.

```
src/
  config.py             - Configurações e logging
  core/
    bigquery_client.py   - Conexão BigQuery
    query_builder.py     - Construtor de queries
    cache_manager.py     - Cache em memória
    csv_processor.py     - Processamento CSV
    performance.py       - Otimização de performance
    lazy_loader.py       - Carregamento preguiçoso
    query_history.py     - Histórico de queries
    saved_queries.py     - Queries salvas
  pages/
    kpis.py              - Indicadores chave
    trends.py            - Tendências temporais
    segmentation.py      - Segmentação comparativa
    cohort.py            - Análise de coorte
    funnel.py            - Funil educacional
    retention.py         - Retenção e evasão
  components/
    sidebar.py           - Navegação lateral
    filters.py           - Filtros dinâmicos
    date_picker.py       - Seletor de datas
    charts.py            - Gráficos Plotly
    metrics_cards.py     - Cartões de métrica
    tables.py            - Tabelas paginadas
    sql_editor.py        - Editor SQL
    theme.py             - Temas customizáveis
  exporters/
    csv_exporter.py      - Exportação CSV
    excel_exporter.py    - Exportação Excel
    pdf_exporter.py      - Exportação PDF
  analytics/
    forecasting.py       - Projeções
    anomaly_detection.py - Detecção de anomalias
    benchmarks.py        - Benchmarks e metas
    data_quality.py      - Qualidade de dados
    data_lineage.py      - Linhagem de dados
    alerts.py            - Sistema de alertas
    scheduler.py         - Relatórios agendados
    period_comparison.py - Comparação de períodos
  auth/
    authenticator.py     - Autenticação básica
  collaboration/
    comments.py          - Comentários
    annotations.py       - Anotações em gráficos
app.py                   - Ponto de entrada
tests/                   - Testes automatizados
docs/                    - Documentação
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

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

## Documentação

- [Guia do Usuário](docs/user_guide.md)
- [Documentação de Features](docs/features.md)

## Changelog

### v2.0.0 (2024-06-25)
- Análise de coorte, funil e retenção
- Projeções e detecção de anomalias
- Benchmarks com metas nacionais
- Verificação de qualidade de dados
- Editor SQL com validação
- Queries salvas e histórico
- Exportação Excel e PDF
- Temas customizáveis
- Sistema de alertas e relatórios agendados
- Colaboração com comentários e anotações
- Otimizações de performance e lazy loading

### v1.0.0 (2023-12-28)
- Dashboard base com KPIs, tendências e segmentação
- Conexão BigQuery com cache
- Filtros dinâmicos e seletor de datas
- Gráficos Plotly e tabelas paginadas
- Exportação CSV
- Autenticação básica
- Containerização Docker

## Licença

GPL-3.0-or-later
