'use client'

import PhoneInput from 'react-phone-number-input'
import 'react-phone-number-input/style.css'
import { cn } from '@/lib/utils'

interface PhoneNumberInputProps {
  value: string
  onChange: (value: string | undefined) => void
  disabled?: boolean
  className?: string
}

export function PhoneNumberInput({ value, onChange, disabled, className }: PhoneNumberInputProps) {
  return (
    <PhoneInput
      international
      defaultCountry="CA"
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={cn(
        'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      numberInputProps={{
        className: 'flex-1 bg-transparent outline-none'
      }}
    />
  )
}
