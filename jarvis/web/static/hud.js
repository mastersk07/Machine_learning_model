/* Reactive WebGL "arc reactor" core. States: idle, listening, thinking, speaking. */
(function () {
  const container = document.getElementById("scene-container");

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    55, window.innerWidth / window.innerHeight, 0.1, 100
  );
  camera.position.z = 6;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const COLORS = {
    idle: 0x4ff3ff,
    listening: 0x5dffa0,
    thinking: 0xffb04a,
    speaking: 0x4ff3ff,
  };

  const group = new THREE.Group();
  scene.add(group);

  // Core sphere
  const coreGeo = new THREE.IcosahedronGeometry(1, 2);
  const coreMat = new THREE.MeshBasicMaterial({
    color: COLORS.idle,
    wireframe: true,
    transparent: true,
    opacity: 0.85,
  });
  const core = new THREE.Mesh(coreGeo, coreMat);
  group.add(core);

  // Orbiting rings
  const rings = [];
  for (let i = 0; i < 3; i++) {
    const ringGeo = new THREE.TorusGeometry(1.6 + i * 0.35, 0.01, 8, 128);
    const ringMat = new THREE.MeshBasicMaterial({
      color: COLORS.idle,
      transparent: true,
      opacity: 0.5 - i * 0.1,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.random() * Math.PI;
    ring.rotation.y = Math.random() * Math.PI;
    group.add(ring);
    rings.push(ring);
  }

  // Particle field
  const particleCount = 400;
  const positions = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount; i++) {
    const r = 3 + Math.random() * 4;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
  }
  const particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: COLORS.idle,
    size: 0.02,
    transparent: true,
    opacity: 0.6,
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  let state = "idle";
  let pulseSpeed = 1;
  let targetScale = 1;
  const clock = new THREE.Clock();

  window.JarvisHUD = {
    setState(next) {
      state = next;
      const color = COLORS[state] ?? COLORS.idle;
      coreMat.color.setHex(color);
      particleMat.color.setHex(color);
      rings.forEach((r) => r.material.color.setHex(color));
      pulseSpeed = { idle: 0.6, listening: 2.2, thinking: 1.6, speaking: 3 }[state] ?? 1;
      targetScale = state === "listening" ? 1.25 : state === "speaking" ? 1.15 : 1;

      const label = document.getElementById("state-label");
      label.textContent = state.toUpperCase();
      label.className = state;
    },
  };

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    const pulse = 1 + Math.sin(t * pulseSpeed) * 0.06;
    const scale = THREE.MathUtils.lerp(core.scale.x, targetScale * pulse, 0.1);
    core.scale.setScalar(scale);

    core.rotation.y += 0.003;
    core.rotation.x += 0.001;

    rings.forEach((ring, i) => {
      ring.rotation.z += 0.002 * (i + 1) * (state === "thinking" ? 3 : 1);
      ring.rotation.x += 0.001 * (i + 1);
    });

    particles.rotation.y += 0.0006;

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
