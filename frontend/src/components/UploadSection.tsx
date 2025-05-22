import { Download, Scaling, Trash2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface UploadSectionProps {
  label: string;
  accept: string;
  fileUrl: string | null;
  inputRef: React.RefObject<HTMLInputElement> | null;
  onUpload: (file: File) => void;
  onClear: () => void;
  onScaleRedefine?: () => void;
}

export default function UploadSection({
  label,
  accept,
  inputRef,
  fileUrl,
  onUpload,
  onClear,
  onScaleRedefine,
}: UploadSectionProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
  };

  return (
    <div className="grid w-full items-center gap-1.5">
      <Label className="font-light">{label}</Label>

      <div className="flex gap-2 items-center">
        {fileUrl ? (
          <div className="flex flex-wrap gap-2">
            <Input
              disabled
              className="font-light w-[320px]"
              placeholder={fileUrl.slice(fileUrl.length - 36, fileUrl.length)}
            />
            <Button
              className="cursor-pointer"
              variant="destructive"
              onClick={onClear}
            >
              <Trash2 />
              Supprimer
            </Button>
            {/* only for floor plans images (base model) */}
            {accept === "image/*" && (
              <>
                <Button
                  className="cursor-pointer"
                  variant="outline"
                  onClick={() => {
                    // telecharger le fichier
                    if (fileUrl) {
                      const link = document.createElement("a");
                      link.href = fileUrl;
                      link.download =
                        fileUrl.split("/").pop() + ".glb" || "download";
                      link.click();
                    }
                  }}
                >
                  <Download />
                  Télécharger
                </Button>
                <Button
                  className="cursor-pointer"
                  variant="outline"
                  onClick={onScaleRedefine}
                >
                  <Scaling />
                  Redéfinir l'échelle
                </Button>
              </>
            )}
          </div>
        ) : (
          <Input
            className="font-light max-w-[320px] text-primary hover:bg-primary/10 cursor-pointer"
            type="file"
            accept={accept}
            onChange={handleChange}
            ref={inputRef}
          />
        )}
      </div>
    </div>
  );
}
