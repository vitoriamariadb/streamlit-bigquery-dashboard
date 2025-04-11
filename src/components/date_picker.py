import streamlit as st
import logging
from datetime import date, timedelta
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

PRESETS: dict[str, dict] = {
    "Ultimo Ano": {"days": 365},
    "Ultimos 3 Anos": {"days": 1095},
    "Ultimos 5 Anos": {"days": 1825},
    "Ultimos 10 Anos": {"days": 3650},
    "Personalizado": {"days": 0},
}


class DateRange:
    """Representa um intervalo de datas selecionado."""

    def __init__(self, start: date, end: date):
        self.start: date = start
        self.end: date = end

    @property
    def days(self) -> int:
        return (self.end - self.start).days

    @property
    def years(self) -> float:
        return round(self.days / 365.25, 1)

    def to_dict(self) -> dict:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days": self.days,
        }


def render_date_picker(
    min_date: date = date(2005, 1, 1),
    max_date: Optional[date] = None,
) -> DateRange:
    if max_date is None:
        max_date = date.today()

    preset: str = st.selectbox(
        "Periodo",
        options=list(PRESETS.keys()),
        index=2,
        key="date_preset",
    )

    if preset == "Personalizado":
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input(
                "Data inicial",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="date_start",
            )
        with col2:
            end = st.date_input(
                "Data final",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="date_end",
            )
    else:
        days = PRESETS[preset]["days"]
        end = max_date
        start = max_date - timedelta(days=days)
        if start < min_date:
            start = min_date
        st.caption(f"Periodo: {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}")

    date_range = DateRange(start, end)
    logger.info("Periodo selecionado: %s", date_range.to_dict())
    return date_range


def render_year_selector(
    min_year: int = 2005,
    max_year: Optional[int] = None,
) -> tuple[int, int]:
    if max_year is None:
        max_year = date.today().year

    years = list(range(min_year, max_year + 1))

    col1, col2 = st.columns(2)
    with col1:
        start_year: int = st.selectbox(
            "Ano inicial",
            options=years,
            index=0,
            key="year_start",
        )
    with col2:
        end_year: int = st.selectbox(
            "Ano final",
            options=[y for y in years if y >= start_year],
            index=len([y for y in years if y >= start_year]) - 1,
            key="year_end",
        )

    logger.info("Anos selecionados: %d - %d", start_year, end_year)
    return start_year, end_year
