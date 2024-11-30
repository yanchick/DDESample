import { sveltekit } from "@sveltejs/kit/vite"
	import { createLogger } from 'vite';
	import { sourceQueryHmr, configVirtual, queryDirectoryHmr } from '@evidence-dev/sdk/build/vite';
	import { isDebug } from '@evidence-dev/sdk/utils';
	import { log } from "@evidence-dev/sdk/logger";

	const logger = createLogger();

    const strictFs = (process.env.NODE_ENV === 'development') ? false : true;
    /** @type {import('vite').UserConfig} */
     const config = 
    {
        plugins: [sveltekit(), configVirtual(), queryDirectoryHmr, sourceQueryHmr()],
        optimizeDeps: {
            include: ['echarts-stat', 'echarts', 'blueimp-md5', 'nanoid', '@uwdata/mosaic-sql',
				// We need these to prevent HMR from doing a full page reload
				...(process.env.EVIDENCE_DISABLE_INCLUDE ? [] : [
					'@evidence-dev/core-components',
					// Evidence packages injected into process-queries
					'@evidence-dev/component-utilities/stores','@evidence-dev/component-utilities/formatting','@evidence-dev/component-utilities/globalContexts','@evidence-dev/sdk/utils/svelte','@evidence-dev/component-utilities/profile','@evidence-dev/sdk/usql','@evidence-dev/component-utilities/buildQuery',
					'debounce', 
					'@duckdb/duckdb-wasm',
					'apache-arrow'
				])
				
			],
            exclude: ['svelte-icons', '@evidence-dev/universal-sql', '$evidence/config']
        },
        ssr: {
            external: ['@evidence-dev/telemetry', 'blueimp-md5', 'nanoid', '@uwdata/mosaic-sql', '@evidence-dev/sdk/plugins']
        },
        server: {
            fs: {
                strict: strictFs // allow template to get dependencies outside the .evidence folder
            },
			hmr: {
				overlay: false
			}
        },
		build: {
			// 🚩 Triple check this
			minify: isDebug() ? false : true,
			target: isDebug() ? 'esnext' : undefined,
			rollupOptions: {
				external: [/^@evidence-dev\/tailwind\/fonts\//],
				onwarn(warning, warn) {
					if (warning.code === 'EVAL') return;
					warn(warning);
				}
			}
		},
		customLogger: logger
    }

	if (isDebug()) {
		const loggerWarn = logger.warn;
		const loggerOnce = logger.warnOnce

		/**
		 * @see https://github.com/evidence-dev/evidence/issues/1876
		 * Ignore the duckdb-wasm sourcemap warning
		 */
		logger.warnOnce = (m, o) => {
			if (m.match(/Sourcemap for ".+\/node_modules\/@duckdb\/duckdb-wasm\/dist\/duckdb-browser-eh\.worker\.js" points to missing source files/)) return;
			loggerOnce(m, o)
		}

		logger.warn = (msg, options) => {
			// ignore fs/promises warning, used in +layout.js behind if (!browser) check
			if (msg.includes('Module "fs/promises" has been externalized for browser compatibility')) return;

			// ignore eval warning, used in duckdb-wasm
			if (msg.includes('Use of eval in') && msg.includes('is strongly discouraged as it poses security risks and may cause issues with minification.')) return;

			loggerWarn(msg, options);
		};
	} else {
		config.logLevel = 'silent';
		logger.error = (msg) => log.error(msg);
		logger.info = logger.warn = logger.warnOnce = () => {};
	}

    export default config