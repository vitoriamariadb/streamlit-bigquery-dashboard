import streamlit as st
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


class MetricCard:
    """Representacao de um cartao de metrica para o dashboard."""

    def __init__(
        self,
        label: str,
        value: str | float,
        delta: Optional[float] = None,
        delta_color: str = "normal",
        help_text: Optional[str] = None,
    ):
        self.label: str = label
        self.value: str | float = value
        self.delta: Optional[float] = delta
        self.delta_color: str = delta_color
        self.help_text: Optional[str] = help_text


def render_metric_card(col: st.delta_generator.DeltaGenerator, card: MetricCard) -> None:
    delta_str = None
    if card.delta is not None:
        delta_str = f"{card.delta:+.2f}"

    col.metric(
        label=card.label,
        value=card.value,
        delta=delta_str,
        delta_color=card.delta_color,
        help=card.help_text,
    )


def render_metric_row(cards: list[MetricCard]) -> None:
    if not cards:
        return

    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        render_metric_card(col, card)

    logger.debug("Renderizados %d cartoes de metrica", len(cards))


def render_summary_metrics(data: dict[str, float]) -> None:
    cards = []
    for label, value in data.items():
        cards.append(MetricCard(label=label, value=f"{value:,.1f}"))

    render_metric_row(cards)


def render_comparison_metrics(
    current: dict[str, float],
    previous: dict[str, float],
) -> None:
    cards = []
    for label in current:
        cur_val = current[label]
        prev_val = previous.get(label)
        delta = (cur_val - prev_val) if prev_val is not None else None

        cards.append(
            MetricCard(
                label=label,
                value=f"{cur_val:,.1f}",
                delta=delta,
                delta_color="normal",
            )
        )

    render_metric_row(cards)
    logger.info("Metricas comparativas renderizadas: %d indicadores", len(cards))
