<script lang="ts">
	import { base } from '$app/paths';
	import { onMount, onDestroy } from 'svelte';
	import appIcon from '$lib/assets/ghostchar_app_icon.png';

	let copied = $state(false);
	let webcams = $state<MediaDeviceInfo[]>([]);
	let selectedCamId = $state<string>('');
	let isStreaming = $state(false);
	let errorMessage = $state('');
	
	let videoEl = $state<HTMLVideoElement | null>(null);
	let canvasEl = $state<HTMLCanvasElement | null>(null);
	let stream: MediaStream | null = null;
	let animationFrameId: number | null = null;

	// Monospace ASCII density character ramp
	const CHARS = [" ", ".", ",", "-", "~", ":", "i", "r", "s", "t", "l", "C", "O", "Z", "w", "m", "#", "8", "%", "@"];

	function copyCommand() {
		navigator.clipboard.writeText('xattr -cr /Applications/GhostChar.app');
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}

	async function getCameras() {
		try {
			// Trigger a permission prompt if we haven't already to list device names
			if (!webcams.some(w => w.label)) {
				await navigator.mediaDevices.getUserMedia({ video: true });
			}
			const devices = await navigator.mediaDevices.enumerateDevices();
			webcams = devices.filter(device => device.kind === 'videoinput');
			if (webcams.length > 0 && !selectedCamId) {
				selectedCamId = webcams[0].deviceId;
			}
		} catch (err: any) {
			console.error('Error fetching cameras:', err);
			errorMessage = 'Camera permission denied. Please grant camera access to use the online tester.';
		}
	}

	async function startCameraTest() {
		errorMessage = '';
		if (stream) {
			stopCameraTest();
		}
		
		try {
			stream = await navigator.mediaDevices.getUserMedia({
				video: {
					deviceId: selectedCamId ? { exact: selectedCamId } : undefined,
					width: { ideal: 640 },
					height: { ideal: 480 }
				}
			});
			
			if (videoEl) {
				videoEl.srcObject = stream;
				videoEl.onloadedmetadata = () => {
					videoEl?.play();
					isStreaming = true;
					renderLoop();
				};
			}
		} catch (err: any) {
			console.error('Error starting camera test:', err);
			errorMessage = 'Could not access the selected camera. Check system permissions.';
		}
	}

	function stopCameraTest() {
		isStreaming = false;
		if (animationFrameId) {
			cancelAnimationFrame(animationFrameId);
			animationFrameId = null;
		}
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
			stream = null;
		}
		if (videoEl) {
			videoEl.srcObject = null;
		}
		
		// Clear canvas
		if (canvasEl) {
			const ctx = canvasEl.getContext('2d');
			if (ctx) {
				ctx.fillStyle = '#0d0e0f';
				ctx.fillRect(0, 0, canvasEl.width, canvasEl.height);
			}
		}
	}

	function renderLoop() {
		if (!isStreaming || !videoEl || !canvasEl) return;

		const ctx = canvasEl.getContext('2d');
		if (!ctx) return;

		// Monospace ASCII Grid Settings
		const cols = 85;
		const fontAspect = 0.55; 
		const aspect = videoEl.videoWidth / videoEl.videoHeight || 4/3;
		const rows = Math.max(10, Math.round((cols / aspect) * fontAspect));

		// Downsample frames offscreen
		const offscreen = document.createElement('canvas');
		offscreen.width = cols;
		offscreen.height = rows;
		const offscreenCtx = offscreen.getContext('2d');
		
		if (offscreenCtx) {
			offscreenCtx.drawImage(videoEl, 0, 0, cols, rows);
			const imgData = offscreenCtx.getImageData(0, 0, cols, rows);
			const data = imgData.data;

			const charWidth = 8;
			const charHeight = 14;
			const targetWidth = cols * charWidth;
			const targetHeight = rows * charHeight;

			if (canvasEl.width !== targetWidth || canvasEl.height !== targetHeight) {
				canvasEl.width = targetWidth;
				canvasEl.height = targetHeight;
			}

			// Background fill
			ctx.fillStyle = '#0d0e0f';
			ctx.fillRect(0, 0, targetWidth, targetHeight);
			
			// Glowing Text Color Config
			ctx.fillStyle = '#a3d8d4'; 
			ctx.shadowColor = '#a3d8d4';
			ctx.shadowBlur = 4;
			ctx.font = 'bold 11px monospace';
			ctx.textAlign = 'left';
			ctx.textBaseline = 'top';

			for (let r = 0; r < rows; r++) {
				let line = '';
				for (let c = 0; c < cols; c++) {
					const idx = (r * cols + c) * 4;
					const red = data[idx];
					const green = data[idx + 1];
					const blue = data[idx + 2];

					const grayVal = (red * 0.299 + green * 0.587 + blue * 0.114);
					const charIdx = Math.floor((grayVal / 255) * (CHARS.length - 1));
					line += CHARS[charIdx];
				}
				ctx.fillText(line, 0, r * charHeight);
			}
		}

		animationFrameId = requestAnimationFrame(renderLoop);
	}

	onMount(() => {
		navigator.mediaDevices.enumerateDevices().then(devices => {
			const cams = devices.filter(device => device.kind === 'videoinput');
			if (cams.length > 0) {
				webcams = cams;
				if (cams[0].deviceId && cams[0].label) {
					selectedCamId = cams[0].deviceId;
				}
			}
		});
	});

	onDestroy(() => {
		stopCameraTest();
	});
