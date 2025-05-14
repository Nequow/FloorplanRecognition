import { useLoader } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

interface ModelProps {
  url: string;
  position?: [number, number, number];
}

export default function Model({ url, position = [0, 0, 0] }: ModelProps) {
  const model = useLoader(GLTFLoader, url);

  return <primitive object={model.scene} position={position} />;
}
