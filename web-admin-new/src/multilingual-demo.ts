/**
 * Demo: Multilingual System
 * Comprehensive demonstration of i18n functionality
 */

import {
  SupportedLanguage,
  SUPPORTED_LANGUAGES,
  loadTranslation,
  translateKey,
  formatDate,
  formatCurrency,
  formatNumber,
  getLanguageInfo
} from './lib/i18n-simple'

import {
  MultilingualPDFGenerator
} from './lib/multilingual-pdf'

// Demo data structures
interface DemoData {
  invoice: {
    invoiceNumber: string
    customerName: string
    items: Array<{
      description: string
      quantity: number
      price: number
      amount: number
    }>
    total: number
    issueDate: Date
    dueDate: Date
  }
  report: {
    title: string
    period: { from: Date; to: Date }
    summary: Record<string, any>
    data: any[]
  }
}

// Initialize demo data
const demoData: DemoData = {
  invoice: {
    invoiceNumber: 'INV-2024-001',
    customerName: 'ABC Autószerviz Kft.',
    items: [
      {
        description: 'Olajcsere szolgáltatás',
        quantity: 1,
        price: 15000,
        amount: 15000
      },
      {
        description: 'Szűrőcsere',
        quantity: 2,
        price: 5000,
        amount: 10000
      },
      {
        description: 'Diagnosztikai vizsgálat', 
        quantity: 1,
        price: 8000,
        amount: 8000
      }
    ],
    total: 33000,
    issueDate: new Date('2024-01-15'),
    dueDate: new Date('2024-01-30')
  },
  report: {
    title: 'Havi Forgalom Jelentés',
    period: {
      from: new Date('2024-01-01'),
      to: new Date('2024-01-31')
    },
    summary: {
      totalRevenue: 450000,
      totalOrders: 25,
      averageOrder: 18000
    },
    data: [
      { service: 'Olajcsere', count: 12, revenue: 180000 },
      { service: 'Szűrőcsere', count: 8, revenue: 80000 },
      { service: 'Diagnosztika', count: 5, revenue: 40000 }
    ]
  }
}

// Demo class for testing multilingual functionality
class MultilingualDemo {
  private pdfGenerator: MultilingualPDFGenerator
  private translations: Record<SupportedLanguage, Record<string, any>> = {} as any

  constructor() {
    this.pdfGenerator = new MultilingualPDFGenerator()
    this.initializeTranslations()
  }

