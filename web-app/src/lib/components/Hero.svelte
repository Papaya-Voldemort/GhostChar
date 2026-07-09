<script lang="ts">
	import { resolve } from '$app/paths';
</script>

<div class="hero">
	<div class="hero-glow"></div>
	<div class="hero-content">
		<div class="ascii-badge">
			<span class="pulse"></span> NEURAL ART GENERATOR
		</div>
		
		<h1 class="hero-title">
			Translate Your World <br />
			Into <span class="neon-text">High-Fidelity ASCII</span>
		</h1>
		
		<p class="hero-subtitle">
			GhostChar uses real-time neural network inference to convert video streams and media files into stunning, interactive CRT-style text artwork.
		</p>
		
		<div class="cta-container">
			<a href={resolve('/demo')} class="btn btn-primary">
				Launch Live Demo
				<span class="btn-icon">→</span>
			</a>
			<a href={resolve('/download')} class="btn btn-secondary">
				Download Desktop App
				<span class="btn-icon">⚡</span>
			</a>
		</div>

		<div class="features-preview">
			<div class="feature-card">
				<div class="feature-icon">👁️</div>
				<h3>Real-Time Camera</h3>
				<p>Transform webcam streams at up to 60 FPS with zero latency.</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon">🧠</div>
				<h3>Neural Core</h3>
				<p>Powered by local ONNX model classifications for rich shading.</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon">👾</div>
				<h3>Virtual Camera</h3>
				<p>Stream directly to Discord, Zoom, or OBS as a virtual webcam.</p>
			</div>
		</div>
	</div>
</div>

<style>
	.hero {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: calc(85vh - 100px);
		padding: 4rem 2rem;
		text-align: center;
		font-family: var(--font-family);
		color: var(--on-surface);
		overflow: hidden;
	}

	.hero-glow {
		position: absolute;
		top: 10%;
		left: 50%;
		transform: translate(-50%, -20%);
		width: 600px;
		height: 600px;
		background: radial-gradient(circle, rgba(163, 216, 212, 0.15) 0%, rgba(31, 78, 75, 0.05) 50%, rgba(0, 0, 0, 0) 70%);
		border-radius: 50%;
		filter: blur(80px);
		pointer-events: none;
		z-index: 0;
	}

	.hero-content {
		position: relative;
		z-index: 1;
		max-width: 900px;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.ascii-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		background: rgba(163, 216, 212, 0.08);
		border: 1px solid rgba(163, 216, 212, 0.2);
		padding: 0.5rem 1rem;
		border-radius: 20px;
		font-size: 0.8rem;
		font-weight: 600;
		letter-spacing: 0.15em;
		color: var(--primary);
		margin-bottom: 2rem;
		text-transform: uppercase;
	}

	.pulse {
		display: inline-block;
		width: 8px;
		height: 8px;
		background-color: var(--primary);
		border-radius: 50%;
		box-shadow: 0 0 8px var(--primary);
		animation: pulse-glow 2s infinite;
	}

	@keyframes pulse-glow {
		0% {
			transform: scale(0.95);
			box-shadow: 0 0 0 0 rgba(163, 216, 212, 0.7);
		}
		70% {
			transform: scale(1);
			box-shadow: 0 0 0 8px rgba(163, 216, 212, 0);
		}
		100% {
			transform: scale(0.95);
			box-shadow: 0 0 0 0 rgba(163, 216, 212, 0);
		}
	}

	.hero-title {
		font-size: 3.5rem;
		font-weight: 800;
		line-height: 1.15;
		letter-spacing: -0.02em;
		margin-bottom: 1.5rem;
	}

	.neon-text {
		color: var(--primary);
		text-shadow: 0 0 30px rgba(163, 216, 212, 0.3);
	}

	.hero-subtitle {
		font-size: 1.25rem;
		color: var(--on-surface-variant);
		max-width: 650px;
		margin-bottom: 3rem;
		line-height: 1.6;
	}

	.cta-container {
		display: flex;
		gap: 1.5rem;
		margin-bottom: 5rem;
		flex-wrap: wrap;
		justify-content: center;
	}

	.btn {
		display: inline-flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 2rem;
		font-size: 1rem;
		font-weight: 700;
		text-decoration: none;
		border-radius: var(--roundness);
		transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
		border: 1px solid transparent;
		letter-spacing: 0.02em;
	}

	.btn-primary {
		background-color: var(--primary);
		color: var(--on-primary);
		box-shadow: 0 4px 20px rgba(163, 216, 212, 0.25);
	}

	.btn-primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 30px rgba(163, 216, 212, 0.4);
		background-color: #beece9;
	}

	.btn-secondary {
		background-color: transparent;
		border-color: rgba(163, 216, 212, 0.3);
		color: var(--primary);
	}

	.btn-secondary:hover {
		transform: translateY(-2px);
		background-color: rgba(163, 216, 212, 0.05);
		border-color: var(--primary);
	}

	.btn-icon {
		font-size: 1.1rem;
		transition: transform 0.2s;
	}

	.btn-primary:hover .btn-icon {
		transform: translateX(4px);
	}

	.btn-secondary:hover .btn-icon {
		transform: rotate(15deg);
	}

	.features-preview {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 2rem;
		width: 100%;
		max-width: 1000px;
		text-align: left;
		border-top: 1px solid rgba(163, 216, 212, 0.1);
		padding-top: 4rem;
	}

	.feature-card {
		background: rgba(31, 32, 33, 0.4);
		border: 1px solid rgba(163, 216, 212, 0.05);
		border-radius: var(--roundness);
		padding: 2rem;
		transition: all 0.3s;
	}

	.feature-card:hover {
		border-color: rgba(163, 216, 212, 0.2);
		background: rgba(31, 32, 33, 0.6);
		transform: translateY(-4px);
	}

	.feature-icon {
		font-size: 2rem;
		margin-bottom: 1rem;
	}

	.feature-card h3 {
		font-size: 1.15rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
		color: var(--on-surface);
	}

	.feature-card p {
		font-size: 0.95rem;
		color: var(--on-surface-variant);
		line-height: 1.5;
	}

	@media (max-width: 768px) {
		.hero-title {
			font-size: 2.5rem;
		}
		
		.features-preview {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.cta-container {
			flex-direction: column;
			width: 100%;
		}

		.btn {
			width: 100%;
			justify-content: center;
		}
	}
</style>