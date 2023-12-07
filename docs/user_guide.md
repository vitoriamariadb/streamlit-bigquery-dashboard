# Guia do Usuario - Panorama da Educacao Basica

## Visao Geral

O Panorama da Educacao Basica e um dashboard interativo para analise de indicadores
educacionais brasileiros. A ferramenta consolida dados do INEP, IDEB e outros
indicadores em visualizacoes intuitivas.

## Requisitos

- Navegador web moderno (Chrome, Firefox, Edge)
- Acesso a rede interna (para conexao BigQuery)
- Credenciais de acesso fornecidas pelo administrador

## Primeiros Passos

### 1. Acessando o Dashboard

Acesse o dashboard pelo endereco fornecido pelo administrador do sistema.
A pagina inicial exibe um resumo dos principais indicadores.

### 2. Navegacao

Utilize o menu lateral esquerdo para navegar entre as paginas:

- **Inicio**: Visao geral com metricas consolidadas
- **KPIs**: Indicadores chave de performance educacional
- **Tendencias**: Evolucao temporal dos indicadores
- **Segmentacao**: Comparativos entre regioes, estados e redes de ensino

### 3. Filtros

Os filtros permitem refinar a analise por:

- **Regiao**: Norte, Nordeste, Centro-Oeste, Sudeste, Sul
- **Estado**: Todos os 27 UFs
- **Dependencia Administrativa**: Federal, Estadual, Municipal, Privada
- **Etapa de Ensino**: Educacao Infantil, Fundamental, Medio
- **Periodo**: Selecao de intervalo de anos

### 4. Exportacao de Dados

Para exportar os dados exibidos:

1. Navegue ate a pagina desejada
2. Aplique os filtros necessarios
3. Clique no botao "Baixar CSV" abaixo da tabela

## Indicadores Disponiveis

| Indicador | Descricao | Fonte |
|-----------|-----------|-------|
| Taxa de Aprovacao | Percentual de aprovados no ano | INEP |
| Taxa de Reprovacao | Percentual de reprovados no ano | INEP |
| Taxa de Abandono | Percentual de abandonos | INEP |
| IDEB | Indice de Desenvolvimento | INEP |
| Matriculas | Total de matriculas | Censo Escolar |

## Solucao de Problemas

### Dados nao carregam
- Verifique a conexao de rede
- Aguarde alguns segundos e tente novamente
- Contate o administrador se o problema persistir

### Graficos nao aparecem
- Certifique-se de que ha dados para o filtro selecionado
- Tente reduzir o intervalo de datas

### Exportacao falha
- Verifique se ha dados na tabela antes de exportar
- Tente com um filtro menos restritivo

## Contato

Para suporte tecnico, entre em contato com a equipe de dados.
