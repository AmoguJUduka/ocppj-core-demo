import asyncio
from datetime import datetime, timezone

import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus

from csms.store import Store

store = Store()


class CentralSystem(ChargePoint):

    @on(Action.boot_notification)
    async def boot(self, charge_point_vendor, charge_point_model, **kwargs):
        print(f"[CSMS] Boot from {self.id}")
        return call_result.BootNotification(
            current_time=datetime.now(tz=timezone.utc).isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )

    @on(Action.heartbeat)
    async def heartbeat(self):
        print(f"[CSMS] Heartbeat from {self.id}")
        return call_result.Heartbeat(
            current_time=datetime.now(tz=timezone.utc).isoformat()
        )

    @on(Action.authorize)
    async def authorize(self, id_tag):
        status = (
            AuthorizationStatus.accepted
            if id_tag in store.allowed_tags
            else AuthorizationStatus.invalid
        )
        print(f"[CSMS] Authorize {id_tag} → {status}")
        return call_result.Authorize(id_tag_info={"status": status})

    @on(Action.start_transaction)
    async def start_tx(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        tx_id = store.start_tx(
            id_tag,
            connector_id,
            meter_start,
            datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        )
        print(f"[CSMS] StartTransaction tx={tx_id}")
        return call_result.StartTransaction(
            transaction_id=tx_id,
            id_tag_info={"status": AuthorizationStatus.accepted},
        )

    @on(Action.stop_transaction)
    async def stop_tx(self, transaction_id, meter_stop, timestamp, **kwargs):
        store.stop_tx(
            transaction_id,
            meter_stop,
            datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        )
        print(f"[CSMS] StopTransaction tx={transaction_id}")
        return call_result.StopTransaction(
            id_tag_info={"status": AuthorizationStatus.accepted}
        )


async def on_connect(ws):
    cp_id = ws.request.path.strip("/")
    print(f"[CSMS] Connected {cp_id}")
    await CentralSystem(cp_id, ws).start()


async def main():
    server = await websockets.serve(
        on_connect,
        "localhost",
        9000,
        subprotocols=["ocpp1.6"],
    )
    print("[CSMS] Listening on ws://localhost:9000/<CP_ID>")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())

