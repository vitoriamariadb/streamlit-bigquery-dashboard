# Panorama da Educacao Basica

Dashboard interativo para analise de dados educacionais, construido com Streamlit e integrado ao BigQuery.

## Visao Geral

O Panorama da Educacao Basica consolida indicadores educacionais de diversas fontes,
permitindo analise visual e exportacao de relatorios.

## Stack Tecnologica

- Python 3.10+
- Streamlit
- Google BigQuery
- Pandas
- Plotly

## Estrutura do Projeto

```
src/
  config.py
  core/          - Conexao BigQuery, cache, queries
  pages/         - Paginas do dashboard
  components/    - Componentes reutilizaveis
  exporters/     - Exportadores CSV, Excel, PDF
  analytics/     - Modulos de analise avancada
  auth/          - Autenticacao
  collaboration/ - Funcionalidades colaborativas
app.py           - Ponto de entrada
tests/           - Testes automatizados
docs/            - Documentacao
```

## Instalacao

```bash
pip install -r requirements.txt
```

## Execucao

```bash
streamlit run app.py
```

## Licenca

GPL-3.0-or-later
