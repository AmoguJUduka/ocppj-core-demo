from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Transaction:
    transaction_id: int
    id_tag: str
    connector_id: int
    meter_start: int
    start_time: datetime
    meter_stop: Optional[int] = None
    stop_time: Optional[datetime] = None


class Store:
    def __init__(self):
        self.next_tx_id = 1
        self.transactions: Dict[int, Transaction] = {}
        self.allowed_tags = {"ABC123"}

    def start_tx(self, id_tag, connector_id, meter_start, start_time):
        tx_id = self.next_tx_id
        self.next_tx_id += 1
        self.transactions[tx_id] = Transaction(
            tx_id, id_tag, connector_id, meter_start, start_time
        )
        return tx_id

    def stop_tx(self, tx_id, meter_stop, stop_time):
        tx = self.transactions.get(tx_id)
        if tx:
            tx.meter_stop = meter_stop
            tx.stop_time = stop_time

