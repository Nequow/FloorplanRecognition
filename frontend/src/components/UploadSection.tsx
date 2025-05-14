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
}

export default function UploadSection({
  label,
  accept,
  inputRef,
  fileUrl,
  onUpload,
  onClear,
}: UploadSectionProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
  };

  return (
    <div className="grid w-full max-w-sm items-center gap-1.5">
      <Label className="font-light">{label}</Label>

      <div className="flex gap-2 items-center">
        {fileUrl ? (
          <>
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
              Supprimer
            </Button>
          </>
        ) : (
          <Input
            className="font-light text-primary hover:bg-primary/10 cursor-pointer"
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
