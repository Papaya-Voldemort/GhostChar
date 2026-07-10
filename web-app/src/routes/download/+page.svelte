<script lang="ts">
    import { base } from '$app/paths';
    import appIcon from '$lib/assets/ghostchar_app_icon.png';

    let copied = $state(false);

    function copyCommand() {
        navigator.clipboard.writeText('xattr -cr /Applications/GhostChar.app');
        copied = true;
        setTimeout(() => {
            copied = false;
        }, 2000);
    }
</script>

<svelte:head>
    <title>&lt;GhostChar /&gt; // Download Desktop</title>
    <meta name="description" content="Download GhostChar for macOS. Neural network real-time ASCII art webcam utility." />
</svelte:head>

<div class="download-page">
    <div class="page-glow"></div>
    
    <div class="container">
        <header class="download-header">
            <img src={appIcon} alt="GhostChar App Icon" class="app-logo animate-float" />
            <div class="ascii-badge">
                <span class="pulse"></span> macOS Version v0.1.0
            </div>
            <h1>Get GhostChar for Desktop</h1>
            <p class="subtitle">Experience high-fidelity neural ASCII rendering directly on your Mac.</p>
        </header>

        <div class="obs-requirement-banner brutalist-alert">
            <span class="alert-icon">⚠️</span>
            <div class="alert-text">
                <strong>Prerequisite Required:</strong> GhostChar depends entirely on the background virtual camera driver included with <strong>OBS Studio</strong>. You must have OBS installed for the virtual webcam device routing to activate.
            </div>
        </div>

        <section class="main-card glassmorphic focal-point">
            <div class="card-inner">
                <div class="platform-info">
                    <span class="platform-badge">Universal Build</span>
                    <h2>GhostChar Installer</h2>
                    <p class="file-meta">Universal DMG Disk Image / Apple Silicon (M1/M2/M3/M4) & Intel</p>
                </div>
                <a href="{base}/downloads/GhostChar.dmg" class="btn-download" download>
                    <span class="download-icon">📥</span>
                    <div class="text">
                        <span class="btn-label">Download for macOS</span>
                        <span class="btn-sub">Universal .dmg (110MB)</span>
                    </div>
                </a>
            </div>
        </section>

        <section class="install-guide">
            <h2>Installation Checklist</h2>
            <div class="steps-grid">
                <div class="step-card glassmorphic alert-card">
                    <div class="step-num">01</div>
                    <h3>Install OBS Studio</h3>
                    <p>Ensure OBS Studio is installed on your Mac to provide the system-level virtual camera background extension driver.</p>
                </div>
                <div class="step-card glassmorphic">
                    <div class="step-num">02</div>
                    <h3>Download & Mount</h3>
                    <p>Retrieve the <code>GhostChar.dmg</code> installer and open the disk image layout screen.</p>
                </div>
                <div class="step-card glassmorphic">
                    <div class="step-num">03</div>
                    <h3>Deploy & Authorize</h3>
                    <p>Drag <strong>GhostChar.app</strong> into <strong>Applications</strong>. Enable the virtual extension in <em>Privacy & Security</em> if prompted.</p>
                </div>
            </div>
        </section>

        <section class="security-layout">
            <div class="sec-card gatekeeper-card glassmorphic">
                <div class="sec-header warning-header">
                    <span class="sec-icon warning-icon">🛠️</span>
                    <h3>Gatekeeper Override</h3>
                </div>
                <p class="sec-desc">
                    Because this app is compiled locally without an Apple Developer ID, Gatekeeper might block execution and throw a <span class="quote">"damaged file"</span> error.
                </p>
                <p class="sec-sub">
                    Clear the Gatekeeper quarantine flag by running this command in your Terminal shell:
                </p>
                
                <div class="code-box">
                    <code class="cmd-text">xattr -cr /Applications/GhostChar.app</code>
                    <button onclick={copyCommand} class="btn-copy" aria-label="Copy terminal command">
                        {#if copied}
                            <span class="copy-success">✓ Copied!</span>
                        {:else}
                            <span>📋 Copy</span>
                        {/if}
                    </button>
                </div>
            </div>

            <div class="sec-card vcam-card glassmorphic">
                <div class="sec-header info-header">
                    <span class="sec-icon info-icon">🔌</span>
                    <h3>Headless Driver Details</h3>
                </div>
                <p class="sec-desc">
                    GhostChar exposes native application output directly to macOS core audio/video frameworks using background plugins:
                </p>
                <div class="vcam-bullet-list">
                    <div class="vcam-bullet">
                        <span class="bullet-dot"></span>
                        <p><strong>No App Overhead</strong>: You do <strong>not</strong> need to keep the full OBS Studio interface running; it works purely as a headless background server extension.</p>
                    </div>
                    <div class="vcam-bullet">
                        <span class="bullet-dot"></span>
                        <p><strong>System Targets</strong>: Once mapped, the output will register smoothly across Discord, Zoom, and web browsers as a hardware video input device.</p>
                    </div>
                </div>
            </div>
        </section>
    </div>
</div>

<style>
    .download-page {
        position: relative;
        font-family: var(--font-family);
        color: var(--on-surface);
        padding: 4rem 1.5rem;
        min-height: 100vh;
        overflow: hidden;
        background-color: var(--surface);
    }

    .page-glow {
        position: absolute;
        top: -15%;
        left: 50%;
        transform: translateX(-50%);
        width: 1100px;
        height: 850px;
        background: radial-gradient(circle, rgba(163, 216, 212, 0.15) 0%, rgba(31, 78, 75, 0.04) 50%, rgba(0, 0, 0, 0) 70%);
        border-radius: 50%;
        filter: blur(120px);
        pointer-events: none;
        z-index: 0;
    }

    .container {
        position: relative;
        z-index: 1;
        max-width: 860px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 3rem;
    }

    .download-header {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .app-logo {
        max-width: 120px;
        height: auto;
        border-radius: 28px;
        box-shadow: 0 12px 40px rgba(163, 216, 212, 0.25);
        border: 1px solid rgba(163, 216, 212, 0.2);
        margin-bottom: 1.5rem;
    }

    .animate-float {
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .ascii-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(163, 216, 212, 0.08);
        border: 1px solid rgba(163, 216, 212, 0.2);
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: var(--primary);
        margin-bottom: 1.25rem;
        text-transform: uppercase;
    }

    .pulse {
        display: inline-block;
        width: 6px;
        height: 6px;
        background-color: var(--primary);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--primary);
    }

    .download-header h1 {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.75rem;
        background: linear-gradient(135deg, #ffffff 0%, var(--primary) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-size: 1.2rem;
        color: var(--on-surface-variant);
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* HIGH-CONTRAST PREREQUISITE WARNING BANNER */
    .brutalist-alert {
        background: rgba(239, 68, 68, 0.07);
        border: 2px solid rgba(239, 68, 68, 0.35);
        border-radius: 4px;
        padding: 1.25rem 1.75rem;
        display: flex;
        gap: 1.25rem;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    .alert-icon {
        font-size: 1.75rem;
        flex-shrink: 0;
    }

    .alert-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #fca5a5;
    }

    .alert-text strong {
        color: #ef4444;
    }

    /* GLASSMORPHISM UTILITIES */
    .glassmorphic {
        background: rgba(25, 27, 28, 0.45);
        border: 1px solid rgba(163, 216, 212, 0.08);
        border-radius: 6px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* DOWNLOAD HERO SECTORS */
    .focal-point {
        border-color: rgba(163, 216, 212, 0.2);
        background: rgba(28, 31, 32, 0.6);
        box-shadow: 0 12px 40px rgba(163, 216, 212, 0.05);
        position: relative;
    }

    .focal-point::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 6px;
        padding: 1px;
        background: linear-gradient(to bottom right, rgba(163,216,212,0.3), transparent 60%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }

    .main-card {
        padding: 3rem;
    }

    .card-inner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 2rem;
    }

    .platform-info h2 {
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .platform-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        background: rgba(163, 216, 212, 0.1);
        color: var(--primary);
        padding: 0.2rem 0.75rem;
        border-radius: 12px;
        border: 1px solid rgba(163, 216, 212, 0.25);
        margin-bottom: 0.75rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .file-meta {
        font-size: 0.95rem;
        color: var(--on-surface-variant);
    }

    .btn-download {
        display: inline-flex;
        align-items: center;
        gap: 1.25rem;
        background: var(--primary);
        color: var(--on-primary);
        padding: 1.25rem 2.75rem;
        text-decoration: none;
        border-radius: var(--roundness);
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 24px rgba(163, 216, 212, 0.25);
    }

    .btn-download:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 36px rgba(163, 216, 212, 0.4);
        background: #bbeeec;
    }

    .btn-download .download-icon {
        font-size: 2rem;
    }

    .btn-download .text {
        display: flex;
        flex-direction: column;
        text-align: left;
    }

    .btn-label {
        font-size: 1.15rem;
        line-height: 1.2;
    }

    .btn-sub {
        font-size: 0.75rem;
        opacity: 0.85;
        font-weight: 500;
        margin-top: 0.2rem;
    }

    /* TIMELINE CHECKLIST GRID */
    .install-guide h2 {
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }

    .steps-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }

    .step-card {
        padding: 2.25rem 2rem;
        position: relative;
    }

    .alert-card {
        border-color: rgba(239, 68, 68, 0.2);
    }

    .step-num {
        font-family: monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: rgba(163, 216, 212, 0.05);
        position: absolute;
        top: 1rem;
        right: 1.5rem;
    }

    .alert-card .step-num {
        color: rgba(239, 68, 68, 0.05);
    }

    .step-card h3 {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.85rem;
        color: var(--primary);
    }

    .alert-card h3 {
        color: #f87171;
    }

    .step-card p {
        font-size: 0.95rem;
        color: var(--on-surface-variant);
        line-height: 1.6;
    }

    /* TECHNICAL FOOTER CONTAINER */
    .security-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }

    .sec-card {
        padding: 2.25rem;
        display: flex;
        flex-direction: column;
    }

    .sec-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }

    .sec-icon {
        font-size: 1.5rem;
    }

    .sec-card h3 {
        font-size: 1.3rem;
        font-weight: 700;
    }

    .warning-header h3 {
        color: #beeeea;
    }

    .info-header h3 {
        color: var(--primary);
    }

    .sec-desc {
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1rem;
        color: var(--on-surface);
    }

    .quote {
        font-family: monospace;
        background: rgba(0, 0, 0, 0.35);
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        color: #f87171;
    }

    .sec-sub {
        font-size: 0.9rem;
        color: var(--on-surface-variant);
        margin-bottom: 1.25rem;
    }

    .code-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #070809;
        border: 1px solid rgba(163, 216, 212, 0.1);
        border-radius: var(--roundness);
        padding: 0.875rem 1.25rem;
        font-family: monospace;
        font-size: 0.9rem;
        margin-top: auto;
        gap: 1rem;
        overflow-x: auto;
    }

    .cmd-text {
        color: #beeeea;
        white-space: nowrap;
    }

    .btn-copy {
        background: rgba(163, 216, 212, 0.05);
        border: 1px solid rgba(163, 216, 212, 0.15);
        color: var(--primary);
        padding: 0.4rem 0.85rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-copy:hover {
        background: rgba(163, 216, 212, 0.12);
        border-color: var(--primary);
    }

    .copy-success {
        color: #4ade80;
    }

    .vcam-bullet-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: auto;
    }

    .vcam-bullet {
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
    }

    .bullet-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        background-color: var(--primary);
        border-radius: 50%;
        margin-top: 0.5rem;
        flex-shrink: 0;
    }

    .vcam-bullet p {
        font-size: 0.9rem;
        color: var(--on-surface-variant);
        line-height: 1.5;
    }

    @media (max-width: 900px) {
        .security-layout {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .card-inner {
            flex-direction: column;
            align-items: stretch;
        }

        .btn-download {
            justify-content: center;
        }

        .steps-grid {
            grid-template-columns: 1fr;
        }

        .code-box {
            flex-direction: column;
            align-items: stretch;
            gap: 0.75rem;
        }

        .btn-copy {
            text-align: center;
        }
    }
</style>