import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import axios from "axios";
import { Suspense, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Toaster, toast } from "sonner";

import ModeSelector from "./components/ModeSelector";
import Model from "./components/Model";
import MovableModel from "./components/MovableModel";
import UploadSection from "./components/UploadSection";

import ScaleDialog from "./components/ScaleDialog";
import { Pointer } from "./components/magicui/pointer";
import { ModeToggle } from "./components/mode-toggle";
import { ThemeProvider } from "./components/theme-provider";
import { Card } from "./components/ui/card";
import { Spinner } from "./components/ui/spinner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function App() {
  const [baseModelUrl, setBaseModelUrl] = useState<string | null>(null);
  const [movableModel, setMovableModel] = useState<{
    url: string | null;
    fileName: string | null;
  }>({ url: null, fileName: null });
  const [loading, setLoading] = useState(false);
  const [isAPIReady, setIsAPIReady] = useState(false);
  const [transformMode, setTransformMode] = useState<
    "translate" | "rotate" | "scale"
  >("translate");

  const orbitRef = useRef(null);
  const movableInputRef = useRef<HTMLInputElement | null>(null);
  const baseInputRef = useRef<HTMLInputElement | null>(null);

  const theme = localStorage.getItem("vite-ui-theme") || "system";

  const [showScaleDialog, setShowScaleDialog] = useState(false);
  const [scaleDialogImage, setScaleDialogImage] = useState<string | null>(null);

  const scaleDialogHandlerRef = useRef<(p1: any, p2: any, d: number) => void>(
    () => {}
  );
  const setScaleDialogHandler = (fn: (p1: any, p2: any, d: number) => void) => {
    scaleDialogHandlerRef.current = fn;
  };

  useLayoutEffect(() => {
    const checkAPIStatus = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/`);
        setIsAPIReady(res.status === 200);
      } catch (err) {
        console.error("Erreur API:", err);
        setIsAPIReady(false);
      }
    };
    checkAPIStatus();
  }, []);

  const selectScale = (
    imageUrl: string
  ): Promise<{
    point1: { x: number; y: number };
    point2: { x: number; y: number };
    realDistance: number;
  }> => {
    return new Promise((resolve) => {
      setShowScaleDialog(true);
      setScaleDialogImage(imageUrl);
      setScaleDialogHandler((p1, p2, dist) =>
        resolve({ point1: p1, point2: p2, realDistance: dist })
      );
    });
  };

  const handleBaseUpload = async (file: File) => {
    setLoading(true);

    const imageUrl = URL.createObjectURL(file);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${BACKEND_URL}/predict/`, formData);

      if (response.data.class === "floor plan") {
        toast.success("L'image est un fond de plan valide !");
      } else {
        throw new Error("L'image n'est pas un fond de plan valide !");
      }

      const { point1, point2, realDistance } = await selectScale(imageUrl);

      formData.append("point1", `${point1.x},${point1.y}`);
      formData.append("point2", `${point2.x},${point2.y}`);
      formData.append("real_distance_m", `${realDistance}`);

      try {
        const uploadResponse = await axios.post(
          `${BACKEND_URL}/upload/`,
          formData,
          {
            responseType: "blob",
          }
        );
        const objectUrl = URL.createObjectURL(
          new Blob([uploadResponse.data], { type: "application/octet-stream" })
        );
        setBaseModelUrl(objectUrl);
        toast.success("Modèle 3D du fond de plan généré avec succès !");
      } catch (err) {
        console.error("Erreur upload base:", err);
        toast.error("Erreur lors de l'upload du modèle 3D !");
        setBaseModelUrl(null);
        if (baseInputRef.current) baseInputRef.current.value = "";
      } finally {
        setLoading(false);
      }
    } catch (err) {
      console.error("Erreur upload base:", err);
      toast.error("L'image n'est pas un fond de plan valide !");
      setLoading(false);
      if (baseInputRef.current) baseInputRef.current.value = "";
      setBaseModelUrl(null);
    }
  };

  const handleMovableUpload = (file: File) => {
    const objectUrl = URL.createObjectURL(file);
    setMovableModel({ fileName: file.name, url: objectUrl });
  };

  useEffect(() => {}, [localStorage.getItem("vite-ui-theme")]);
  return (
    <ThemeProvider defaultTheme={"system"} storageKey="vite-ui-theme">
      <div className="p-5">
        {isAPIReady ? (
          <>
            {showScaleDialog && scaleDialogImage && (
              <ScaleDialog
                open={showScaleDialog}
                imageUrl={scaleDialogImage}
                onClose={() => {
                  setShowScaleDialog(false);
                  setScaleDialogImage(null);
                  setScaleDialogHandler(() => () => {});
                  setBaseModelUrl(null);
                  if (baseInputRef.current) baseInputRef.current.value = "";
                  setLoading(false);
                }}
                onConfirm={(p1, p2, realDist) =>
                  scaleDialogHandlerRef.current(p1, p2, realDist)
                }
                setShowScaleDialog={setShowScaleDialog}
              />
            )}
            <Card className="flex flex-row p-4 max-w-full max-h-62 items-center relative">
              <div className="absolute top-4 right-4">
                <ModeToggle />
              </div>

              <div className="flex flex-col gap-4">
                <h1 className="text-3xl font-bold">Manipulation 3D</h1>

                <UploadSection
                  label="Importer le fond de plan :"
                  accept="image/*"
                  inputRef={baseInputRef as React.RefObject<HTMLInputElement>}
                  fileUrl={baseModelUrl}
                  onUpload={handleBaseUpload}
                  onClear={() => {
                    setBaseModelUrl(null);
                    if (baseInputRef.current) baseInputRef.current.value = "";
                    toast.success(
                      "Modèle 3D du Fond de plan supprimé avec succès !"
                    );
                    setScaleDialogImage(null);
                  }}
                />

                <UploadSection
                  label="Importer un objet 3D (GLB ou OBJ) :"
                  accept=".glb,.obj"
                  inputRef={
                    movableInputRef as React.RefObject<HTMLInputElement>
                  }
                  fileUrl={movableModel.url}
                  onUpload={handleMovableUpload}
                  onClear={() => {
                    setMovableModel({ url: null, fileName: null });
                    if (movableInputRef.current)
                      movableInputRef.current.value = "";
                    toast.success("Modèle 3D supprimé avec succès !");
                  }}
                />

                {movableModel.url && (
                  <ModeSelector
                    mode={transformMode}
                    onChange={setTransformMode}
                  />
                )}
              </div>

              {baseModelUrl && (
                <div>
                  <img
                    src={scaleDialogImage || ""}
                    className="w-52 h-52 ml-20"
                  ></img>
                </div>
              )}
              {/* {loading && <p>Traitement en cours...</p>} */}
            </Card>

            <Card className="flex flex-col mt-4 relative">
              {loading && (
                <div className="absolute top-4 right-4">
                  <Spinner size="large" />
                </div>
              )}

              <Canvas
                camera={{ position: [10, 10, 10], fov: 50 }}
                style={{ height: "600px", marginTop: "20px" }}
              >
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 10, 5]} intensity={3.5} />
                <directionalLight position={[-5, -10, -5]} intensity={3.5} />
                <gridHelper args={[100, 100]} />
                <Suspense fallback={null}>
                  {baseModelUrl && (
                    <Model url={baseModelUrl} position={[0, 0, 0]} />
                  )}
                  {movableModel.url && (
                    <MovableModel
                      url={movableModel.url}
                      filename={movableModel.fileName}
                      orbitRef={orbitRef}
                      mode={transformMode}
                    />
                  )}
                </Suspense>
                <OrbitControls ref={orbitRef} />
              </Canvas>
              <Pointer className="fill-black" />
            </Card>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-screen">
            <Spinner size="large">Loading...</Spinner>
          </div>
        )}

        <Toaster
          key={theme}
          richColors
          closeButton
          theme={theme as "system" | "dark" | "light"}
        />
      </div>
    </ThemeProvider>
  );
}
