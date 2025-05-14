import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AlertDialogDescription } from "@radix-ui/react-alert-dialog";
import { useEffect, useRef, useState } from "react";

interface Point {
  x: number;
  y: number;
}

export default function ScaleDialog({
  open,
  onClose,
  onConfirm,
  imageUrl,
  setShowScaleDialog,
}: {
  open: boolean;
  onClose: () => void;
  onConfirm: (p1: Point, p2: Point, realDistance: number) => void;
  imageUrl: string;
  setShowScaleDialog: (show: boolean) => void;
}) {
  const [points, setPoints] = useState<Point[]>([]);
  const [realDistance, setRealDistance] = useState("");

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [_, setScale] = useState<{ x: number; y: number }>({ x: 1, y: 1 });

  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    const img = imgRef.current;
    if (!img) return;

    const rect = img.getBoundingClientRect();
    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    if (points.length < 2) {
      setPoints([...points, { x, y }]);
    } else {
      setPoints([{ x, y }]); // reset with new first point
    }
  };

  const handleConfirm = () => {
    if (points.length === 2 && realDistance) {
      onConfirm(points[0], points[1], parseFloat(realDistance));
      setShowScaleDialog(false);
      setPoints([]);
      setRealDistance("");
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const img = imgRef.current;

    if (!canvas || !ctx || !img) return;

    const displayedWidth = img.clientWidth;
    const displayedHeight = img.clientHeight;

    canvas.width = displayedWidth;
    canvas.height = displayedHeight;

    const scaleX = displayedWidth / img.naturalWidth;
    const scaleY = displayedHeight / img.naturalHeight;
    setScale({ x: scaleX, y: scaleY });

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const displayPoints = points.map((pt) => ({
      x: pt.x * scaleX,
      y: pt.y * scaleY,
    }));

    // Dessiner les points rouges
    displayPoints.forEach((pt) => {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 5, 0, 2 * Math.PI);
      ctx.fillStyle = "red";
      ctx.fill();
    });

    // Dessiner la ligne bleue
    if (displayPoints.length === 2) {
      ctx.beginPath();
      ctx.moveTo(displayPoints[0].x, displayPoints[0].y);
      ctx.lineTo(displayPoints[1].x, displayPoints[1].y);
      ctx.strokeStyle = "blue";
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }, [points]);

  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Définir l’échelle</AlertDialogTitle>
          <AlertDialogDescription className="text-sm font-light italic">
            Veuillez selectionner 2 points sur l'image pour définir l'échelle.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="relative w-full">
          <img
            ref={imgRef}
            src={imageUrl}
            alt="fond de plan"
            className="w-full h-auto cursor-crosshair border"
            onClick={handleImageClick}
          />
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 pointer-events-none"
          />
        </div>

        <div className="my-2 text-sm">
          Points sélectionnés : {points.length}/2
        </div>

        <Input
          placeholder="Distance réelle (en mètres)"
          type="number"
          step="0.01"
          value={realDistance}
          onChange={(e) => setRealDistance(e.target.value)}
        />

        <AlertDialogFooter className="mt-4 flex gap-2 justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            className="cursor-pointer"
          >
            Annuler
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={points.length !== 2 || !realDistance}
            className="cursor-pointer"
          >
            Valider
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
