import { Centrifuge } from 'centrifuge';
import WebSocket from 'ws';
import readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function getToken() {
    return new Promise((resolve) => {
        rl.question("", (answer) => {
            resolve(answer);
            rl.close();
        });
    });
}

async function main() {
    try {
        const token = await getToken();

        if (!token) {
            console.error('❌ Токен не был введен.');
            return;
        }

        const centrifuge = new Centrifuge("wss://ws.lis-skins.com/connection/websocket", {
            websocket: WebSocket,
            getToken: async () => token,
        });

        centrifuge.on('connect', ctx => {
            console.log('✅ Connected:', ctx);
        });

        centrifuge.on('disconnect', ctx => {
            console.error('❌ Disconnected:', ctx);
        });

        const sub = centrifuge.newSubscription("public:obtained-skins");

        sub.on('publication', function (ctx) {
            process.stdout.write(JSON.stringify(ctx.data) + '\n');
        });

        sub.subscribe();
        centrifuge.connect();

    } catch (error) {
        console.error("❌ Ошибка при подключении:", error);
    }
}

main();
