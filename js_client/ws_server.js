import WebSocket, { WebSocketServer } from 'ws';
import { Centrifuge } from 'centrifuge';
import fetch from 'node-fetch';

const wss = new WebSocketServer({ port: 8080 });

async function fetchWsToken(lisToken) {
    const res = await fetch('https://api.lis-skins.com/v1/user/get-ws-token', {
        headers: {
            Authorization: 'Bearer ' + lisToken,
        },
    });

    if (!res.ok) {
        throw new Error(`Ошибка получения ws_token: ${res.status}`);
    }

    const json = await res.json();
    return json.data.token;
}

// test
wss.on('connection', (ws) => {
    let centrifuge = null;
    let subscription = null;
    let refreshTimer = null;
    let lisToken = null;

    async function startCentrifuge(token) {
        centrifuge = new Centrifuge("wss://ws.lis-skins.com/connection/websocket", {
            websocket: WebSocket,
            getToken: async () => token,
        });

        centrifuge.on('connect', ctx => {
            console.log("✅ Connected:", ctx);
        });

        centrifuge.on('disconnect', ctx => {
            console.error("❌ Disconnected:", ctx);
        });

        centrifuge.on('error', err => {
            console.error("❌ Centrifuge error:", err);
        });

        subscription = centrifuge.newSubscription("public:obtained-skins");

        subscription.on('publication', (ctx) => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'event',
                    data: ctx.data
                }));
            }
        });

        subscription.subscribe();
        centrifuge.connect();

        refreshTimer = setTimeout(async () => {
            console.log(`[${new Date().toISOString()}] 🔄 Обновление ws_token и переподключение...`);
            try {
                if (subscription) subscription.unsubscribe();
                if (centrifuge) centrifuge.disconnect();

                const newToken = await fetchWsToken(lisToken);
                await startCentrifuge(newToken);
            } catch (e) {
                console.error("❌ Ошибка при обновлении ws_token:", e);
                ws.close();
            }
        }, 9 * 60 * 1000);
    }

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message.toString());

            if (data.type === 'start' && data.lis_token) {
                lisToken = data.lis_token;

                const wsToken = await fetchWsToken(lisToken);
                await startCentrifuge(wsToken);
            }

            if (data.type === 'stop') {
                if (refreshTimer) clearTimeout(refreshTimer);
                if (subscription) subscription.unsubscribe();
                if (centrifuge) centrifuge.disconnect();
                ws.close();
            }
        } catch (e) {
            console.error("❌ Ошибка обработки сообщения:", e);
        }
    });

    ws.on('close', () => {
        if (refreshTimer) clearTimeout(refreshTimer);
        if (subscription) subscription.unsubscribe();
        if (centrifuge) centrifuge.disconnect();
        console.log("❎ Client disconnected");
    });

    ws.on('error', (err) => {
        console.error("⚠️ Ошибка WebSocket:", err);
    });
});

console.log("🟢 WebSocket сервер слушает на порту 8080");
