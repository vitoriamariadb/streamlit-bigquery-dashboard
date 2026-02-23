# Documentação de Features - Painel Educação Básica v2.0

## Páginas do Dashboard

### KPIs
Visão consolidada dos indicadores chave: taxa de aprovação, reprovação, abandono e IDEB.
Exibe valores atuais com deltas em relação ao período anterior e progresso em relação às metas.

### Tendências
Evolução temporal dos indicadores com seleção de métricas e granularidade.
Suporta comparação de múltiplos indicadores no mesmo gráfico.

### Segmentação
Análise comparativa entre segmentos: região, UF, dependência administrativa,
localização e etapa de ensino. Exibe estatísticas descritivas e gráficos de barras.

### Análise de Coorte
Acompanhamento de grupos de alunos ao longo do tempo.
Gera matriz de retenção colorida para identificar padrões de evasão.

### Funil Educacional
Visualização do fluxo de alunos desde a matrícula até a conclusão.
Calcula taxas de conversão entre cada etapa do funil.

### Retenção e Evasão
Análise detalhada das taxas de retenção e evasão com três modos de visualização:
série temporal, comparativo regional e detalhamento tabular.

## Componentes

### Filtros Dinâmicos
Sistema de filtros hierárquicos (região -> estado) com suporte a múltipla seleção.
Filtros por dependência administrativa e etapa de ensino.

### Seletor de Datas
Suporte a presets (último ano, 3, 5, 10 anos) e seleção personalizada.
Seletor de ano com validação de intervalo.

### Editor SQL
Editor integrado com templates pré-definidos, validação de segurança
(bloqueia DDL/DML), limite de linhas configurável.

### Gráficos Plotly
Biblioteca de gráficos reutilizáveis: linha, barra, pizza, heatmap.
Paleta de cores consistente e template padronizado.

### Tabelas Paginadas
Exibição tabular com paginação, busca textual, formatação numérica automática
e tabelas pivot.

### Cartões de Métrica
Componente reutilizável para exibição de KPIs com delta e barra de progresso.

## Analytics

### Projeções (Forecasting)
Projeção linear e média móvel com R-quadrado para avaliação da qualidade do modelo.
Visualização combinada de dados históricos e projeção.

### Detecção de Anomalias
Três métodos complementares: Z-Score, IQR e variação súbita.
Classificação de severidade e descrição contextualizada.

### Benchmarks
Comparação com metas do PNE, média nacional e top 10%.
Visualização em gauge com faixas coloridas.

### Qualidade de Dados
Verificações automáticas de completude, duplicatas, intervalos válidos
e atualidade dos dados. Pontuação geral de qualidade.

### Comparação de Períodos
Comparação lado a lado entre dois períodos com variação absoluta e percentual.
Gráfico de barras agrupadas para visualização.

### Linhagem de Dados
Rastreabilidade das fontes de dados (censo escolar, indicadores, pesquisas) e
transformações aplicadas até a visualização no dashboard.

## Infraestrutura

### Alertas
Sistema de alertas com regras configuráveis, níveis de severidade
(crítico, aviso, info) e reconhecimento de alertas.

### Relatórios Agendados
Agendamento de relatórios automáticos com frequência configurável
(diário, semanal, mensal, trimestral).

### Exportação
Suporte a exportação em CSV, Excel (múltiplas abas com formatação)
e PDF (com tabelas formatadas).

### Queries Salvas
Persistência de queries frequentes com categorias, tags e busca.

### Histórico de Queries
Registro automático de queries executadas com métricas de performance.

### Performance
Cache em múltiplas camadas (memória e Streamlit), otimização de tipos de dados,
lazy loading de seções do dashboard e monitoramento de performance.

### Autenticação
Login básico com hash SHA-256 e gerenciamento via Streamlit Secrets.

### Colaboração
Sistema de comentários em elementos do dashboard e anotações em gráficos
com tipos diferenciados (nota, alerta, meta, observação).

## Stack Tecnológica

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Frontend | Streamlit | >= 1.28 |
| Gráficos | Plotly | >= 5.18 |
| Dados | Pandas | >= 2.1 |
| Data Lake | BigQuery | >= 3.12 |
| Autenticação | google-auth | >= 2.23 |
| Excel | xlsxwriter | >= 3.1 |
| Container | Docker | 3.8 |
