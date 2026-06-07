import { inject } from '@vercel/analytics';
import { injectSpeedInsights } from '@vercel/speed-insights';

try {
    const host = window.location.hostname;
    const isLocalHost = host === 'localhost' || host === '127.0.0.1' || host === '::1';

    if (!isLocalHost) {
        inject();
        injectSpeedInsights();
    }
} catch (error) {
    console.warn('[rectg] analytics/speed-insights init failed:', error);
}
