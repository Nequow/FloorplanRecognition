import { Move3D, Rotate3D, Scale3D } from "lucide-react";
import { Button } from "./ui/button";

interface ModeSelectorProps {
  mode: "translate" | "rotate" | "scale";
  onChange: (mode: "translate" | "rotate" | "scale") => void;
}

export default function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="flex gap-2">
      {["translate", "rotate", "scale"].map((m) => (
        <Button
          key={m}
          variant={mode === m ? "default" : "outline"}
          onClick={() => onChange(m as any)}
        >
          {m === "translate" ? (
            <>
              <Move3D /> Déplacer
            </>
          ) : m === "rotate" ? (
            <>
              <Rotate3D /> Tourner
            </>
          ) : (
            <>
              <Scale3D /> Redimensioner
            </>
          )}
        </Button>
      ))}
    </div>
  );
}
