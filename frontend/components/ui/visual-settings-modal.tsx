"use client"

import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Settings2, Ratio, Palette, Camera, Target, X } from "lucide-react"

interface VisualSettingsModalProps {
  aspectRatio: string
  colorPalette: string
  cameraSettings: string
  imagePurpose: string
  onAspectRatioChange: (value: string) => void
  onColorPaletteChange: (value: string) => void
  onCameraSettingsChange: (value: string) => void
  onImagePurposeChange: (value: string) => void
  onApply: () => void
  onClear: () => void
  hasSettings: boolean
  aspectRatioOptions: Array<{ value: string; label: string }>
  colorPaletteOptions: Array<{ value: string; label: string }>
  cameraSettingsOptions: Array<{ value: string; label: string }>
  imagePurposeOptions: Array<{ value: string; label: string }>
}

export function VisualSettingsModal({
  aspectRatio,
  colorPalette,
  cameraSettings,
  imagePurpose,
  onAspectRatioChange,
  onColorPaletteChange,
  onCameraSettingsChange,
  onImagePurposeChange,
  onApply,
  onClear,
  hasSettings,
  aspectRatioOptions,
  colorPaletteOptions,
  cameraSettingsOptions,
  imagePurposeOptions,
}: VisualSettingsModalProps) {
  const [open, setOpen] = useState(false)

  const handleApply = () => {
    onApply()
    setOpen(false)
  }

  const handleClear = () => {
    onClear()
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-9 bg-white border-gray-200 hover:bg-gray-50 text-gray-700 hover:text-gray-900 shadow-sm transition-colors flex items-center gap-2 ${hasSettings ? 'ring-2 ring-blue-500 ring-offset-2' : ''
            }`}
        >
          <Settings2 className={`w-4 h-4 ${hasSettings ? 'text-blue-600' : ''}`} />
          <span className="hidden sm:inline text-xs font-medium">
            Visual Settings {hasSettings && '✓'}
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px] bg-white">
        <DialogHeader>
          <DialogTitle className="text-gray-900 flex items-center gap-2 text-xl">
            <Settings2 className="w-5 h-5 text-blue-600" />
            Visual Settings
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            Customize the visual aspects of your generated image (optional)
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
          {/* Aspect Ratio */}
          <div className="space-y-2">
            <Label htmlFor="aspect-ratio" className="text-sm font-medium text-gray-900 flex items-center gap-2">
              <Ratio className="w-4 h-4 text-gray-500" />
              Aspect Ratio
            </Label>
            <Select value={aspectRatio} onValueChange={onAspectRatioChange}>
              <SelectTrigger id="aspect-ratio" className="w-full bg-white border-gray-200 text-gray-900 hover:text-black hover:bg-gray-50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white border-gray-200 max-h-[300px]">
                {aspectRatioOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-gray-700 hover:bg-gray-50"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Color Palette */}
          <div className="space-y-2">
            <Label htmlFor="color-palette" className="text-sm font-medium text-gray-900 flex items-center gap-2">
              <Palette className="w-4 h-4 text-gray-500" />
              Color & Lighting
            </Label>
            <Select value={colorPalette} onValueChange={onColorPaletteChange}>
              <SelectTrigger id="color-palette" className="w-full bg-white border-gray-200 text-gray-900 hover:text-black hover:bg-gray-50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white border-gray-200 max-h-[300px]">
                {colorPaletteOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-gray-700 hover:bg-gray-50"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Camera Settings */}
          <div className="space-y-2">
            <Label htmlFor="camera-settings" className="text-sm font-medium text-gray-900 flex items-center gap-2">
              <Camera className="w-4 h-4 text-gray-500" />
              Camera & Lens
            </Label>
            <Select value={cameraSettings} onValueChange={onCameraSettingsChange}>
              <SelectTrigger id="camera-settings" className="w-full bg-white border-gray-200 text-gray-900 hover:text-black hover:bg-gray-50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white border-gray-200 max-h-[300px]">
                {cameraSettingsOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-gray-700 hover:bg-gray-50"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Image Purpose */}
          <div className="space-y-2">
            <Label htmlFor="image-purpose" className="text-sm font-medium text-gray-900 flex items-center gap-2">
              <Target className="w-4 h-4 text-gray-500" />
              Image Purpose
            </Label>
            <Select value={imagePurpose} onValueChange={onImagePurposeChange}>
              <SelectTrigger id="image-purpose" className="w-full bg-white border-gray-200 text-gray-900 hover:text-black hover:bg-gray-50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white border-gray-200 max-h-[300px]">
                {imagePurposeOptions.map((option) => (
                  <SelectItem
                    key={option.value}
                    value={option.value}
                    className="text-gray-700 hover:bg-gray-50"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex justify-between items-center gap-3 pt-4 border-t border-gray-200">
          <Button
            variant="outline"
            onClick={handleClear}
            className="border-gray-200 text-red-600 hover:bg-red-50 hover:text-red-700 flex items-center gap-2"
          >
            <X className="w-4 h-4" />
            Clear Settings
          </Button>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              className="border-gray-200 text-gray-900 hover:bg-gray-50 bg-white"
            >
              Cancel
            </Button>
            <Button
              onClick={handleApply}
              className="bg-black hover:bg-gray-800 text-white"
            >
              Apply Settings
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
