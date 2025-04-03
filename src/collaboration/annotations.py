import streamlit as st
import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Annotation:
    """Anotacao em um grafico ou visualizacao do dashboard."""

    author: str
    text: str
    chart_id: str
    x_value: Optional[str] = None
    y_value: Optional[float] = None
    annotation_type: str = "nota"
    color: str = "#3498db"
    visible: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    annotation_id: str = ""

    def __post_init__(self):
        if not self.annotation_id:
            timestamp = self.created_at.strftime("%Y%m%d%H%M%S%f")
            self.annotation_id = f"ann_{timestamp}"


ANNOTATION_TYPES: dict[str, dict] = {
    "nota": {"cor": "#3498db", "icone": "N"},
    "alerta": {"cor": "#e74c3c", "icone": "A"},
    "meta": {"cor": "#2ecc71", "icone": "M"},
    "observacao": {"cor": "#f39c12", "icone": "O"},
}


class AnnotationManager:
    """Gerenciador de anotacoes em visualizacoes."""

    def __init__(self):
        self._annotations: dict[str, Annotation] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add_annotation(self, annotation: Annotation) -> str:
        self._annotations[annotation.annotation_id] = annotation
        self.logger.info(
            "Anotacao adicionada por %s em %s", annotation.author, annotation.chart_id
        )
        return annotation.annotation_id

    def get_annotations(self, chart_id: str) -> list[Annotation]:
        annotations = [
            a for a in self._annotations.values()
            if a.chart_id == chart_id and a.visible
        ]
        return sorted(annotations, key=lambda a: a.created_at)

    def update_annotation(self, annotation_id: str, text: str) -> bool:
        ann = self._annotations.get(annotation_id)
        if ann:
            ann.text = text
            self.logger.info("Anotacao atualizada: %s", annotation_id)
            return True
        return False

    def delete_annotation(self, annotation_id: str) -> bool:
        if annotation_id in self._annotations:
            del self._annotations[annotation_id]
            self.logger.info("Anotacao removida: %s", annotation_id)
            return True
        return False

    def toggle_visibility(self, annotation_id: str) -> bool:
        ann = self._annotations.get(annotation_id)
        if ann:
            ann.visible = not ann.visible
            return True
        return False

    def get_by_author(self, author: str) -> list[Annotation]:
        return [a for a in self._annotations.values() if a.author == author]

    @property
    def total_annotations(self) -> int:
        return len(self._annotations)


def render_annotation_form(chart_id: str) -> Optional[Annotation]:
    with st.expander("Adicionar anotacao"):
        ann_type: str = st.selectbox(
            "Tipo",
            options=list(ANNOTATION_TYPES.keys()),
            key=f"ann_type_{chart_id}",
        )

        text: str = st.text_area(
            "Texto da anotacao",
            key=f"ann_text_{chart_id}",
            max_chars=500,
        )

        x_ref: str = st.text_input(
            "Referencia X (ex: 2023)",
            key=f"ann_xref_{chart_id}",
        )

        if st.button("Salvar anotacao", key=f"ann_save_{chart_id}"):
            if text:
                author = st.session_state.get("username", "anonimo")
                annotation = Annotation(
                    author=author,
                    text=text,
                    chart_id=chart_id,
                    x_value=x_ref if x_ref else None,
                    annotation_type=ann_type,
                    color=ANNOTATION_TYPES[ann_type]["cor"],
                )
                st.success("Anotacao salva")
                return annotation
            else:
                st.warning("Texto da anotacao e obrigatorio")

    return None
