import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { spawn } from "node:child_process";
import { appendFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";

const STATUS_KEY = "azure-ai-cost";
const REFRESH_MS = 15 * 60 * 1000;
const SCRIPT_PATH = resolve(__dirname, "azure_openai_cost_query.py");

// Logging
const LOG_DIR = resolve(process.env.HOME ?? "~", ".pi", "logs");
const LOG_FILE = resolve(LOG_DIR, "azure-ai-cost.log");

const logLine = (line: string) => {
	try {
		mkdirSync(LOG_DIR, { recursive: true });
		appendFileSync(LOG_FILE, `${new Date().toISOString()} ${line}\n`, { encoding: "utf8" });
	} catch {
		// If we can't write to /var/log (permissions), don't crash the extension.
	}
};

const isoDate = (d: Date) => d.toISOString().slice(0, 10);

const last7DaysRange = () => {
	const now = new Date();
	const to = isoDate(now);
	const fromDate = new Date(now);
	fromDate.setDate(now.getDate() - 6); // inclusive 7 days
	const from = isoDate(fromDate);
	return { from, to };
};

const runCostScript = async (ctx: ExtensionContext): Promise<void> => {
	logLine("update: start");
	const subscriptionId = process.env.AZURE_SUBSCRIPTION_ID;
	if (!subscriptionId) {
		ctx.ui.setStatus(STATUS_KEY, "AOAI7d: missing AZURE_SUBSCRIPTION_ID");
		logLine("update: missing AZURE_SUBSCRIPTION_ID");
		return;
	}

	const { from, to } = last7DaysRange();

	const args = [
		SCRIPT_PATH,
		"--subscription-id",
		subscriptionId,
		"--resource-group",
		process.env.AZURE_AOAI_RESOURCE_GROUP ?? "rg-pi-openai-test",
		"--account-name",
		process.env.AZURE_AOAI_ACCOUNT_NAME ?? "pi-openai-test-1",
		"--from",
		from,
		"--to",
		to,
	];

	ctx.ui.setStatus(STATUS_KEY, "AOAI7d: updating...");
	logLine(`cmd: python ${args.map((a) => JSON.stringify(a)).join(" ")}`);

	const proc = spawn("python", args, {
		timeout: 60_000,
		env: process.env,
	});

	let stdout = "";
	let stderr = "";

	proc.stdout.on("data", (d) => {
		stdout += d.toString("utf8");
	});
	proc.stderr.on("data", (d) => {
		stderr += d.toString("utf8");
	});

	const exitCode: number = await new Promise((resolveCode) => {
		const timeout = setTimeout(() => {
			logLine("update: timeout after 60s");
			try {
				proc.kill();
			} catch {
				// ignore
			}
			resolveCode(124);
		}, 60_000);
		proc.on("close", (code) => {
			clearTimeout(timeout);
			resolveCode(code ?? 0);
		});
		proc.on("error", () => {
			clearTimeout(timeout);
			resolveCode(1);
		});
	});

	// Note: we already handled close/error above to resolve.
	// Keep the old handlers removed.

	if (exitCode !== 0) {
		const combined = (stderr || stdout).trim();
		const msg = combined.split("\n").slice(-1)[0] || `exit ${exitCode}`;
		ctx.ui.setStatus(STATUS_KEY, `AOAI7d: ERR`);
		logLine(`update: fail exit=${exitCode}`);
		if (stdout.trim()) logLine(`stdout: ${stdout.trim().slice(0, 2000)}`);
		if (stderr.trim()) logLine(`stderr: ${stderr.trim().slice(0, 2000)}`);
		if (ctx.hasUI) ctx.ui.notify(`Azure cost update failed: ${msg}`, "warning");
		return;
	}

	const raw = stdout.trim();
	const value = Number(raw);
	if (!Number.isFinite(value)) {
		ctx.ui.setStatus(STATUS_KEY, "AOAI7d: ERR");
		logLine("update: non-numeric output");
		if (stdout.trim()) logLine(`stdout: ${stdout.trim().slice(0, 2000)}`);
		if (stderr.trim()) logLine(`stderr: ${stderr.trim().slice(0, 2000)}`);
		if (ctx.hasUI) ctx.ui.notify(`Azure cost update returned non-number: ${raw}`, "warning");
		return;
	}

	ctx.ui.setStatus(STATUS_KEY, `AOAI7d: $${value.toFixed(2)}`);
	logLine(`update: ok value=${value}`);
};

export default function (pi: ExtensionAPI) {
	let interval: NodeJS.Timeout | undefined;

	const schedule = (ctx: ExtensionContext) => {
		// Run at startup
		void runCostScript(ctx);

		// Then periodically
		interval = setInterval(() => void runCostScript(ctx), REFRESH_MS);
	};

	pi.on("session_start", async (_event, ctx) => {
		// Only schedule once.
		if (!interval) schedule(ctx);
	});

	pi.on("session_shutdown", async () => {
		if (interval) clearInterval(interval);
		interval = undefined;
	});

	pi.registerCommand("update-azure-cost", {
		description: "Force refresh Azure OpenAI cost in the status bar (last 7 days)",
		handler: async (_args, ctx) => {
			await runCostScript(ctx);
		},
	});
}