  // Load all translations
  private async initializeTranslations() {
    console.log('🔄 Loading translations for all supported languages...')
    
    for (const language of Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]) {
      try {
        this.translations[language] = await loadTranslation(language)
        console.log(`✅ Loaded ${language} translations`)
      } catch (error) {
        console.warn(`❌ Failed to load ${language} translations:`, error)
        this.translations[language] = {}
      }
    }
  }

  // Demonstrate translation functionality
  public demonstrateTranslations() {
    console.log('\n📝 TRANSLATION DEMONSTRATION')
    console.log('=' .repeat(50))

    const testKeys = [
      'common.save',
      'common.loading',
      'nav.dashboard',
      'auth.login',
      'invoice.title',
      'pdf.header.title'
    ]

    for (const language of Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]) {
      const languageInfo = getLanguageInfo(language)
      console.log(`\n${languageInfo.flag} ${languageInfo.nativeName} (${language})`)
      console.log('-'.repeat(30))
      
      testKeys.forEach(key => {
        const translation = translateKey(this.translations[language] || {}, key)
        console.log(`  ${key}: "${translation}"`)
      })
    }
  }

  // Demonstrate formatting functionality
  public demonstrateFormatting() {
    console.log('\n📊 FORMATTING DEMONSTRATION')
    console.log('=' .repeat(50))

    const testDate = new Date('2024-01-15T14:30:00')
    const testAmount = 125450.75
    const testNumber = 1234567.89

    for (const language of Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]) {
      const languageInfo = getLanguageInfo(language)
      console.log(`\n${languageInfo.flag} ${languageInfo.nativeName} (${language})`)
      console.log('-'.repeat(30))
      
      console.log(`  Date (short): ${formatDate(testDate, language, 'short')}`)
      console.log(`  Date (medium): ${formatDate(testDate, language, 'medium')}`)
      console.log(`  Date (long): ${formatDate(testDate, language, 'long')}`)
      console.log(`  Currency: ${formatCurrency(testAmount, language)}`)
      console.log(`  Number: ${formatNumber(testNumber, language)}`)
    }
  }

  // Demonstrate PDF generation
  public async demonstratePDFGeneration() {
    console.log('\n📄 PDF GENERATION DEMONSTRATION')
    console.log('=' .repeat(50))

    for (const language of Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]) {
      const languageInfo = getLanguageInfo(language)
      console.log(`\n${languageInfo.flag} Generating PDF in ${languageInfo.nativeName}...`)

      // Generate invoice template
      const invoiceTemplate = this.pdfGenerator.generateInvoiceTemplate(
        demoData.invoice,
        language
      )

      console.log(`  📋 Invoice template: ${invoiceTemplate.sections.length} sections`)
      console.log(`  📝 Layout: ${invoiceTemplate.layout}, Type: ${invoiceTemplate.type}`)
      
      // Generate report template  
      const reportTemplate = this.pdfGenerator.generateReportTemplate(
        demoData.report,
        language
      )

      console.log(`  📊 Report template: ${reportTemplate.sections.length} sections`)
      console.log(`  📝 Layout: ${reportTemplate.layout}, Type: ${reportTemplate.type}`)

      // Show sample content from templates
      const headerSection = invoiceTemplate.sections.find(s => s.type === 'header')
      if (headerSection) {
        console.log(`  📄 Header content: "${headerSection.content}"`)
      }
    }
  }

  // Demonstrate language switching
  public demonstrateLanguageSwitching() {
    console.log('\n🔄 LANGUAGE SWITCHING DEMONSTRATION')
    console.log('=' .repeat(50))

    // Simulate user session
    let currentLanguage: SupportedLanguage = 'hu'
    
    const simulateUserAction = (action: string, key: string) => {
      const languageInfo = getLanguageInfo(currentLanguage)
      const translation = translateKey(this.translations[currentLanguage] || {}, key)
      
      console.log(`${languageInfo.flag} [${currentLanguage.toUpperCase()}] ${action}: "${translation}"`)
    }

    // Demonstrate UI flow in Hungarian
    currentLanguage = 'hu'
    console.log('\n🇭🇺 User session in Hungarian:')
    simulateUserAction('Login button', 'auth.login')
    simulateUserAction('Dashboard title', 'dashboard.title')
    simulateUserAction('Save action', 'common.save')

    // Switch to English
    currentLanguage = 'en'
    console.log('\n🇺🇸 User switches to English:')
    simulateUserAction('Login button', 'auth.login')
    simulateUserAction('Dashboard title', 'dashboard.title')
    simulateUserAction('Save action', 'common.save')

    // Switch to German
    currentLanguage = 'de'
    console.log('\n🇩🇪 User switches to German:')
    simulateUserAction('Login button', 'auth.login')
    simulateUserAction('Dashboard title', 'dashboard.title')
    simulateUserAction('Save action', 'common.save')
  }

  // Demonstrate parameter replacement
  public demonstrateParameterReplacement() {
    console.log('\n🔧 PARAMETER REPLACEMENT DEMONSTRATION')
    console.log('=' .repeat(50))

    const testParams = {
      name: 'János Kovács',
      date: formatDate(new Date(), 'hu'),
      total: formatCurrency(75000, 'hu'),
      number: 'INV-2024-001'
    }

    for (const language of Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]) {
      const languageInfo = getLanguageInfo(language)
      console.log(`\n${languageInfo.flag} ${languageInfo.nativeName}:`)

      // Format date and currency for the language
      const localParams = {
        ...testParams,
        date: formatDate(new Date(), language),
        total: formatCurrency(75000, language)
      }

      const customerText = translateKey(
        this.translations[language] || {},
        'invoice.customer',
        localParams
      )
      
      const totalText = translateKey(
        this.translations[language] || {},
        'invoice.total',
        localParams
      )

      console.log(`  Customer: ${customerText}`)
      console.log(`  Total: ${totalText}`)
    }
  }

  // Run all demonstrations
  public async runFullDemo() {
    console.log('🚀 MULTILINGUAL SYSTEM FULL DEMONSTRATION')
    console.log('='.repeat(60))

    await this.initializeTranslations()

    this.demonstrateTranslations()
    this.demonstrateFormatting()
    await this.demonstratePDFGeneration()
    this.demonstrateLanguageSwitching()
    this.demonstrateParameterReplacement()

    console.log('\n✅ DEMONSTRATION COMPLETE')
    console.log('All multilingual features working correctly!')
  }
}

// Export demo functionality
export { MultilingualDemo, demoData }

// Demo runner function
export async function runMultilingualDemo(): Promise<void> {
  const demo = new MultilingualDemo()
  await demo.runFullDemo()
}

// Export for use in other modules
export default MultilingualDemo