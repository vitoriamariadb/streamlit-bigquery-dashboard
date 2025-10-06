import logging
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Representacao de um alerta do sistema."""

    level: str
    title: str
    message: str
    metric: str
    threshold: float
    current_value: float
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

    @property
    def is_critical(self) -> bool:
        return self.level == "critico"

    @property
    def deviation(self) -> float:
        if self.threshold == 0:
            return 0.0
        return round(
            ((self.current_value - self.threshold) / self.threshold) * 100, 2
        )


class AlertRule:
    """Regra para geracao automatica de alertas."""

    def __init__(
        self,
        metric: str,
        condition: str,
        threshold: float,
        level: str = "aviso",
        message_template: str = "",
    ):
        self.metric: str = metric
        self.condition: str = condition
        self.threshold: float = threshold
        self.level: str = level
        self.message_template: str = message_template

    def evaluate(self, value: float) -> Optional[Alert]:
        triggered = False

        if self.condition == "abaixo" and value < self.threshold:
            triggered = True
        elif self.condition == "acima" and value > self.threshold:
            triggered = True
        elif self.condition == "igual" and value == self.threshold:
            triggered = True

        if triggered:
            message = self.message_template.format(
                metric=self.metric,
                value=value,
                threshold=self.threshold,
            )
            return Alert(
                level=self.level,
                title=f"Alerta: {self.metric}",
                message=message or f"{self.metric} = {value} ({self.condition} de {self.threshold})",
                metric=self.metric,
                threshold=self.threshold,
                current_value=value,
            )
        return None


class AlertManager:
    """Gerenciador centralizado de alertas."""

    def __init__(self):
        self.rules: list[AlertRule] = []
        self.active_alerts: list[Alert] = []
        self.history: list[Alert] = []
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add_rule(self, rule: AlertRule) -> None:
        self.rules.append(rule)
        self.logger.info("Regra adicionada: %s %s %s", rule.metric, rule.condition, rule.threshold)

    def evaluate_all(self, metrics: dict[str, float]) -> list[Alert]:
        new_alerts: list[Alert] = []
        for rule in self.rules:
            value = metrics.get(rule.metric)
            if value is not None:
                alert = rule.evaluate(value)
                if alert:
                    new_alerts.append(alert)
                    self.active_alerts.append(alert)
                    self.logger.warning(
                        "Alerta disparado: %s (valor: %s, limiar: %s)",
                        alert.title, alert.current_value, alert.threshold,
                    )
        return new_alerts

    def acknowledge(self, alert: Alert) -> None:
        alert.acknowledged = True
        self.history.append(alert)
        if alert in self.active_alerts:
            self.active_alerts.remove(alert)

    def get_active_count(self) -> dict[str, int]:
        counts = {"critico": 0, "aviso": 0, "info": 0}
        for alert in self.active_alerts:
            if alert.level in counts:
                counts[alert.level] += 1
        return counts

    def setup_default_rules(self) -> None:
        default_rules = [
            AlertRule("taxa_aprovacao", "abaixo", 85.0, "critico",
                      "Taxa de aprovacao em {value:.1f}% (limiar: {threshold:.1f}%)"),
            AlertRule("taxa_abandono", "acima", 5.0, "aviso",
                      "Taxa de abandono em {value:.1f}% (limiar: {threshold:.1f}%)"),
            AlertRule("ideb", "abaixo", 4.0, "critico",
                      "IDEB em {value:.1f} (limiar: {threshold:.1f})"),
        ]
        for rule in default_rules:
            self.add_rule(rule)
