/**
 * Language Switcher Component
 * Provides language selection functionality with proper UI
 */

import { useState } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Check, Globe, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { 
  useLanguage, 
  SUPPORTED_LANGUAGES, 
  SupportedLanguage,
  getLanguageInfo 
} from '@/lib/i18n'

interface LanguageSwitcherProps {
  variant?: 'select' | 'dropdown' | 'compact'
  showFlag?: boolean
  showNativeName?: boolean
  className?: string
}

export function LanguageSwitcher({
  variant = 'dropdown',
  showFlag = true,
  showNativeName = true,
  className
}: LanguageSwitcherProps) {
  const { language, setLanguage } = useLanguage()

  if (variant === 'select') {
    return (
      <Select value={language} onValueChange={(value: SupportedLanguage) => setLanguage(value)}>
        <SelectTrigger className={cn("w-[180px]", className)}>
          <SelectValue>
            <div className="flex items-center gap-2">
              {showFlag && <span>{getLanguageInfo(language).flag}</span>}
              <span>{showNativeName ? getLanguageInfo(language).nativeName : getLanguageInfo(language).name}</span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
            <SelectItem key={code} value={code}>
              <div className="flex items-center gap-2">
                {showFlag && <span>{info.flag}</span>}
                <span>{showNativeName ? info.nativeName : info.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={cn("flex items-center gap-1", className)}>
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <Button
            key={code}
            variant={language === code ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setLanguage(code as SupportedLanguage)}
            className="h-8 w-8 p-0"
            title={info.nativeName}
          >
            {showFlag ? info.flag : code.toUpperCase()}
          </Button>
        ))}
      </div>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className={cn("gap-2", className)}>
          <Globe className="h-4 w-4" />
          {showFlag && <span>{getLanguageInfo(language).flag}</span>}
          <span className="hidden sm:inline">
            {showNativeName ? getLanguageInfo(language).nativeName : getLanguageInfo(language).name}
          </span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <DropdownMenuItem
            key={code}
            onClick={() => setLanguage(code as SupportedLanguage)}
            className="gap-2"
          >
            {showFlag && <span>{info.flag}</span>}
            <span>{showNativeName ? info.nativeName : info.name}</span>
            {language === code && <Check className="h-4 w-4 ml-auto" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// Compact language indicator for mobile/small spaces
export function LanguageIndicator({ className }: { className?: string }) {
  const { language } = useLanguage()
  const info = getLanguageInfo(language)
  
  return (
    <div className={cn("flex items-center gap-1 text-sm text-muted-foreground", className)}>
      <Globe className="h-3 w-3" />
      <span>{info.flag}</span>
      <span className="font-medium">{info.code.toUpperCase()}</span>
    </div>
  )
}

// Language settings component for user preferences
export function LanguageSettings({ className }: { className?: string }) {
  const { language, setLanguage } = useLanguage()

  return (
    <div className={cn("space-y-4", className)}>
      <div>
        <h3 className="text-lg font-medium">Language / Nyelv / Sprache</h3>
        <p className="text-sm text-muted-foreground">
          Select your preferred language for the interface
        </p>
      </div>
      
      <div className="grid gap-3">
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <div
            key={code}
            className={cn(
              "flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors",
              language === code ? "border-primary bg-primary/5" : "hover:bg-muted/50"
            )}
            onClick={() => setLanguage(code as SupportedLanguage)}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{info.flag}</span>
              <div>
                <div className="font-medium">{info.nativeName}</div>
                <div className="text-sm text-muted-foreground">{info.name}</div>
              </div>
            </div>
            {language === code && (
              <Check className="h-4 w-4 ml-auto text-primary" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default LanguageSwitcher