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
          {m === "translate"
            ? "Déplacer"
            : m === "rotate"
            ? "Tourner"
            : "Redimensionner"}
        </Button>
      ))}
    </div>
  );
}
