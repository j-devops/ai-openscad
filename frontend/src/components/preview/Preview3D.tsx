import { Suspense, useRef, useMemo } from 'react'
import { Canvas, useLoader } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader'
import * as THREE from 'three'
import './Preview3D.css'

interface Preview3DProps {
  jobId: string | null
}

function STLModel({ url }: { url: string }) {
  const geometry = useLoader(STLLoader, url)
  const meshRef = useRef<THREE.Mesh>(null)

  // Center and scale the model
  if (geometry) {
    geometry.computeBoundingBox()
    const boundingBox = geometry.boundingBox
    if (boundingBox) {
      const center = new THREE.Vector3()
      boundingBox.getCenter(center)
      geometry.translate(-center.x, -center.y, -center.z)
    }
  }

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial color="#3b82f6" metalness={0.3} roughness={0.4} />
    </mesh>
  )
}

function OpenSCADAxes() {
  const axisLength = 100
  const tickInterval = 10

  // Create simple line geometry for axes
  const createAxisLine = (start: THREE.Vector3, end: THREE.Vector3, color: number) => {
    const points = [start, end]
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    return (
      <line geometry={geometry}>
        <lineBasicMaterial color={color} linewidth={2} />
      </line>
    )
  }

  // Generate tick positions
  const ticks = useMemo(() => {
    const result = []
    for (let i = -axisLength; i <= axisLength; i += tickInterval) {
      if (i !== 0) result.push(i)
    }
    return result
  }, [])

  return (
    <group>
      {/* X Axis - Red */}
      {createAxisLine(
        new THREE.Vector3(-axisLength, 0, 0),
        new THREE.Vector3(axisLength, 0, 0),
        0xff0000
      )}
      {/* X Axis Ticks and Labels */}
      {ticks.map((pos) => (
        <group key={`x-${pos}`}>
          {/* Tick mark */}
          <mesh position={[pos, 0, 0]}>
            <boxGeometry args={[0.3, 1, 0.3]} />
            <meshBasicMaterial color="#ff0000" />
          </mesh>
          {/* Measurement label */}
          <Html position={[pos, -5, 0]} center>
            <div className="scad-tick-label">{pos}</div>
          </Html>
        </group>
      ))}

      {/* Y Axis - Green */}
      {createAxisLine(
        new THREE.Vector3(0, -axisLength, 0),
        new THREE.Vector3(0, axisLength, 0),
        0x00ff00
      )}
      {/* Y Axis Ticks and Labels */}
      {ticks.map((pos) => (
        <group key={`y-${pos}`}>
          <mesh position={[0, pos, 0]}>
            <boxGeometry args={[1, 0.3, 0.3]} />
            <meshBasicMaterial color="#00ff00" />
          </mesh>
          <Html position={[-5, pos, 0]} center>
            <div className="scad-tick-label">{pos}</div>
          </Html>
        </group>
      ))}

      {/* Z Axis - Blue */}
      {createAxisLine(
        new THREE.Vector3(0, 0, -axisLength),
        new THREE.Vector3(0, 0, axisLength),
        0x0000ff
      )}
      {/* Z Axis Ticks and Labels */}
      {ticks.map((pos) => (
        <group key={`z-${pos}`}>
          <mesh position={[0, 0, pos]}>
            <boxGeometry args={[0.3, 0.3, 1]} />
            <meshBasicMaterial color="#0000ff" />
          </mesh>
          <Html position={[0, -5, pos]} center>
            <div className="scad-tick-label">{pos}</div>
          </Html>
        </group>
      ))}

      {/* Axis Labels - OpenSCAD style */}
      <Html position={[axisLength + 10, 0, 0]} center>
        <div className="scad-axis-label scad-axis-x">X</div>
      </Html>
      <Html position={[0, axisLength + 10, 0]} center>
        <div className="scad-axis-label scad-axis-y">Y</div>
      </Html>
      <Html position={[0, 0, axisLength + 10]} center>
        <div className="scad-axis-label scad-axis-z">Z</div>
      </Html>
    </group>
  )
}

function FloorGrid() {
  const size = 200
  const divisions = 20
  const gridHelper = useMemo(() => {
    return new THREE.GridHelper(size, divisions, 0x444444, 0x222222)
  }, [])

  return <primitive object={gridHelper} rotation={[0, 0, 0]} position={[0, -50, 0]} />
}

function Scene({ jobId }: { jobId: string }) {
  const stlUrl = `${import.meta.env.VITE_API_URL}/api/v1/render/${jobId}/download`

  return (
    <>
      {/* Camera positioned like OpenSCAD default view */}
      <PerspectiveCamera makeDefault position={[100, 100, 100]} fov={45} />
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={500}
      />

      {/* Lighting similar to OpenSCAD */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[100, 100, 100]} intensity={0.7} castShadow />
      <directionalLight position={[-100, -100, -100]} intensity={0.3} />

      <Suspense fallback={null}>
        <STLModel url={stlUrl} />
      </Suspense>

      <FloorGrid />
      <OpenSCADAxes />

      {/* Subtle fog for depth */}
      <fog attach="fog" args={['#1a1a1a', 200, 400]} />
    </>
  )
}

export default function Preview3D({ jobId }: Preview3DProps) {
  const handleDownload = () => {
    if (jobId) {
      const downloadUrl = `${import.meta.env.VITE_API_URL}/api/v1/render/${jobId}/download`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `model-${jobId}.stl`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <div className="preview-3d">
      <div className="preview-header">
        <h3>3D Preview</h3>
        {jobId && (
          <button onClick={handleDownload} className="download-button">
            Download STL
          </button>
        )}
      </div>
      <div className="preview-content">
        {jobId ? (
          <Canvas>
            <Scene jobId={jobId} />
          </Canvas>
        ) : (
          <div className="preview-placeholder">
            <p>Click "Render" to generate a preview</p>
            <p className="preview-hint">
              Use mouse to rotate, zoom, and pan the 3D model
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
