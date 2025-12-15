import asyncio
from datetime import datetime, timezone

import websockets
from ocpp.v16 import ChargePoint
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus


class VirtualCP(ChargePoint):

    async def run(self):
        # Boot
        boot = await self.call(
            call.BootNotification(
                charge_point_vendor="DemoVendor",
                charge_point_model="VirtualCP",
            )
        )
        print("[CP] Boot:", boot.status)

        if boot.status != RegistrationStatus.accepted:
            return

        # Heartbeat loop
        asyncio.create_task(self.heartbeat_loop(boot.interval))

        # Authorize
        auth = await self.call(call.Authorize(id_tag="ABC123"))
        print("[CP] Authorize:", auth.id_tag_info)

        # Start transaction
        start = await self.call(
            call.StartTransaction(
                connector_id=1,
                id_tag="ABC123",
                meter_start=1000,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            )
        )
        print("[CP] Start tx:", start.transaction_id)

        await asyncio.sleep(5)

        # Stop transaction
        await self.call(
            call.StopTransaction(
                transaction_id=start.transaction_id,
                meter_stop=1050,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            )
        )
        print("[CP] Stop tx")

    async def heartbeat_loop(self, interval):
        while True:
            await self.call(call.Heartbeat())
            await asyncio.sleep(interval)


async def main():
    async with websockets.connect(
        "ws://localhost:9000/CP_1",
        subprotocols=["ocpp1.6"],
    ) as ws:
        cp = VirtualCP("CP_1", ws)
        await asyncio.gather(cp.start(), cp.run())


if __name__ == "__main__":
    asyncio.run(main())

