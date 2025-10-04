'use client'

import React from 'react'
import { MaintenanceCalendar } from '@/components/maintenance/MaintenanceCalendar'

export default function CalendarPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <MaintenanceCalendar />
    </div>
  )
}