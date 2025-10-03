'use client'

import React, { useState } from 'react'
import { 
  CheckCircle, 
  AlertTriangle, 
  X, 
  Download, 
  Share2, 
  Printer,
  Clock,
  User,
  MapPin,
  Calendar,
  FileText,
  Camera,
  MessageSquare,
  Star,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { 
  InspectionInstance, 
  InspectionTemplate, 
  STATUS_CONFIGS,
  PRIORITY_CONFIGS,
  INSPECTION_CATEGORIES 
} from '@/lib/types/inspection'

interface InspectionSummaryProps {
  inspection: InspectionInstance
  template: InspectionTemplate
  onClose: () => void
  onEdit?: () => void
  onSubmit?: () => void
  onPrint?: () => void
  onExport?: () => void
  className?: string
}

export function InspectionSummary({
  inspection,
  template,
  onClose,
  onEdit,
  onSubmit,
  onPrint,
  onExport,
  className = ''
}: InspectionSummaryProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'comments'>('overview')

  // Calculate statistics
  const totalFields = template.fields.length
  const completedFields = inspection.completedFields.length
  const completionRate = totalFields > 0 ? (completedFields / totalFields) * 100 : 0
  
  const fieldsByType = template.fields.reduce((acc, field) => {
    acc[field.type] = (acc[field.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const statusConfig = STATUS_CONFIGS[inspection.status]
  const priorityConfig = PRIORITY_CONFIGS[inspection.priority]
  const categoryConfig = INSPECTION_CATEGORIES[template.category]

  // Calculate inspection duration
  const duration = inspection.startedAt && inspection.completedAt 
    ? Math.round((inspection.completedAt.getTime() - inspection.startedAt.getTime()) / (1000 * 60))
    : null

  const getResultColor = () => {
    switch (inspection.overallResult) {
      case 'pass': return 'text-green-600 bg-green-50 border-green-200'
      case 'fail': return 'text-red-600 bg-red-50 border-red-200'
      case 'partial': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getResultIcon = () => {
    switch (inspection.overallResult) {
      case 'pass': return <CheckCircle className="w-5 h-5" />
      case 'fail': return <X className="w-5 h-5" />
      case 'partial': return <AlertTriangle className="w-5 h-5" />
      default: return <Clock className="w-5 h-5" />
    }
  }

  const getResultText = () => {
    switch (inspection.overallResult) {
      case 'pass': return 'Megfelelő'
      case 'fail': return 'Nem megfelelő'
      case 'partial': return 'Részben megfelelő'
      default: return 'Függőben'
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between p-6 border-b">
        <div className="flex items-start space-x-4">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-xl bg-${categoryConfig.color}-100`}>
            {categoryConfig.icon}
          </div>
          
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{inspection.title}</h2>
            <p className="text-sm text-gray-600 mt-1">{template.name}</p>
            
            <div className="flex items-center space-x-4 mt-2">
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                statusConfig.color === 'gray' ? 'bg-gray-100 text-gray-700' :
                statusConfig.color === 'blue' ? 'bg-blue-100 text-blue-700' :
                statusConfig.color === 'green' ? 'bg-green-100 text-green-700' :
                statusConfig.color === 'red' ? 'bg-red-100 text-red-700' :
                'bg-indigo-100 text-indigo-700'
              }`}>
                <span>{statusConfig.icon}</span>
                <span>{statusConfig.label}</span>
              </div>
              
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                priorityConfig.color === 'green' ? 'bg-green-100 text-green-700' :
                priorityConfig.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                priorityConfig.color === 'orange' ? 'bg-orange-100 text-orange-700' :
                'bg-red-100 text-red-700'
              }`}>
                <span>{priorityConfig.icon}</span>
                <span>{priorityConfig.label}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onPrint}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Nyomtatás"
          >
            <Printer className="w-5 h-5" />
          </button>
          
          <button
            onClick={onExport}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Exportálás"
          >
            <Download className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => {/* Share logic */}}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Megosztás"
          >
            <Share2 className="w-5 h-5" />
          </button>
          
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Bezárás"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Overall Result */}
      {inspection.overallResult && (
        <div className={`p-4 border-b border-l-4 ${getResultColor()}`}>
          <div className="flex items-center space-x-3">
            {getResultIcon()}
            <div>
              <h3 className="font-semibold">Összesített Eredmény: {getResultText()}</h3>
              {inspection.score !== undefined && (
                <p className="text-sm mt-1">Pontszám: {inspection.score}%</p>
              )}
            </div>
          </div>
          
          {(inspection.criticalIssues > 0 || inspection.minorIssues > 0) && (
            <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span>Kritikus problémák: {inspection.criticalIssues}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Minus className="w-4 h-4 text-yellow-500" />
                <span>Kisebb problémák: {inspection.minorIssues}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex space-x-6 px-6">
          {[
            { key: 'overview', label: 'Áttekintés', icon: <FileText className="w-4 h-4" /> },
            { key: 'details', label: 'Részletek', icon: <MessageSquare className="w-4 h-4" /> },
            { key: 'comments', label: `Megjegyzések (${inspection.comments.length})`, icon: <MessageSquare className="w-4 h-4" /> }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center space-x-2 py-3 border-b-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab
            inspection={inspection}
            template={template}
            completionRate={completionRate}
            duration={duration}
            fieldsByType={fieldsByType}
          />
        )}
        
        {activeTab === 'details' && (
          <DetailsTab
            inspection={inspection}
            template={template}
          />
        )}
        
        {activeTab === 'comments' && (
          <CommentsTab
            comments={inspection.comments}
          />
        )}
      </div>

      {/* Actions Footer */}
      <div className="px-6 py-4 border-t bg-gray-50 flex items-center justify-between">
        <div className="text-sm text-gray-500">
          {inspection.lastSavedAt && (
            <span>Utoljára mentve: {inspection.lastSavedAt.toLocaleString('hu-HU')}</span>
          )}
        </div>
        
        <div className="flex items-center space-x-3">
          {onEdit && inspection.status !== 'approved' && (
            <button
              onClick={onEdit}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 
                       border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
            >
              Szerkesztés
            </button>
          )}
          
          {onSubmit && inspection.status === 'completed' && (
            <button
              onClick={onSubmit}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 
                       rounded-md hover:bg-indigo-700 transition-colors"
            >
              Elküldés Jóváhagyásra
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

// Overview Tab Component
interface OverviewTabProps {
  inspection: InspectionInstance
  template: InspectionTemplate
  completionRate: number
  duration: number | null
  fieldsByType: Record<string, number>
}

function OverviewTab({
  inspection,
  template,
  completionRate,
  duration,
  fieldsByType
}: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Kitöltöttség</span>
          </div>
          <div className="text-2xl font-bold text-blue-900">{Math.round(completionRate)}%</div>
          <div className="text-xs text-blue-700">
            {inspection.completedFields.length} / {template.fields.length} mező
          </div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Időtartam</span>
          </div>
          <div className="text-2xl font-bold text-green-900">
            {duration ? `${duration}p` : 'N/A'}
          </div>
          <div className="text-xs text-green-700">
            Becsült: {template.estimatedDuration}p
          </div>
        </div>
        
        {inspection.score !== undefined && (
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Star className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">Pontszám</span>
            </div>
            <div className="text-2xl font-bold text-purple-900">{inspection.score}%</div>
            <div className="text-xs text-purple-700">
              {inspection.score >= 85 ? 'Kiváló' : 
               inspection.score >= 70 ? 'Jó' : 
               inspection.score >= 50 ? 'Megfelelő' : 'Fejlesztendő'}
            </div>
          </div>
        )}
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span className="text-sm font-medium text-orange-900">Problémák</span>
          </div>
          <div className="text-2xl font-bold text-orange-900">
            {inspection.criticalIssues + inspection.minorIssues}
          </div>
          <div className="text-xs text-orange-700">
            {inspection.criticalIssues} kritikus, {inspection.minorIssues} kisebb
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Alapadatok</h3>
          
          <div className="space-y-3">
            {inspection.assignedTo && (
              <div className="flex items-center space-x-2 text-sm">
                <User className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Felelős:</span>
                <span className="font-medium">{inspection.assignedTo}</span>
              </div>
            )}
            
            {inspection.gateId && (
              <div className="flex items-center space-x-2 text-sm">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Kapu:</span>
                <span className="font-medium">{inspection.gateId}</span>
              </div>
            )}
            
            <div className="flex items-center space-x-2 text-sm">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Létrehozva:</span>
              <span className="font-medium">{inspection.createdAt.toLocaleDateString('hu-HU')}</span>
            </div>
            
            {inspection.dueDate && (
              <div className="flex items-center space-x-2 text-sm">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Határidő:</span>
                <span className={`font-medium ${
                  inspection.dueDate < new Date() ? 'text-red-600' : 'text-gray-900'
                }`}>
                  {inspection.dueDate.toLocaleDateString('hu-HU')}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Mező Típusok</h3>
          
          <div className="space-y-2">
            {Object.entries(fieldsByType).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between text-sm">
                <span className="text-gray-600 capitalize">{type}:</span>
                <span className="font-medium">{count} db</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Timeline */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Idősor</h3>
        
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span className="text-sm text-gray-600">
              Létrehozva: {inspection.createdAt.toLocaleString('hu-HU')}
            </span>
          </div>
          
          {inspection.startedAt && (
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Elkezdve: {inspection.startedAt.toLocaleString('hu-HU')}
              </span>
            </div>
          )}
          
          {inspection.completedAt && (
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Befejezve: {inspection.completedAt.toLocaleString('hu-HU')}
              </span>
            </div>
          )}
          
          {inspection.submittedAt && (
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Elküldve: {inspection.submittedAt.toLocaleString('hu-HU')}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Details Tab Component
interface DetailsTabProps {
  inspection: InspectionInstance
  template: InspectionTemplate
}

function DetailsTab({ inspection, template }: DetailsTabProps) {
  return (
    <div className="space-y-6">
      <h3 className="font-semibold text-gray-900">Mező Értékek</h3>
      
      <div className="space-y-4">
        {template.fields.map(field => {
          const fieldValue = inspection.fieldValues.find(fv => fv.fieldId === field.id)
          const isCompleted = inspection.completedFields.includes(field.id)
          
          return (
            <div
              key={field.id}
              className={`p-4 border rounded-lg ${
                isCompleted ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{field.label}</h4>
                  {field.description && (
                    <p className="text-sm text-gray-600 mt-1">{field.description}</p>
                  )}
                  
                  <div className="mt-2">
                    {fieldValue ? (
                      <div className="text-sm">
                        <span className="font-medium">Érték:</span>{' '}
                        {typeof fieldValue.value === 'boolean' 
                          ? (fieldValue.value ? 'Igen' : 'Nem')
                          : Array.isArray(fieldValue.value) 
                          ? fieldValue.value.join(', ')
                          : fieldValue.value?.toString() || 'Üres'}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500 italic">Nem kitöltve</span>
                    )}
                  </div>
                  
                  {fieldValue?.notes && (
                    <div className="mt-2 text-sm">
                      <span className="font-medium">Megjegyzés:</span> {fieldValue.notes}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    isCompleted
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {field.type}
                  </span>
                  
                  {isCompleted && (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Comments Tab Component
interface CommentsTabProps {
  comments: any[]
}

function CommentsTab({ comments }: CommentsTabProps) {
  if (comments.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">Nincsenek megjegyzések</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {comments.map(comment => (
        <div key={comment.id} className="border rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-gray-600" />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <span className="font-medium text-gray-900">{comment.userName}</span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  comment.type === 'issue' ? 'bg-red-100 text-red-800' :
                  comment.type === 'approval' ? 'bg-green-100 text-green-800' :
                  comment.type === 'rejection' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {comment.type}
                </span>
                <span className="text-xs text-gray-500">
                  {comment.timestamp.toLocaleString('hu-HU')}
                </span>
              </div>
              
              <p className="text-sm text-gray-700">{comment.message}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}