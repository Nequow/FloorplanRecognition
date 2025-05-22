import { TransformControls } from "@react-three/drei";
import { useLoader } from "@react-three/fiber";
import { useEffect, useRef } from "react";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";

interface MovableModelProps {
  url: string;
  filename: string | null;
  orbitRef: React.RefObject<any>;
  mode: "translate" | "rotate" | "scale";
}

export default function MovableModel({
  url,
  filename,
  orbitRef,
  mode,
}: MovableModelProps) {
  const isGLB = filename!.toLowerCase().endsWith(".glb");
  const isOBJ = filename!.toLowerCase().endsWith(".obj");

  const gltf = isGLB ? useLoader(GLTFLoader, url) : null;
  const obj = isOBJ ? useLoader(OBJLoader, url) : null;

  const transformRef = useRef<any | null>(null);

  const model = isGLB ? gltf?.scene : isOBJ ? obj : null;
  if (!model) return null;

  useEffect(() => {
    const controls = transformRef.current;
    if (!controls || !orbitRef?.current) return;

    const callback = (event: any) => {
      orbitRef.current.enabled = !event.value;
    };

    controls.addEventListener("dragging-changed", callback);
    return () => controls.removeEventListener("dragging-changed", callback);
  }, [orbitRef]);


  return (
    <TransformControls
      ref={transformRef}
      mode={mode}
    >
      <primitive object={model} />
    </TransformControls>
  );
}
