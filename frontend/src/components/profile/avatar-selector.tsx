'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

const AVATARS = Array.from({ length: 20 }, (_, i) => `/avatars/avatar${i + 1}.png`)

interface AvatarSelectorProps {
  onSelect: (avatarUrl: string) => void
  selectedAvatar?: string
  className?: string
  disabled?: boolean
}

export function AvatarSelector({ onSelect, selectedAvatar, className, disabled }: AvatarSelectorProps) {
  const [localSelection, setLocalSelection] = useState(selectedAvatar || '')

  const handleSelect = (avatarUrl: string) => {
    setLocalSelection(avatarUrl)
    onSelect(avatarUrl)
  }

  return (
    <Card className={cn("p-6", className)}>
      <div className="space-y-4">
        <div>
          <h3 className="font-semibold text-lg">Choose an Avatar</h3>
          <p className="text-sm text-muted-foreground">Select from our collection of avatars</p>
        </div>

        <div className="grid grid-cols-4 gap-4 max-h-[400px] overflow-y-auto p-1">
          {AVATARS.map((avatar, index) => (
            <button
              key={index}
              onClick={() => handleSelect(avatar)}
              disabled={disabled}
              className={cn(
                "relative group rounded-lg border-2 p-1 transition-all duration-200",
                localSelection === avatar
                  ? "border-primary ring-2 ring-primary ring-offset-2"
                  : "border-transparent hover:border-primary/30 hover:shadow-md",
                disabled && "opacity-50 cursor-not-allowed"
              )}
            >
              <Avatar className="h-full w-full">
                <AvatarImage src={avatar} alt={`Avatar ${index + 1}`} />
                <AvatarFallback>{index + 1}</AvatarFallback>
              </Avatar>
              
              {localSelection === avatar && (
                <div className="absolute inset-0 flex items-center justify-center bg-primary/20 rounded-lg">
                  <div className="rounded-full bg-primary p-1">
                    <Check className="h-4 w-4 text-primary-foreground" />
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </Card>
  )
}
