/**
 * Simple Language Switcher Component
 * Native HTML dropdown for language selection
 */

import { useLanguage } from '../lib/i18n-hooks'
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '../lib/i18n-simple'

interface LanguageSwitcherProps {
  className?: string
}

export function LanguageSwitcher({ className = '' }: LanguageSwitcherProps) {
  const { language, setLanguage } = useLanguage()

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label htmlFor="language-select" className="text-sm font-medium">
        Language:
      </label>
      <select
        id="language-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
        className="px-3 py-1 border border-gray-300 rounded-md bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => (
          <option key={code} value={code}>
            {info.flag} {info.nativeName}
          </option>
        ))}
      </select>
    </div>
  )
}

// Compact version with just flag buttons
export function CompactLanguageSwitcher({ className = '' }: LanguageSwitcherProps) {
  const { language, setLanguage } = useLanguage()

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
          {info.flag} {code.toUpperCase()}
        </button>
      ))}
    </div>
  )
}

// Language indicator for mobile/small spaces
export function LanguageIndicator({ className = '' }: LanguageSwitcherProps) {
  const { language, languageInfo } = useLanguage()
  
  return (
    <div className={`flex items-center gap-1 text-sm text-gray-600 ${className}`}>
      <span>🌐</span>
      <span>{languageInfo.flag}</span>
      <span className="font-medium">{language.toUpperCase()}</span>
    </div>
  )
}

export default LanguageSwitcher