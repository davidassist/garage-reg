import { Metadata } from 'next'
import { LabelGeneratorPage } from '@/components/labels/LabelGeneratorPage'

export const metadata: Metadata = {
  title: 'Címke generálás | GarageReg',
  description: 'QR kódos címkék készítése és nyomtatása kapukhoz - A4 nyomtatóbarát formátumban',
}

export default function LabelsPage() {
  return <LabelGeneratorPage />
}