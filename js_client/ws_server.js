const WebSocket = require('ws');
const { Centrifuge } = require('centrifuge');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    let centrifuge = null;
    let subscription = null;

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message.toString());

            if (data.type === 'start' && data.token) {
                centrifuge = new Centrifuge("wss://ws.lis-skins.com/connection/websocket", {
                    websocket: WebSocket,
                    getToken: async () => data.token,
                });

                centrifuge.on('connect', ctx => {
                    console.log("✅ Connected:", ctx);
                });

                centrifuge.on('disconnect', ctx => {
                    console.error("❌ Disconnected:", ctx);
                });

                subscription = centrifuge.newSubscription("public:obtained-skins");

                subscription.on('publication', (ctx) => {
                    ws.send(JSON.stringify({
                        type: 'event',
                        data: ctx.data
                    }));
                });

                subscription.subscribe();
                centrifuge.connect();
            }

            if (data.type === 'stop') {
                if (subscription) subscription.unsubscribe();
                if (centrifuge) centrifuge.disconnect();
                ws.close();
            }

        } catch (e) {
            console.error("❌ Error parsing message:", e);
        }
    });

    ws.on('close', () => {
        if (subscription) subscription.unsubscribe();
        if (centrifuge) centrifuge.disconnect();
        console.log("❎ Client disconnected");
    });
});

console.log("🟢 WebSocket сервер слушает на порту 8080");
