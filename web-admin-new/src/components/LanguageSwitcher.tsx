/**
 * Nyelvváltó komponens - Magyar követelmények alapján
 * Complete Language Switcher with flag icons and native names
 */

import React from 'react'
import { useI18n } from '../lib/i18n-hooks'
import { SupportedLanguage, SUPPORTED_LANGUAGES } from '../lib/i18n-simple'

interface LanguageSwitcherProps {
  className?: string
  variant?: 'dropdown' | 'compact' | 'buttons'
}

export function LanguageSwitcher({ 
  className = '', 
  variant = 'dropdown' 
}: LanguageSwitcherProps) {
  const { language, setLanguage } = useI18n()

  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <button
            key={code}
            onClick={() => setLanguage(code as SupportedLanguage)}
            className={`
              px-2 py-1 text-sm rounded transition-colors
              ${language === code 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }
            `}
            title={info.nativeName}
          >
            {info.flag}
          </button>
        ))}
      </div>
    )
  }

  if (variant === 'buttons') {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <button
            key={code}
            onClick={() => setLanguage(code as SupportedLanguage)}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-lg transition-colors
              ${language === code
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700'
              }
            `}
          >
            <span className="text-lg">{info.flag}</span>
            <span className="text-sm font-medium">{info.nativeName}</span>
          </button>
        ))}
      </div>
    )
  }

  // Default dropdown variant
  return (
    <div className={`relative ${className}`}>
      <label htmlFor="language-select" className="sr-only">
        Nyelv kiválasztása / Language Selection
      </label>
      <select
        id="language-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
        className="
          appearance-none bg-white border border-gray-300 rounded-md 
          px-3 py-2 pr-8 text-sm font-medium
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          cursor-pointer
        "
      >
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <option key={code} value={code}>
            {info.flag} {info.nativeName}
          </option>
        ))}
      </select>
      
      {/* Custom dropdown arrow */}
      <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}

// Language indicator component for headers/footers
export function LanguageIndicator({ className = '' }: { className?: string }) {
  const { language } = useI18n()
  const languageInfo = SUPPORTED_LANGUAGES[language]

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-lg">{languageInfo.flag}</span>
      <span className="text-sm font-medium text-gray-600">
        {languageInfo.nativeName}
      </span>
    </div>
  )
}

export default LanguageSwitcher
