import React, { useEffect, useRef } from 'react';
import { Renderer, Camera, Geometry, Program, Mesh } from 'ogl';
import '../css/Particles.css';

const defaultColors = ['#ffffff', '#ffffff', '#ffffff'];

const hexToRgb = hex => {
  hex = hex.replace(/^#/, '');
  if (hex.length === 3) {
    hex = hex
      .split('')
      .map(c => c + c)
      .join('');
  }
  const int = parseInt(hex, 16);
  const r = ((int >> 16) & 255) / 255;
  const g = ((int >> 8) & 255) / 255;
  const b = (int & 255) / 255;
  return [r, g, b];
};

const vertex = /* glsl */ `
  attribute vec3 position;
  attribute vec4 random;
  attribute vec3 color;

  uniform mat4 modelMatrix;
  uniform mat4 viewMatrix;
  uniform mat4 projectionMatrix;
  uniform float uTime;
  uniform float uSpread;
  uniform float uBaseSize;
  uniform float uSizeRandomness;

  varying vec4 vRandom;
  varying vec3 vColor;

  void main() {
    vRandom = random;
    vColor = color;

    vec3 pos = position * uSpread;
    pos.z *= 10.0;

    vec4 mPos = modelMatrix * vec4(pos, 1.0);
    float t = uTime;
    mPos.x += sin(t * random.z + 6.28 * random.w) * mix(0.1, 1.5, random.x);
    mPos.y += sin(t * random.y + 6.28 * random.x) * mix(0.1, 1.5, random.w);
    mPos.z += sin(t * random.w + 6.28 * random.y) * mix(0.1, 1.5, random.z);

    vec4 mvPos = viewMatrix * mPos;

    if (uSizeRandomness == 0.0) {
      gl_PointSize = uBaseSize;
    } else {
      gl_PointSize = (uBaseSize * (1.0 + uSizeRandomness * (random.x - 0.5))) / -mvPos.z;
    }

    gl_Position = projectionMatrix * mvPos;
  }
`;

const fragment = /* glsl */ `
  precision highp float;

  uniform float uTime;
  uniform float uAlphaParticles;
  varying vec4 vRandom;
  varying vec3 vColor;

  void main() {
    vec2 uv = gl_PointCoord.xy;
    float d = length(uv - vec2(0.5));

    if(uAlphaParticles < 0.5) {
      if(d > 0.5) {
        discard;
      }
      gl_FragColor = vec4(vColor + 0.2 * sin(uv.yxx + uTime + vRandom.y * 6.28), 1.0);
    } else {
      float circle = smoothstep(0.5, 0.4, d) * 0.8;
      gl_FragColor = vec4(vColor + 0.2 * sin(uv.yxx + uTime + vRandom.y * 6.28), circle);
    }
  }
`;

const Particles = ({
  particleCount = 200,
  particleSpread = 10,
  speed = 0.05,
  particleColors,
  moveParticlesOnHover = true, 
  particleHoverFactor = 1,
  alphaParticles = true,
  particleBaseSize = 50, 
  sizeRandomness = 1,
  cameraDistance = 20,
  disableRotation = false,
  className
}) => {
  const containerRef = useRef(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  
  // Refs to store WebGL objects
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const programRef = useRef(null);
  const particlesRef = useRef(null);
  const animationFrameIdRef = useRef(null);
  const lastTimeRef = useRef(performance.now());
  const elapsedRef = useRef(0);

  // Effect to set up the scene only once
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const renderer = new Renderer({ depth: false, alpha: true });
    const gl = renderer.gl;
    if (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(gl.canvas);
    gl.clearColor(0, 0, 0, 0); 
    rendererRef.current = renderer;

    const camera = new Camera(gl, { fov: 7 });
    camera.position.set(0, 0, cameraDistance);
    cameraRef.current = camera;

    const resize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.perspective({ aspect: window.innerWidth / window.innerHeight });
    };
    window.addEventListener('resize', resize, false);
    resize(); 

    const handleMouseMove = e => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1; 
      mouseRef.current = { x, y };
    };

    const count = particleCount;
    const positions = new Float32Array(count * 3);
    const randoms = new Float32Array(count * 4);
    const colors = new Float32Array(count * 3);
    const palette = particleColors && particleColors.length > 0 ? particleColors : defaultColors;

    for (let i = 0; i < count; i++) {
        const x = Math.random() * 2 - 1;
        const y = Math.random() * 2 - 1;
        const z = Math.random() * 2 - 1;

        positions.set([x, y, z], i * 3);
        randoms.set([Math.random(), Math.random(), Math.random(), Math.random()], i * 4);
        const col = hexToRgb(palette[Math.floor(Math.random() * palette.length)]);
        colors.set(col, i * 3);
    }

    const geometry = new Geometry(gl, {
        position: { size: 3, data: positions },
        random: { size: 4, data: randoms },
        color: { size: 3, data: colors }
    });

    const program = new Program(gl, {
        vertex,
        fragment,
        uniforms: {
            uTime: { value: 0 },
            uSpread: { value: particleSpread },
            uBaseSize: { value: particleBaseSize },
            uSizeRandomness: { value: sizeRandomness },
            uAlphaParticles: { value: alphaParticles ? 1 : 0 }
        },
        transparent: true,
        depthTest: false
    });
    programRef.current = program;

    const particles = new Mesh(gl, { mode: gl.POINTS, geometry, program });
    particlesRef.current = particles;

    // Animation loop
    const update = (t) => {
        animationFrameIdRef.current = requestAnimationFrame(update);
        
        const delta = t - lastTimeRef.current;
        lastTimeRef.current = t;
        elapsedRef.current += delta * speed;

        program.uniforms.uTime.value = elapsedRef.current * 0.001;

        if (moveParticlesOnHover) {
            particles.position.x = -mouseRef.current.x * particleHoverFactor;
            particles.position.y = -mouseRef.current.y * particleHoverFactor;
        } else {
            particles.position.x = 0;
            particles.position.y = 0;
        }

        // --- ROTATION CODE REMOVED ---

        renderer.render({ scene: particles, camera });
    };

    animationFrameIdRef.current = requestAnimationFrame(update);

    // Cleanup
    return () => {
        window.removeEventListener('resize', resize);
        if (moveParticlesOnHover) {
             window.removeEventListener('mousemove', handleMouseMove);
        }
        cancelAnimationFrame(animationFrameIdRef.current);
        if (container && gl.canvas && container.contains(gl.canvas)) {
            container.removeChild(gl.canvas);
        }
    };
  }, []); // Empty dependency array ensures this runs only once on mount

  // Effect to handle mouse move listener
  useEffect(() => {
    const handleMouseMove = e => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1; 
      mouseRef.current = { x, y };
    };

    if (moveParticlesOnHover) {
      window.addEventListener('mousemove', handleMouseMove);
    } else {
      window.removeEventListener('mousemove', handleMouseMove);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [moveParticlesOnHover]);

  // Effect to update colors dynamically
  useEffect(() => {
    if (!particlesRef.current || !particleColors) return;

    const count = particleCount;
    const colors = new Float32Array(count * 3);
    const palette = particleColors.length > 0 ? particleColors : defaultColors;

    for (let i = 0; i < count; i++) {
      const col = hexToRgb(palette[Math.floor(Math.random() * palette.length)]);
      colors.set(col, i * 3);
    }

    // Update the geometry attribute directly
    particlesRef.current.geometry.attributes.color.data.set(colors);
    particlesRef.current.geometry.attributes.color.needsUpdate = true;
    
  }, [particleColors, particleCount]); // Re-run only when colors or count change

  // Effects to update uniforms dynamically
  useEffect(() => {
    if (programRef.current) programRef.current.uniforms.uSpread.value = particleSpread;
  }, [particleSpread]);

  useEffect(() => {
    if (programRef.current) programRef.current.uniforms.uBaseSize.value = particleBaseSize;
  }, [particleBaseSize]);

  useEffect(() => {
    if (programRef.current) programRef.current.uniforms.uSizeRandomness.value = sizeRandomness;
  }, [sizeRandomness]);
  
  useEffect(() => {
    if (programRef.current) programRef.current.uniforms.uAlphaParticles.value = alphaParticles ? 1 : 0;
  }, [alphaParticles]);
  
  useEffect(() => {
    if (cameraRef.current) cameraRef.current.position.z = cameraDistance;
  }, [cameraDistance]);

  return (
    <div
      ref={containerRef}
      className={`particles-container ${className || ''}`} 
      style={{
        position: 'fixed',
        zIndex: -1,
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none'
      }}
    />
  );
};

export default Particles;