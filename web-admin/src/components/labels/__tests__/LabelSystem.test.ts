/**
 * Label Generation System Test
 * 
 * Test the complete label generation workflow:
 * - QR code generation
 * - Various label formats
 * - Print optimization
 * - Browser compatibility
 */

import { QRCodeService } from '@/lib/services/qr-service'
import { LabelService } from '@/lib/services/label-service'
import { 
  LabelFormat, 
  LABEL_FORMATS, 
  GateLabelData, 
  PrintJob 
} from '@/lib/types/labels'

describe('Label Generation System', () => {
  describe('QR Code Service', () => {
    test('generates QR code SVG', async () => {
      const qrSvg = await QRCodeService.generateQRCodeSVG('test-content')
      
      expect(qrSvg).toContain('<svg')
      expect(qrSvg).toContain('</svg>')
      expect(qrSvg).toContain('test-content')
    })

    test('validates QR content', () => {
      const validResult = QRCodeService.validateQRContent('valid-content')
      expect(validResult.valid).toBe(true)
      
      const emptyResult = QRCodeService.validateQRContent('')
      expect(emptyResult.valid).toBe(false)
      
      const tooLongResult = QRCodeService.validateQRContent('x'.repeat(3000))
      expect(tooLongResult.valid).toBe(false)
    })

    test('optimizes QR config for different label sizes', () => {
      const smallConfig = QRCodeService.optimizeQRConfigForSize(25, 25, true)
      const largeConfig = QRCodeService.optimizeQRConfigForSize(100, 70, true)
      
      expect(smallConfig.size).toBeLessThan(largeConfig.size!)
      expect(smallConfig.textSize).toBeLessThanOrEqual(largeConfig.textSize!)
    })
  })

  describe('Label Service', () => {
    const mockLabels: GateLabelData[] = [
      {
        gateId: 'gate-1',
        gateName: 'Test Gate 1',
        serialNumber: 'SN-001',
        location: 'Building A',
        qrContent: 'https://app.garagereg.hu/gates/gate-1'
      },
      {
        gateId: 'gate-2', 
        gateName: 'Test Gate 2',
        serialNumber: 'SN-002',
        qrContent: 'https://app.garagereg.hu/gates/gate-2'
      }
    ]

    test('validates label data correctly', () => {
      const validResult = LabelService.validateLabelData(mockLabels)
      expect(validResult.valid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      
      const invalidLabels = [{ ...mockLabels[0], gateName: '', qrContent: '' }]
      const invalidResult = LabelService.validateLabelData(invalidLabels)
      expect(invalidResult.valid).toBe(false)
      expect(invalidResult.errors.length).toBeGreaterThan(0)
    })

    test('calculates pages correctly', () => {
      expect(LabelService.getLabelsPerPage('A4_GRID_25x25')).toBe(77) // 7x11
      expect(LabelService.getLabelsPerPage('A4_GRID_38x19')).toBe(70) // 5x14
      expect(LabelService.getLabelsPerPage('SINGLE_A6')).toBe(1)
      
      expect(LabelService.calculatePages(150, 'A4_GRID_25x25')).toBe(2) // 150/77 = 2 pages
      expect(LabelService.calculatePages(5, 'SINGLE_A6')).toBe(5) // 5 pages
    })

    test('generates labels for all formats', async () => {
      const formats: LabelFormat[] = [
        'A4_GRID_25x25',
        'A4_GRID_38x19',
        'A4_GRID_50x30',
        'SINGLE_A6'
      ]

      for (const format of formats) {
        const printJob: PrintJob = {
          format,
          qrConfig: {
            size: 80,
            errorCorrectionLevel: 'M',
            margin: 1,
            includeText: true,
            textSize: 8,
            textPosition: 'below'
          },
          labels: mockLabels.slice(0, 1), // Test with one label
          copies: 1,
          includeGrid: false,
          includeMargins: false
        }

        const result = await LabelService.generateLabels(printJob)
        
        expect(result.success).toBe(true)
        expect(result.printUrl).toBeDefined()
        expect(result.totalLabels).toBe(1)
        expect(result.pagesGenerated).toBeGreaterThan(0)
      }
    })
  })

  describe('Label Formats', () => {
    test('all formats have required properties', () => {
      Object.values(LABEL_FORMATS).forEach(format => {
        expect(format.name).toBeDefined()
        expect(format.description).toBeDefined()
        expect(format.dimensions.width).toBeGreaterThan(0)
        expect(format.dimensions.height).toBeGreaterThan(0)
        expect(format.pageSize.width).toBe(210) // A4 width
        expect(format.pageSize.height).toBe(297) // A4 height
      })
    })

    test('grid formats have valid configurations', () => {
      const gridFormats = Object.values(LABEL_FORMATS).filter(f => f.grid)
      
      gridFormats.forEach(format => {
        const { grid, dimensions, pageSize } = format
        
        expect(grid!.cols).toBeGreaterThan(0)
        expect(grid!.rows).toBeGreaterThan(0)
        
        // Check if labels fit on page
        const totalWidth = grid!.marginLeft + (grid!.cols * dimensions.width) + ((grid!.cols - 1) * grid!.gapX)
        const totalHeight = grid!.marginTop + (grid!.rows * dimensions.height) + ((grid!.rows - 1) * grid!.gapY)
        
        expect(totalWidth).toBeLessThanOrEqual(pageSize.width)
        expect(totalHeight).toBeLessThanOrEqual(pageSize.height)
      })
    })
  })

  describe('Browser Compatibility', () => {
    test('generates print-friendly CSS', async () => {
      const printJob: PrintJob = {
        format: 'A4_GRID_25x25',
        qrConfig: {
          size: 80,
          errorCorrectionLevel: 'M',
          margin: 1,
          includeText: true,
          textSize: 8,
          textPosition: 'below'
        },
        labels: mockLabels,
        copies: 1,
        includeGrid: false,
        includeMargins: false
      }

      const result = await LabelService.generateLabels(printJob)
      
      if (result.success && result.printUrl) {
        const response = await fetch(result.printUrl)
        const html = await response.text()
        
        // Check for essential print CSS
        expect(html).toContain('@page')
        expect(html).toContain('size: A4')
        expect(html).toContain('margin: 0')
        expect(html).toContain('@media print')
        expect(html).toContain('-webkit-print-color-adjust: exact')
        expect(html).toContain('color-adjust: exact')
        
        // Check for page break handling
        expect(html).toContain('page-break-before: always')
        
        // Verify no JavaScript (print-friendly)
        expect(html).not.toContain('<script')
      }
    })

    test('supports Chrome/Edge print margins', async () => {
      const formats: LabelFormat[] = ['A4_GRID_25x25', 'A4_GRID_38x19']
      
      for (const format of formats) {
        const config = LABEL_FORMATS[format]
        
        // Verify zero margins for Chrome/Edge compatibility
        expect(config.printMargins.top).toBe(0)
        expect(config.printMargins.right).toBe(0)
        expect(config.printMargins.bottom).toBe(0)
        expect(config.printMargins.left).toBe(0)
      }
    })
  })

  describe('Performance', () => {
    test('handles large label batches', async () => {
      // Create large label batch
      const largeLabelSet: GateLabelData[] = Array.from({ length: 200 }, (_, i) => ({
        gateId: `gate-${i}`,
        gateName: `Gate ${i}`,
        serialNumber: `SN-${i.toString().padStart(3, '0')}`,
        qrContent: `https://app.garagereg.hu/gates/gate-${i}`
      }))

      const printJob: PrintJob = {
        format: 'A4_GRID_25x25',
        qrConfig: {
          size: 60, // Smaller for performance
          errorCorrectionLevel: 'L', // Lower correction for performance
          margin: 0,
          includeText: true,
          textSize: 6,
          textPosition: 'below'
        },
        labels: largeLabelSet,
        copies: 1,
        includeGrid: false,
        includeMargins: false
      }

      const startTime = performance.now()
      const result = await LabelService.generateLabels(printJob)
      const endTime = performance.now()
      
      expect(result.success).toBe(true)
      expect(result.totalLabels).toBe(200)
      expect(endTime - startTime).toBeLessThan(5000) // Should complete in under 5 seconds
    }, 10000) // 10 second timeout
  })
})

/**
 * Manual Testing Checklist for Chrome/Edge Print:
 * 
 * 1. Open /labels in browser
 * 2. Add test labels
 * 3. Select different formats
 * 4. Generate preview
 * 5. Click "Nyomtatás" button
 * 6. In print dialog:
 *    - Set margins to "Minimum" or "None"
 *    - Verify "More settings" > "Options" > "Background graphics" is checked
 *    - Check paper size is A4
 * 7. Print preview should show:
 *    - QR codes clearly visible
 *    - Text properly positioned
 *    - Labels aligned to grid
 *    - No content cut off at margins
 * 
 * Expected Results:
 * ✅ 25×25mm labels: 7×11 grid = 77 labels per A4 page
 * ✅ 38×19mm labels: 5×14 grid = 70 labels per A4 page  
 * ✅ 50×30mm labels: 4×9 grid = 36 labels per A4 page
 * ✅ 70×42mm labels: 3×6 grid = 18 labels per A4 page
 * ✅ QR codes scannable at print size
 * ✅ Text readable and properly sized
 * ✅ No overlapping or misaligned elements
 * ✅ Clean page breaks between multi-page jobs
 */