</script>

<svelte:head>
	<title>&lt;GhostChar /&gt; // Download Desktop</title>
	<meta name="description" content="Download GhostChar for macOS. Neural network real-time ASCII art webcam utility with dynamic browser camera checker." />
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

		<!-- DYNAMIC CAMERA TESTER CARD -->
		<section class="tester-card glassmorphic">
			<div class="tester-header">
				<span class="icon">🔮</span>
				<div>
					<h2>Interactive Web Camera Tester</h2>
					<p class="sec-label">Scan your system webcams and render live ASCII in-browser</p>
				</div>
			</div>

			<div class="tester-content">
				{#if errorMessage}
					<div class="error-banner">
						<span class="error-icon">⚠️</span>
						<p>{errorMessage}</p>
					</div>
				{/if}

				<div class="control-row">
					<div class="select-wrapper">
						<select id="camera-select" bind:value={selectedCamId} onclick={getCameras} aria-label="Select camera">
							{#if webcams.length === 0}
								<option value="">-- Detect system cameras --</option>
							{:else}
								{#each webcams as webcam}
									<option value={webcam.deviceId}>{webcam.label || 'Webcam ' + webcam.deviceId.slice(0, 5)}</option>
								{/each}
							{/if}
						</select>
					</div>
					
					<div class="action-buttons">
						{#if isStreaming}
							<button onclick={stopCameraTest} class="btn-control btn-stop">
								Stop Test
							</button>
						{:else}
							<button onclick={startCameraTest} class="btn-control btn-start" disabled={!selectedCamId}>
								Start Camera Test
							</button>
						{/if}
					</div>
				</div>

				<div class="preview-frame">
					<video bind:this={videoEl} class="hidden-video" autoplay playsinline muted></video>
					<canvas bind:this={canvasEl} class="ascii-canvas"></canvas>
					{#if !isStreaming}
						<div class="canvas-placeholder">
							<span class="placeholder-ghost animate-float-slow">👻</span>
							<p>Camera feed offline. Select a camera and click "Start Camera Test" to preview the ASCII filter.</p>
						</div>
					{/if}
				</div>
			</div>
		</section>

		<!-- MAIN DOWNLOAD CARD -->
		<section class="main-card glassmorphic">
			<div class="card-inner">
				<div class="platform-info">
					<span class="platform-badge">Universal</span>
					<h2>GhostChar Installer</h2>
					<p class="file-meta">Universal DMG Disk Image / Support for Apple M1/M2/M3/M4 & Intel chips</p>
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

		<!-- STEPS CONTAINER -->
		<section class="install-guide">
			<h2>Installation Checklist</h2>
			<div class="steps-grid">
				<div class="step-card glassmorphic">
					<div class="step-num">01</div>
					<h3>Download DMG</h3>
					<p>Retrieve the <code>GhostChar.dmg</code> installer disk image by clicking the download button.</p>
				</div>
				<div class="step-card glassmorphic">
					<div class="step-num">02</div>
					<h3>Drag to Applications</h3>
					<p>Mount the DMG installer and drag the <strong>GhostChar.app</strong> icon to your <strong>Applications</strong> folder.</p>
				</div>
				<div class="step-card glassmorphic">
					<div class="step-num">03</div>
					<h3>Launch & Setup</h3>
					<p>Open GhostChar. A custom ghost status menu icon will load in your menu bar at the top-right.</p>
				</div>
			</div>
		</section>

		<!-- TECHNICAL SUPPORT GUIDES -->
		<section class="security-layout">
			<div class="sec-card gatekeeper-card glassmorphic">
				<div class="sec-header warning-header">
					<span class="sec-icon warning-icon">⚠️</span>
					<h3>Gatekeeper Override</h3>
				</div>
				<p class="sec-desc">
					Because this app is compiled locally without an Apple Developer ID, Gatekeeper might block execution and show a <span class="quote">"damaged file"</span> error.
				</p>
				<p class="sec-sub">
					Clear the Gatekeeper quarantine flag by running the following command in Terminal:
				</p>
				
				<div class="code-box">
					<code class="cmd-text">xattr -cr /Applications/GhostChar.app</code>
					<button onclick={copyCommand} class="btn-copy" aria-label="Copy terminal command">
						{#if copied}
							<span class="copy-success">✓ Copied!</span>
						{:else}
							<span>📋 Copy Command</span>
						{/if}
					</button>
				</div>
			</div>

			<div class="sec-card vcam-card glassmorphic">
				<div class="sec-header info-header">
					<span class="sec-icon info-icon">🔌</span>
					<h3>No-OBS Virtual Camera</h3>
				</div>
				<p class="sec-desc">
					GhostChar uses CoreMediaIO plugins to expose output frames as a system webcam. Here's what you need to know:
				</p>
				<div class="vcam-bullet-list">
					<div class="vcam-bullet">
						<span class="bullet-dot"></span>
						<p><strong>Driver Dependency</strong>: The system requires the lightweight virtual webcam extension from OBS Studio to capture streams.</p>
					</div>
					<div class="vcam-bullet">
						<span class="bullet-dot"></span>
						<p><strong>Headless Routing</strong>: You do **not** need the full OBS application to be open. The extension works entirely as a background driver.</p>
					</div>
					<div class="vcam-bullet">
						<span class="bullet-dot"></span>
						<p><strong>Sonoma/Sequoia Security</strong>: Make sure the virtual camera system extension is enabled in <em>System Settings > Privacy & Security</em>.</p>
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
		padding: 3rem 1.5rem;
		min-height: 100vh;
		overflow: hidden;
		background-color: var(--surface);
	}

	.page-glow {
		position: absolute;
		top: -10%;
		left: 50%;
		transform: translateX(-50%);
		width: 1000px;
		height: 800px;
		background: radial-gradient(circle, rgba(163, 216, 212, 0.12) 0%, rgba(31, 78, 75, 0.03) 50%, rgba(0, 0, 0, 0) 70%);
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
		gap: 3.5rem;
	}

	.download-header {
		text-align: center;
		margin-top: 1rem;
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

	.animate-float-slow {
		animation: float 8s ease-in-out infinite;
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
		animation: pulse-glow 2s infinite;
	}

	@keyframes pulse-glow {
		0%, 100% {
			transform: scale(0.95);
			box-shadow: 0 0 0 0 rgba(163, 216, 212, 0.6);
		}
		70% {
			transform: scale(1);
			box-shadow: 0 0 0 6px rgba(163, 216, 212, 0);
		}
	}

	.download-header h1 {
		font-size: 2.85rem;
		font-weight: 800;
		letter-spacing: -0.02em;
		margin-bottom: 0.75rem;
		background: linear-gradient(135deg, #ffffff 0%, var(--primary) 100%);
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.subtitle {
		font-size: 1.15rem;
		color: var(--on-surface-variant);
		max-width: 600px;
		margin: 0 auto;
		line-height: 1.6;
	}

	/* GLASSMORPHISM GLOBAL */
	.glassmorphic {
		background: rgba(25, 27, 28, 0.45);
		border: 1px solid rgba(163, 216, 212, 0.08);
		border-radius: 6px;
		backdrop-filter: blur(12px);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
		transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
	}

	.glassmorphic:hover {
		border-color: rgba(163, 216, 212, 0.15);
		background: rgba(25, 27, 28, 0.55);
	}

	/* CAMERA TESTER CARD */
	.tester-card {
		padding: 2.5rem;
	}

	.tester-header {
		display: flex;
		gap: 1.25rem;
		align-items: center;
		margin-bottom: 1.75rem;
		border-bottom: 1px solid rgba(163, 216, 212, 0.06);
		padding-bottom: 1.25rem;
	}

	.tester-header .icon {
		font-size: 2.25rem;
	}

	.tester-header h2 {
		font-size: 1.6rem;
		font-weight: 700;
		margin-bottom: 0.15rem;
	}

	.sec-label {
		font-size: 0.9rem;
		color: var(--on-surface-variant);
	}

	.tester-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.control-row {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 1.25rem;
		align-items: center;
	}

	.select-wrapper {
		position: relative;
		width: 100%;
	}

	select {
		background-color: rgba(0, 0, 0, 0.25);
		border: 1px solid rgba(163, 216, 212, 0.15);
		border-radius: var(--roundness);
		color: var(--on-surface);
		padding: 0.8rem 1.25rem;
		font-size: 0.95rem;
		width: 100%;
		cursor: pointer;
		outline: none;
		transition: all 0.3s;
		appearance: none;
	}

	select:hover {
		border-color: rgba(163, 216, 212, 0.4);
		background-color: rgba(0, 0, 0, 0.35);
	}

	.select-wrapper::after {
		content: "▾";
		position: absolute;
		right: 1.25rem;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
		color: var(--on-surface-variant);
	}

	.btn-control {
		padding: 0.8rem 2rem;
		border-radius: var(--roundness);
		font-size: 0.95rem;
		font-weight: 700;
		transition: all 0.2s ease;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
	}

	.btn-start {
		background-color: var(--primary);
		color: var(--on-primary);
	}

	.btn-start:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 6px 20px rgba(163, 216, 212, 0.3);
		background-color: #beece9;
	}

	.btn-start:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-stop {
		background-color: rgba(239, 68, 68, 0.15);
		border: 1px solid rgba(239, 68, 68, 0.3);
		color: #f87171;
	}

	.btn-stop:hover {
		background-color: rgba(239, 68, 68, 0.25);
		border-color: #ef4444;
	}

	/* CRT ASCIIPREVIEW SCREEN */
	.preview-frame {
		position: relative;
		border: 1px solid rgba(163, 216, 212, 0.15);
		border-radius: var(--roundness);
		overflow: hidden;
		background: #090a0b;
		aspect-ratio: 16 / 9;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.9);
	}

	/* CRT Scanline Shader Overlay */
	.preview-frame::after {
		content: " ";
		display: block;
		position: absolute;
		top: 0; left: 0; bottom: 0; right: 0;
		background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.05), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.05));
		z-index: 2;
		background-size: 100% 4px, 6px 100%;
		pointer-events: none;
	}

	.hidden-video {
		display: none;
	}

	.ascii-canvas {
		display: block;
		max-width: 100%;
		max-height: 100%;
		object-fit: contain;
	}

	.canvas-placeholder {
		position: absolute;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 1.25rem;
		padding: 2rem;
		z-index: 1;
	}

	.placeholder-ghost {
		font-size: 3.5rem;
		opacity: 0.25;
		color: var(--primary);
	}

	.canvas-placeholder p {
		font-size: 0.95rem;
		color: var(--on-surface-variant);
		max-width: 380px;
		line-height: 1.5;
	}

	.error-banner {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background-color: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		padding: 0.75rem 1.25rem;
		border-radius: var(--roundness);
		color: #f87171;
		font-size: 0.9rem;
	}

	/* DOWNLOAD CARD */
	.main-card {
		padding: 2.5rem;
	}

	.card-inner {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 2rem;
	}

	.platform-info h2 {
		font-size: 1.6rem;
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
		font-size: 0.9rem;
		color: var(--on-surface-variant);
	}

	.btn-download {
		display: inline-flex;
		align-items: center;
		gap: 1.25rem;
		background: var(--primary);
		color: var(--on-primary);
		padding: 1.1rem 2.5rem;
		text-decoration: none;
		border-radius: var(--roundness);
		font-weight: 700;
		transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
		box-shadow: 0 4px 20px rgba(163, 216, 212, 0.2);
	}

	.btn-download:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 30px rgba(163, 216, 212, 0.35);
		background: #bbeeec;
	}

	.btn-download .download-icon {
		font-size: 1.85rem;
	}

	.btn-download .text {
		display: flex;
		flex-direction: column;
		text-align: left;
	}

	.btn-label {
		font-size: 1.1rem;
		line-height: 1.2;
	}

	.btn-sub {
		font-size: 0.75rem;
		opacity: 0.85;
		font-weight: 500;
		margin-top: 0.15rem;
	}

	/* STEPS GUIDELINE */
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

	.step-num {
		font-family: monospace;
		font-size: 2.5rem;
		font-weight: 700;
		color: rgba(163, 216, 212, 0.08);
		position: absolute;
		top: 1rem;
		right: 1.5rem;
	}

	.step-card h3 {
		font-size: 1.2rem;
		font-weight: 700;
		margin-bottom: 0.85rem;
		color: var(--primary);
	}

	.step-card p {
		font-size: 0.95rem;
		color: var(--on-surface-variant);
		line-height: 1.6;
	}

	/* DUAL SECURITY & SUPPORT LAYOUT */
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
		color: #f87171;
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
		white-space: nowrap;
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

		.control-row {
			grid-template-columns: 1fr;
		}

		.btn-control {
			width: 100%;
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
