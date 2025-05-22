import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense, useLayoutEffect, useRef, useState } from "react";
import { toast, Toaster } from "sonner";

import ModeSelector from "./components/ModeSelector";
import BaseModel from "./components/Model";
import MovableModel from "./components/MovableModel";
import UploadSection from "./components/UploadSection";

import ScaleDialog from "./components/ScaleDialog";
import { Pointer } from "./components/magicui/pointer";
import { ScrollProgress } from "./components/magicui/scroll-progress";
import { ThemeProvider } from "./components/theme-provider";
import { ThemeToggle } from "./components/theme-toggle";
import { Card } from "./components/ui/card";
import { Spinner } from "./components/ui/spinner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function App() {
  const [baseModel, setBaseModel] = useState<{
    url: string | null;
    fileUrl: string | null;
    file: File | null;
  }>({ url: null, fileUrl: null, file: null });
  const [movableModel, setMovableModel] = useState<{
    url: string | null;
    fileName: string | null;
  }>({ url: null, fileName: null });
  const [loading, setLoading] = useState(false);
  const [isAPIReady, setIsAPIReady] = useState(false);
  const [transformMode, setTransformMode] = useState<
    "translate" | "rotate" | "scale"
  >("translate");

  // Reference for the OrbitControls, which allows us to control the camera
  const orbitRef = useRef(null);
  // References for the input elements to handle file uploads
  const movableInputRef = useRef<HTMLInputElement | null>(null);
  const baseInputRef = useRef<HTMLInputElement | null>(null);


  // Get the theme from localStorage or default to "system"
  const theme = localStorage.getItem("vite-ui-theme") || "system";

  /**
   ***********************************************
   ************** Scale Dialog *******************
   ***********************************************
   */
  const [scaleDialog, setScaleDialog] = useState<{
    open: boolean;
    imageUrl: string | null;
    handlerRef: React.RefObject<(p1: any, p2: any, d: number) => void>;
  }>({
    open: false,
    imageUrl: null,
    handlerRef: useRef(() => { }),
  });

  const setScaleDialogHandler = (fn: (p1: any, p2: any, d: number) => void) => {
    scaleDialog.handlerRef.current = fn;
  };

  // Check if the backend API is ready on initial load
  useLayoutEffect(() => {
    const checkAPIStatus = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/`);
        setIsAPIReady(res.status === 200);
      } catch (err) {
        console.error("Erreur API:", err);
        setIsAPIReady(false);
      }
    };
    checkAPIStatus();
  }, []);

  // Function to select scale points and return a promise
  const selectScale = (
    imageUrl: string
  ): Promise<{
    point1: { x: number; y: number };
    point2: { x: number; y: number };
    realDistance: number;
  }> => {
    return new Promise((resolve) => {
      setScaleDialog((prev) => ({ ...prev, open: true, imageUrl: imageUrl }));
      setScaleDialogHandler((p1, p2, dist) =>
        resolve({ point1: p1, point2: p2, realDistance: dist })
      );
    });
  };

  // Function to reset the base model state
  const resetBaseModel = () => {
    setBaseModel((prev) => ({ ...prev, url: null }));
    if (baseInputRef.current) baseInputRef.current.value = "";
  };

  const resetScaleDialog = () => {
    setScaleDialog((prev) => ({ ...prev, open: false, imageUrl: null }));
    setScaleDialogHandler(() => () => { });
  };

  // Function to upload the base model (floor plan)
  const baseModelUpload = async (formData: FormData) => {
    try {
      const uploadResponse = await fetch(`${BACKEND_URL}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error("Erreur lors de l'upload du modèle 3D !");
      }

      const blob = await uploadResponse.blob();
      const objectUrl = URL.createObjectURL(
        new Blob([blob], { type: "application/octet-stream" })
      );

      setBaseModel((prev) => ({ ...prev, url: objectUrl }));
      toast.success("Modèle 3D du fond de plan généré avec succès !");
    } catch (err) {
      console.error("Erreur upload base:", err);
      toast.error("Erreur lors de l'upload du modèle 3D !");
      resetBaseModel();
      resetScaleDialog();
    } finally {
      setLoading(false);
    }
  };

  // Function to verify if the uploaded file is a valid floor plan
  const verifyFloorPlan = async (file: File): Promise<boolean> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BACKEND_URL}/predict/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Erreur lors de la vérification du fond de plan !");
    }

    const data = await response.json();
    return data.class === "floor plan";
  };

  // Function to handle the upload of the base model (floor plan)
  const handleBaseUpload = async (file: File) => {
    setLoading(true);
    const imageUrl = URL.createObjectURL(file);
    setBaseModel((prev) => ({ ...prev, file, fileUrl: imageUrl }));

    try {
      const isFloorPlan = await verifyFloorPlan(file);
      if (!isFloorPlan)
        throw new Error("L'image n'est pas un fond de plan valide !");
      toast.info("L'image est un fond de plan valide !");
      const { point1, point2, realDistance } = await selectScale(imageUrl);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("point1", `${point1.x},${point1.y}`);
      formData.append("point2", `${point2.x},${point2.y}`);
      formData.append("real_distance_m", `${realDistance}`);
      await baseModelUpload(formData);
    } catch (err: any) {
      console.error("Erreur handleBaseUpload:", err);
      toast.error(err.message || "Une erreur est survenue lors du traitement.");
      resetBaseModel();
      resetScaleDialog();
      setLoading(false);
    }
  };

  // Function to handle the upload of a movable model (GLB or OBJ)
  const handleMovableUpload = (file: File) => {
    const objectUrl = URL.createObjectURL(file);
    setMovableModel({ fileName: file.name, url: objectUrl });
  };

  // Function to clear the movable model state
  const clearMovableModel = () => {
    setMovableModel({ url: null, fileName: null });
    if (movableInputRef.current) movableInputRef.current.value = "";
    toast.success("Modèle 3D supprimé avec succès !");
  };

  /**
   **********************************************
   ************** Main application **************
   **********************************************
   */
  return (
    <ThemeProvider defaultTheme={"system"} storageKey="vite-ui-theme">
      <ScrollProgress />
      <div className="p-5">
        {isAPIReady ? (
          <>
            {/* Display the scale dialog if it's open */}
            {scaleDialog.open && scaleDialog.imageUrl && (
              <ScaleDialog
                open={scaleDialog.open}
                imageUrl={scaleDialog.imageUrl}
                onClose={() => {
                  // clear the input value of the base model and close the dialog
                  if (baseInputRef.current) baseInputRef.current.value = "";
                  setScaleDialog((prev) => ({
                    ...prev,
                    open: false,
                  }));

                  // Reset loading state
                  setLoading(false);

                  // Show a toast notification
                  // toast.info("Dialogue de mise à l'échelle fermé.");
                }}
                onConfirm={(p1, p2, realDist) =>
                  scaleDialog.handlerRef.current(p1, p2, realDist)
                }
                setShowScaleDialog={(show: boolean) =>
                  setScaleDialog((prev) => ({ ...prev, open: show }))
                }
              />
            )}
            {/* Main application card with upload sections and mode selector */}
            <Card className="flex flex-row p-4 max-w-full max-h-fit items-center relative ">
              {/* Display the theme toggle button */}
              <div className="absolute top-4 right-4">
                <ThemeToggle />
              </div>

              {/* Display the upload sections for base and movable models */}
              <div className="flex flex-col gap-4">
                <h1 className="text-3xl font-bold">Manipulation 3D</h1>

                {/* Upload sections for base model */}
                <UploadSection
                  label="Importer le fond de plan :"
                  accept="image/*"
                  inputRef={baseInputRef as React.RefObject<HTMLInputElement>}
                  fileUrl={baseModel.url}
                  onUpload={handleBaseUpload}
                  onClear={() => {
                    // Clear the base model state and input value
                    resetBaseModel();
                    resetScaleDialog();

                    toast.success(
                      "Modèle 3D du Fond de plan supprimé avec succès !"
                    );
                  }}
                  onScaleRedefine={async () => {
                    setLoading(true);
                    setScaleDialog((prev) => ({
                      ...prev,
                      open: true,
                      imageUrl: baseModel.fileUrl,
                    }));
                    const { point1, point2, realDistance } = await selectScale(
                      scaleDialog.imageUrl!
                    );
                    const formData = new FormData();
                    formData.append("file", baseModel.file!);
                    formData.append("point1", `${point1.x},${point1.y}`);
                    formData.append("point2", `${point2.x},${point2.y}`);
                    formData.append("real_distance_m", `${realDistance}`);
                    toast.success(
                      "Echelle redéfinie avec succès ! Génération en cours..."
                    );
                    resetBaseModel();
                    await baseModelUpload(formData);
                    setLoading(false);
                  }}
                />

                {/* Upload sections for movable model */}
                <UploadSection
                  label="Importer un objet 3D (GLB ou OBJ) :"
                  accept=".glb,.obj"
                  inputRef={
                    movableInputRef as React.RefObject<HTMLInputElement>
                  }
                  fileUrl={movableModel.url}
                  onUpload={handleMovableUpload}
                  onClear={clearMovableModel}
                />

                {/* Mode selector is only shown if a movable model is uploaded */}
                {/* Buttons to toggle movable model modes (movement, rotation) */}
                {movableModel.url && (
                  <ModeSelector
                    mode={transformMode}
                    onChange={setTransformMode}
                  />
                )}
              </div>

              {/*  Display the image of the base model if it exists */}
              {baseModel.url && (
                <div className="flex justify-center items-center lg:w-52 lg:h-52 lg:ml-20 overflow-auto">
                  <img
                    src={scaleDialog.imageUrl || ""}
                    className="rounded-lg border w-full h-full"
                  ></img>
                </div>
              )}
            </Card>

            {/* 3D Canvas with the base model and movable model */}
            <Card className="flex flex-col mt-4 relative py-0 gap-0">
              {loading && (
                <div className="absolute top-4 right-4">
                  <Spinner size="large" />
                </div>
              )}

              <Canvas
                style={{ height: "600px" }}
                camera={{ position: [10, 10, 10], fov: 50 }}
              >
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 10, 5]} intensity={3.5} />
                <directionalLight position={[-5, -10, -5]} intensity={3.5} />
                <gridHelper args={[100, 100]} />
                <Suspense fallback={null}>
                  {baseModel.url && (
                    <BaseModel
                      url={baseModel.url}
                      position={[0, 0, 0]}
                    />
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

        {/* Toast notifications for success, error, and info messages */}
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
